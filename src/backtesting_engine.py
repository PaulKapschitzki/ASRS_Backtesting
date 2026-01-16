import pandas as pd
from .position_sizing import calc_position_size

def backtest_schoolrun(df: pd.DataFrame,
                       setups: pd.DataFrame,
                       initial_balance: float = 10000.0,
                       risk_pct: float = 2.0,
                       tick_value: float = 1.0,
                       tick_size: float = 1.0):
    """
    Simpler, nicht-vektorisierter Backtest:
    - Pro Tag max. 1 Trade
    - Limit-Order bei mid
    - SL 2 Punkte hinter Bar-Low/High
    - TP = 2R
    - Kein Intraday-Trailing
    """
    balance = initial_balance
    equity_curve = []
    trades = []

    df = df.copy()

    # Sicherstellen, dass wir schnellen Zugriff auf OHLC nach setup_time haben:
    # Wir nehmen an: wenn Limit getroffen wird, dann intraday nach setup_time.

    for setup_time, row in setups.iterrows():
        day = row['trade_day']
        mid = row['mid']
        h, l = row['high'], row['low']
        direction = row['direction']

        # SL & TP
        if direction == 1:
            sl = l - 2 * tick_size
            R  = mid - sl
            if R <= 0:
                continue
            tp = mid + 2 * R
        else:
            sl = h + 2 * tick_size
            R  = sl - mid
            if R <= 0:
                continue
            tp = mid - 2 * R

        # Positionsgröße
        size = calc_position_size(balance, risk_pct, mid, sl, tick_value, tick_size)
        if size <= 0:
            continue

        # Ab hier: Simulation intraday nach setup_time
        day_df = df[df.index.date == day]
        intraday = day_df[day_df.index > setup_time]

        if intraday.empty:
            continue

        entry_filled = False
        entry_time = None

        # Limit-Fill Prüfen: für Long muss Tief <= mid, für Short muss Hoch >= mid
        for ts, bar in intraday.iterrows():
            high, low = bar['high'], bar['low']
            if direction == 1 and low <= mid <= high:
                entry_filled = True
                entry_time = ts
                break
            if direction == -1 and low <= mid <= high:
                entry_filled = True
                entry_time = ts
                break

        if not entry_filled:
            # Limit nie ausgeführt -> kein Trade
            continue

        # Trade ist offen ab entry_time
        # Nun Lauf bis SL oder TP oder Tagesende
        open_price = mid
        exit_price = None
        exit_time  = None
        result_r   = None

        after_entry = intraday[intraday.index >= entry_time]
        for ts, bar in after_entry.iterrows():
            high, low = bar['high'], bar['low']

            if direction == 1:
                # Long: zuerst SL, dann TP prüfen (konservativ)
                if low <= sl:
                    exit_price = sl
                    exit_time  = ts
                    result_r   = -1.0
                    break
                if high >= tp:
                    exit_price = tp
                    exit_time  = ts
                    result_r   = 2.0
                    break
            else:
                # Short
                if high >= sl:
                    exit_price = sl
                    exit_time  = ts
                    result_r   = -1.0
                    break
                if low <= tp:
                    exit_price = tp
                    exit_time  = ts
                    result_r   = 2.0
                    break

        if exit_price is None:
            # Weder SL noch TP getroffen -> Tagesclose
            last_bar = after_entry.iloc[-1]
            exit_price = last_bar['close']
            exit_time  = last_bar.name
            # R gewichten: Gewinn/Verlust in Preis / R
            pnl_per_unit = (exit_price - open_price) * (1 if direction == 1 else -1)
            result_r = pnl_per_unit / R

        # Geld-PnL
        pnl_money = result_r * risk_pct/100.0 * balance  # Näherung: 1R = 2% des damaligen Balance
        balance += pnl_money

        trades.append({
            'day': day,
            'entry_time': entry_time,
            'exit_time': exit_time,
            'direction': direction,
            'entry_price': open_price,
            'exit_price': exit_price,
            'R': result_r,
            'pnl_money': pnl_money,
            'balance_after': balance,
        })
        equity_curve.append({'time': exit_time, 'balance': balance})

    trades_df = pd.DataFrame(trades)
    equity_df = pd.DataFrame(equity_curve).set_index('time').sort_index()
    return trades_df, equity_df
