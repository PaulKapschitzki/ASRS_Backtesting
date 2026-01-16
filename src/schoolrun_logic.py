import pandas as pd
import numpy as np

def generate_daily_setup(df: pd.DataFrame,
                         open_hour: int = 9,
                         open_minute: int = 0,
                         setup_bar_offset: int = 5):
    """
    df: M5-Daten mit DatetimeIndex, Spalten: open, high, low, close, volume
    setup_bar_offset: 4 = 5. Bar nach Open (0 = erste Bar ab Open)
    setup_bar_offset: 5 = 6. Bar nach Open (09:25 - 09:30)
    """
    df = df.copy()

    # HART: Index sicher in DatetimeIndex konvertieren
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    df['date'] = df.index.date
    df['time'] = df.index.time
    df['weekday'] = df.index.weekday  # 0=Montag, 3=Donnerstag

    setups = []

    for day, day_df in df.groupby('date'):
        # Donnerstag auslassen
        if day_df['weekday'].iloc[0] == 3:
            continue

        # Open-Bar ~ 09:00 finden
        day_open = day_df.between_time(f'{open_hour:02d}:{open_minute:02d}',
                                       f'{open_hour:02d}:{open_minute:02d}')
        if day_open.empty:
            continue

        open_ts = day_open.index[0]

        try:
            open_loc = day_df.index.get_loc(open_ts)
        except KeyError:
            continue

        setup_idx = open_loc + setup_bar_offset
        if setup_idx >= len(day_df):
            continue

        bar = day_df.iloc[setup_idx]
        o, h, l, c = bar['open'], bar['high'], bar['low'], bar['close']
        ts = bar.name

        if not (np.isfinite(o) and np.isfinite(h) and np.isfinite(l) and np.isfinite(c)):
            continue
        if h <= l:
            continue

        mid = (h + l) / 2.0

        if c > o:
            direction = 1    # long
        elif c < o:
            direction = -1   # short
        else:
            continue         # Doji => kein Trade

        setups.append({
            'trade_day': day,
            'setup_time': ts,
            'open': o,
            'high': h,
            'low': l,
            'close': c,
            'mid': mid,
            'direction': direction,
        })

    setups_df = pd.DataFrame(setups)
    if setups_df.empty:
        return setups_df

    setups_df = setups_df.set_index('setup_time').sort_index()
    return setups_df