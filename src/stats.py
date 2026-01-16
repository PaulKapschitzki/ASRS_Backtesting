import pandas as pd
import numpy as np

def compute_stats(trades: pd.DataFrame) -> dict:
    if trades.empty:
        return {}

    wins = trades[trades['pnl_money'] > 0]
    losses = trades[trades['pnl_money'] < 0]

    total = len(trades)
    winrate = len(wins) / total if total > 0 else 0.0
    avg_win = wins['pnl_money'].mean() if not wins.empty else 0.0
    avg_loss = losses['pnl_money'].mean() if not losses.empty else 0.0
    gross_profit = wins['pnl_money'].sum()
    gross_loss   = losses['pnl_money'].sum()
    profit_factor = (gross_profit / abs(gross_loss)) if gross_loss < 0 else np.nan

    # einfache MaxDD
    equity = trades['balance_after']
    cummax = equity.cummax()
    drawdown = (equity - cummax)
    max_dd = drawdown.min()

    return {
        'trades': total,
        'winrate': winrate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'profit_factor': profit_factor,
        'max_drawdown': max_dd,
    }
