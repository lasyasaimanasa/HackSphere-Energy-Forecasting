
import pandas as pd
from transition_controller import determine_grid_state


def apply_transition_rules(forecast_df):
    required_columns = ["timestamp", "predicted_demand_kw"]

    missing = [
        col for col in required_columns
        if col not in forecast_df.columns
    ]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    results = []

    for _, row in forecast_df.iterrows():
        state = determine_grid_state(
            row["timestamp"],
            float(row["predicted_demand_kw"]),
        )
        results.append(state)

    return pd.DataFrame(results)


if __name__ == "__main__":
    sample_forecast = pd.DataFrame([
        {
            "timestamp": "2026-10-25 10:00:00",
            "predicted_demand_kw": 150,
        },
        {
            "timestamp": "2026-10-25 19:00:00",
            "predicted_demand_kw": 170,
        },
        {
            "timestamp": "2026-10-25 21:00:00",
            "predicted_demand_kw": 210,
        },
    ])

    result = apply_transition_rules(sample_forecast)
    print(result.to_string(index=False))
