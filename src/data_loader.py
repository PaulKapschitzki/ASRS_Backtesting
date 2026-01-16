# src/data_loader.py
import pandas as pd

def load_ger40_m1(path: str) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        sep=",",
        parse_dates=['Gmt time'],
        dayfirst=True,              # 04.12.2023 = 4. Dezember
        infer_datetime_format=True
    )

    # Spaltennamen vereinheitlichen
    df = df.rename(columns={
        'Gmt time': 'datetime',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    })

    # Datetime als Index setzen
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.set_index('datetime').sort_index()

    # M5 resamplen
    print("df.dtypes:\n", df.dtypes)
    print("index type:", type(df.index))
    print(df.head())
    df_m5 = df.resample('5T', label='right', closed='right').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    })

    # Leere Bars entfernen
    df_m5 = df_m5.dropna(subset=['open', 'high', 'low', 'close'])

    return df_m5
