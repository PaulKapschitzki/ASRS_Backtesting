def calc_position_size(balance: float,
                      risk_pct: float,
                      entry: float,
                      stop: float,
                      tick_value: float,
                      tick_size: float) -> float:
    """Berechnet Kontraktgröße, sodass max. risk_pct% des Kontos bei SL verloren gehen."""
    risk_money = balance * (risk_pct / 100.0)
    sl_dist = abs(entry - stop)
    if sl_dist <= 0:
        return 0.0
    sl_ticks = sl_dist / tick_size
    loss_per_unit = sl_ticks * tick_value   # Geldverlust pro 1 Kontrakt
    if loss_per_unit <= 0:
        return 0.0
    size = risk_money / loss_per_unit
    return size
