
class BatteryController:
    """Simple simulated battery state-of-charge controller."""

    def __init__(self, initial_soc=80.0, capacity_kwh=100.0):
        if not 0 <= initial_soc <= 100:
            raise ValueError("Initial state-of-charge must be 0-100%.")

        if capacity_kwh <= 0:
            raise ValueError("Battery capacity must be positive.")

        self.soc = float(initial_soc)
        self.capacity_kwh = float(capacity_kwh)

    def update(self, demand_kw, duration_hours=1.0):
        if demand_kw < 0:
            raise ValueError("Demand cannot be negative.")

        if duration_hours <= 0:
            raise ValueError("Duration must be positive.")

        if demand_kw > 160:
            # Discharge when demand is high.
            self.soc -= 2.0 * duration_hours
        else:
            # Simulate charging when demand is lower.
            self.soc += 3.0 * duration_hours

        # Keep battery charge within 0%-100%.
        self.soc = max(0.0, min(100.0, self.soc))

        return round(self.soc, 2)
