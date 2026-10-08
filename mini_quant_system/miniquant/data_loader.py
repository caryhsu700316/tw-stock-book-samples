import re
from urllib.parse import quote_plus

import numpy as np
import pandas as pd
import pyodbc
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.types import BigInteger, Float, NVARCHAR

from .config import DATA_DIR, SQL_DATABASE, SQL_DRIVER, SQL_SERVER, SYMBOLS


def _choose_driver() -> str:
    if SQL_DRIVER:
        return SQL_DRIVER
    drivers = [driver for driver in pyodbc.drivers() if "SQL Server" in driver]
    for preferred in ("ODBC Driver 18 for SQL Server", "ODBC Driver 17 for SQL Server"):
        if preferred in drivers:
            return preferred
    if drivers:
        return drivers[-1]
    raise RuntimeError("找不到 SQL Server ODBC Driver，請先安裝 ODBC Driver 17 或 18 for SQL Server。")


def _quote_database_name(database: str) -> str:
    if not re.match(r"^[\w\-]+$", database):
        raise ValueError("SQL_DATABASE 只能包含英數字、底線與連字號。")
    return f"[{database}]"


def _create_engine(database: str) -> Engine:
    connection_string = (
        f"DRIVER={{{_choose_driver()}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={database};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    return create_engine(
        f"mssql+pyodbc:///?odbc_connect={quote_plus(connection_string)}",
        fast_executemany=True,
        pool_pre_ping=True,
    )


def _ensure_database() -> None:
    master = _create_engine("master").execution_options(isolation_level="AUTOCOMMIT")
    try:
        with master.connect() as conn:
            exists = conn.execute(text("SELECT DB_ID(:database_name)"), {"database_name": SQL_DATABASE}).scalar()
            if exists is None:
                conn.execute(text(f"CREATE DATABASE {_quote_database_name(SQL_DATABASE)}"))
    except SQLAlchemyError as exc:
        raise RuntimeError(
            "無法連線到 SQL Server Express。請確認 SQL Server (SQLEXPRESS) 服務已啟動，"
            "或設定 MINIQUANT_SQL_SERVER 指向你的 instance，例如 localhost\\SQLEXPRESS。"
        ) from exc


def _database_label() -> str:
    return f"{SQL_SERVER}/{SQL_DATABASE}"


def _make_price_data(days: int = 140) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    dates = pd.bdate_range("2025-01-02", periods=days)
    rows = []

    market_noise = rng.normal(0.0008, 0.009, len(dates)).cumsum()
    taiex = 20000 * (1 + market_noise)
    for date, close in zip(dates, taiex):
        rows.append([date.date().isoformat(), "TAIEX", "加權指數", close, 0])

    base_prices = {"2330": 980, "2454": 1180, "2317": 185, "2382": 265, "2881": 82}
    drifts = {"2330": 0.0014, "2454": 0.0007, "2317": 0.0003, "2382": 0.0018, "2881": 0.0002}

    for symbol, name in SYMBOLS.items():
        noise = rng.normal(drifts[symbol], 0.018, len(dates)).cumsum()
        close_series = base_prices[symbol] * (1 + noise)
        volume_base = rng.integers(8_000, 30_000)
        for date, close in zip(dates, close_series):
            volume = int(volume_base * rng.uniform(0.6, 1.8))
            rows.append([date.date().isoformat(), symbol, name, max(close, 10), volume])

    return pd.DataFrame(rows, columns=["trade_date", "symbol", "name", "close", "volume"])


def prepare_database() -> str:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    prices = _make_price_data()

    _ensure_database()
    engine = _create_engine(SQL_DATABASE)
    prices.to_sql(
        "prices",
        engine,
        if_exists="replace",
        index=False,
        schema="dbo",
        dtype={
            "trade_date": NVARCHAR(20),
            "symbol": NVARCHAR(20),
            "name": NVARCHAR(40),
            "close": Float,
            "volume": BigInteger,
        },
    )
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                IF NOT EXISTS (
                    SELECT 1
                    FROM sys.indexes
                    WHERE name = 'idx_prices_symbol_date'
                      AND object_id = OBJECT_ID('dbo.prices')
                )
                CREATE INDEX idx_prices_symbol_date ON dbo.prices(symbol, trade_date)
                """
            )
        )

    return _database_label()


def load_prices(_database_label: str) -> pd.DataFrame:
    engine = _create_engine(SQL_DATABASE)
    return pd.read_sql_query("SELECT * FROM dbo.prices ORDER BY trade_date, symbol", engine)
