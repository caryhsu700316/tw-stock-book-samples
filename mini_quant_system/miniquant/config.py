from pathlib import Path
import os

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"

SQL_SERVER = os.getenv("MINIQUANT_SQL_SERVER", r"localhost\SQLEXPRESS")
SQL_DATABASE = os.getenv("MINIQUANT_SQL_DATABASE", "MiniQuantDemo")
SQL_DRIVER = os.getenv("MINIQUANT_SQL_DRIVER", "")

INITIAL_CASH = 1_000_000
MAX_POSITION_PCT = 0.25
STOP_LOSS_PCT = 0.12
REBALANCE_DAYS = 5
BUY_SCORE_MIN = 6.8
SELL_SCORE_MIN = 4.8

SYMBOLS = {
    "2330": "台積電",
    "2454": "聯發科",
    "2317": "鴻海",
    "2382": "廣達",
    "2881": "富邦金",
}

FACTOR_WEIGHTS = {
    "trend": 0.25,
    "rsi": 0.20,
    "momentum": 0.20,
    "volume": 0.15,
    "regime": 0.20,
}
