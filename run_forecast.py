
import pandas as pd

from predict import predict
from forecast_controller import apply_transition_rules

INPUT_FILE = "sample_test_input.csv"
OUTPUT_FILE = "forecast_results.csv"


def main():
    # Load telemetry data.
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

    # Validate and sort timestamps.
    data["timestamp"] = pd.to_datetime(
        data["timestamp"], errors="coerce"
    )
    data = data.dropna(subset=["timestamp"])
    data = data.sort_values("timestamp")
    data = data.drop_duplicates(subset=["timestamp"])

    if len(data) < 24:
        raise ValueError(
            "At least 24 unique timestamp rows are required."
        )

    # Find 24 consecutive hourly records.
    window = None

    for start in range(len(data) - 23):
        candidate = data.iloc[start:start + 24]
        differences = candidate["timestamp"].diff().dropna()

        if (differences == pd.Timedelta(hours=1)).all():
            window = candidate.copy()
            break

    if window is None:
        raise ValueError(
            "No 24-row window with consecutive hourly timestamps "
            "was found."
        )

    # Generate demand predictions.
    features = window[required_columns].copy()
    predictions = predict(features)

    if len(predictions) != len(window):
        raise ValueError(
            f"Expected {len(window)} predictions, "
            f"received {len(predictions)}."
        )

    predictions = pd.Series(predictions).to_numpy()

    if not pd.Series(predictions).notna().all():
        raise ValueError("Predictions contain missing values.")

    if not pd.Series(predictions).map(
        lambda value: pd.notna(value) and value != float("inf")
        and value != float("-inf")
    ).all():
        raise ValueError("Predictions contain non-finite values.")

    # Prepare forecast input for the grid and battery controllers.
    forecast = pd.DataFrame({
        "timestamp": window["timestamp"].dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        ).to_numpy(),
        "predicted_demand_kw": predictions,
    })

    results = apply_transition_rules(forecast)

    # Ensure the battery simulation was included.
    if "battery_soc_pct" not in results.columns:
        raise ValueError(
            "Battery SoC is missing. Check forecast_controller.py."
        )

    # Preserve the weather inputs.
    weather = window[required_columns].copy()
    weather["timestamp"] = window["timestamp"].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    results = results.merge(
        weather,
        on="timestamp",
        how="left",
        validate="one_to_one",
    )

    # Save the completed forecast.
    results.to_csv(OUTPUT_FILE, index=False)

    print("24-hour forecast workflow completed.")
    print("Rows generated:", len(results))
    print("Output file:", OUTPUT_FILE)
    print("Battery SoC included:", "battery_soc_pct" in results.columns)
    print(results.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
