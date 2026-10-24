
import pandas as pd
from predict import predict

sample = pd.DataFrame([
    {
        "timestamp": "2015-02-24 03:00:00",
        "ambient_temp_c": 9.71,
        "humidity_pct": 88.97,
        "solar_irradiance_wm2": 0
    },
    {
        "timestamp": "2015-02-24 12:00:00",
        "ambient_temp_c": 28.0,
        "humidity_pct": 55.0,
        "solar_irradiance_wm2": 650
    },
    {
        "timestamp": "2015-02-24 18:00:00",
        "ambient_temp_c": 24.0,
        "humidity_pct": 70.0,
        "solar_irradiance_wm2": 100
    }
])

try:
    predictions = predict(sample)

    print("\nMultiple prediction test successful!")
    print("Number of input records:", len(sample))
    print("Number of predictions:", len(predictions))

    for i, value in enumerate(predictions, start=1):
        print(f"Record {i}: {value:.4f} kW")

except Exception as error:
    print("\nPrediction failed.")
    print(type(error).__name__ + ":", error)
