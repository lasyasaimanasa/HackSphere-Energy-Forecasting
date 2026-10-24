
import pandas as pd

from predict import predict
from forecast_controller import apply_transition_rules

INPUT_FILE = "sample_test_input.csv"
OUTPUT_FILE = "forecast_results.csv"


def main():
    # Load the available telemetry data.
    data = pd.read_csv(INPUT_FILE)

    required_columns = [
        "timestamp",
        "ambient_temp_c",
        "humidity_pct",
        "solar_irradiance_wm2",
    ]

    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        raise ValueError(f"Missing input columns: {missing}")

    # Parse and sort timestamps before selecting a forecast window.
    data["timestamp"] = pd.to_datetime(data["timestamp"], errors="coerce")
    data = data.dropna(subset=["timestamp"]).sort_values("timestamp")
    data = data.drop_duplicates(subset=["timestamp"])

    if len(data) < 24:
        raise ValueError("At least 24 unique timestamp rows are required.")

    # Select 24 consecutive hourly rows.
    window = None

    for start in range(len(data) - 23):
        candidate = data.iloc[start:start + 24]

        differences = candidate["timestamp"].diff().dropna()
        if (differences == pd.Timedelta(hours=1)).all():
            window = candidate.copy()
            break

    if window is None:
        raise ValueError(
            "No 24-row window with consecutive hourly timestamps was found."
        )

    # Generate demand predictions for the 24-hour window.
    features = window[required_columns].copy()
    predictions = predict(features)

    if len(predictions) != 24:
        raise ValueError(
            f"Expected 24 predictions, received {len(predictions)}."
        )

    # Apply the smart-grid transition rules.
    forecast = pd.DataFrame({
        "timestamp": window["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S"),
        "predicted_demand_kw": predictions,
    })

    results = apply_transition_rules(forecast)

    # Preserve the weather inputs for inspection.
    results = results.merge(
        window[required_columns].assign(
            timestamp=window["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
        ),
        on="timestamp",
        how="left",
    )

    results.to_csv(OUTPUT_FILE, index=False)

    print("24-hour forecast workflow completed.")
    print("Rows generated:", len(results))
    print("Output file:", OUTPUT_FILE)
    print(results.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
