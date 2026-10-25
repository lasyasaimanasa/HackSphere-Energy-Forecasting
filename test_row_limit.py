
import pandas as pd

rows = 5001

df = pd.DataFrame({
    "timestamp": pd.date_range(
        start="2026-01-01 00:00:00",
        periods=rows,
        freq="h"
    ),
    "ambient_temp_c": [30] * rows,
    "humidity_pct": [55] * rows,
    "solar_irradiance_wm2": [200] * rows,
})

df.to_csv("test_row_limit.csv", index=False)

print(f"Created test_row_limit.csv with {len(df)} rows.")
