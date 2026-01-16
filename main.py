from src.data_loader import load_ger40_m1
from src.schoolrun_logic import generate_daily_setup
from src.backtesting_engine import backtest_schoolrun
from src.stats import compute_stats

def main():
    df = load_ger40_m1("data/GER40_M1.csv")

    # Kontrollausgabe
    print(type(df.index))
    print(df.index[:5])

    setups = generate_daily_setup(
        df,
        open_hour=9,
        open_minute=0,
        setup_bar_offset=5  # setup_bar_offset=4 = 5. Bar nach 09:00 
    )
    
    print("Setups (erste 10):")
    print(setups.head(10))

    trades, equity = backtest_schoolrun(
        df, setups,
        initial_balance=10000.0,
        risk_pct=2.0,
        tick_value=1.0,
        tick_size=1.0
    )
    print("Trades (erste 10):")
    print(trades.head(10))

    stats = compute_stats(trades)
    print("Stats:\n", stats)
    print("Equity last:", equity['balance'].iloc[-1] if not equity.empty else "n/a")

if __name__ == "__main__":
    main()
