import argparse
from portfolio_data import dal, metrics

def _conn_str_check(conn_str: str | None) -> str:
    if not conn_str:
        raise ValueError("Provide conn_str")
    return conn_str

def cmd_get_holdings(args: argparse.Namespace) -> None:
    conn_str = _conn_str_check(args.conn_str)
    if args.cashless:
        df = dal.get_holdings_dat_cashless(conn_str, args.account_id)
    else:
        df = dal.get_holdings_dat(conn_str, args.account_id)
    print(df.to_string(index=False))