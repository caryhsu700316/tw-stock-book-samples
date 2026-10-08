from .config import INITIAL_CASH, MAX_POSITION_PCT, STOP_LOSS_PCT


def calc_shares(cash: float, price: float) -> int:
    budget = min(cash, INITIAL_CASH * MAX_POSITION_PCT)
    return int(budget // price)


def hit_stop_loss(price: float, avg_cost: float) -> bool:
    return price <= avg_cost * (1 - STOP_LOSS_PCT)
