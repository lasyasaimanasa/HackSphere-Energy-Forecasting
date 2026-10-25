
import pandas as pd

from transition_controller import determine_grid_state
from battery_controller import BatteryController


def apply_transition_rules(forecast_df):
    """
    Apply grid-switching rules and simulate battery state-of-charge.

    Battery SoC is simulated, not measured from physical hardware.
    """
    required_columns = ["timestamp", "predicted_demand_kw"]

    for column in required_columns:
        if column not in forecast_df.columns:
            raise ValueError(f"Missing required column: {column}")

    results = []
    battery = BatteryController(initial_soc=80, capacity_kwh=100)

    forecast_df = forecast_df.copy()
    forecast_df["timestamp"] = pd.to_datetime(
        forecast_df["timestamp"], errors="raise"
    )
    forecast_df = forecast_df.sort_values("timestamp").reset_index(drop=True)

    for _, row in forecast_df.iterrows():
        state = determine_grid_state(
            row["timestamp"].to_pydatetime(),
            float(row["predicted_demand_kw"])
        )

        state["battery_soc_pct"] = battery.update(
            demand_kw=float(row["predicted_demand_kw"]),
            duration_hours=1.0
        )

        results.append(state)

    return pd.DataFrame(results)


if __name__ == "__main__":
    sample = pd.DataFrame({
        "timestamp": [
            "2026-10-24 10:00:00",
            "2026-10-24 11:00:00",
            "2026-10-24 19:00:00"
        ],
        "predicted_demand_kw": [150, 180, 210]
    })

    print(apply_transition_rules(sample).to_string(index=False))
