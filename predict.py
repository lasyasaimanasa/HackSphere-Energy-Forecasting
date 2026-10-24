
import os
import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

QUICKML_ENDPOINT_URL = os.getenv("QUICKML_ENDPOINT_URL")
ZOHO_ACCESS_TOKEN = os.getenv("ZOHO_ACCESS_TOKEN")
QUICKML_ENDPOINT_KEY = os.getenv("QUICKML_ENDPOINT_KEY")
CATALYST_ORG = os.getenv("CATALYST_ORG")
CATALYST_ENVIRONMENT = os.getenv(
    "CATALYST_ENVIRONMENT", "Development"
)


def local_predict(input_df: pd.DataFrame) -> np.ndarray:
    """Fallback estimate; not a prediction from the trained QuickML model."""
    hours = pd.to_datetime(
        input_df["timestamp"], errors="coerce"
    ).dt.hour

    if hours.isna().any():
        raise ValueError("Invalid timestamp found in input data.")

    base_load = 120.0 + 30.0 * np.sin(
        2 * np.pi * (hours - 6) / 24
    )

    cooling_load = np.maximum(
        0.0, input_df["ambient_temp_c"].to_numpy(dtype=float) - 24.0
    ) * 8.5

    return np.asarray(base_load + cooling_load, dtype=float)


def predict(input_df: pd.DataFrame) -> np.ndarray:
    required_columns = [
        "timestamp",
        "ambient_temp_c",
        "humidity_pct",
        "solar_irradiance_wm2",
    ]

    missing = [
        col for col in required_columns
        if col not in input_df.columns
    ]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    
    # Temporary offline mode while the QuickML allowance is exhausted.
    if os.getenv("USE_LOCAL_FALLBACK", "false").lower() == "true":
        print("Using local fallback estimates, not QuickML predictions.")
        return local_predict(input_df)
    
    # Use the local fallback when QuickML credentials are unavailable.
    if not all([
        QUICKML_ENDPOINT_URL,
        ZOHO_ACCESS_TOKEN,
        QUICKML_ENDPOINT_KEY,
        CATALYST_ORG,
    ]):
        print(
            "Using local fallback estimates, not QuickML predictions."
        )
        return local_predict(input_df)

    headers = {
        "Authorization": f"Zoho-oauthtoken {ZOHO_ACCESS_TOKEN}",
        "X-QUICKML-ENDPOINT-KEY": QUICKML_ENDPOINT_KEY,
        "CATALYST-ORG": CATALYST_ORG,
        "Environment": CATALYST_ENVIRONMENT,
        "Content-Type": "application/json",
    }

    predictions = []

    try:
        with requests.Session() as session:
            batch_size = 10

            for start in range(0, len(input_df), batch_size):
                batch = input_df.iloc[
                    start:start + batch_size
                ][required_columns]

                response = session.post(
                    QUICKML_ENDPOINT_URL,
                    headers=headers,
                    json={"data": batch.to_dict(orient="records")},
                    timeout=30,
                )

                # Do not silently replace real model predictions
                # with fallback estimates after an API error.
                response.raise_for_status()
                result = response.json().get("result")

                if (
                    not isinstance(result, list)
                    or len(result) != len(batch)
                ):
                    raise ValueError(
                        "Unexpected QuickML prediction response."
                    )

                predictions.extend(float(value) for value in result)

        return np.asarray(predictions, dtype=float)

    except requests.RequestException as error:
        raise RuntimeError(
            "QuickML API request failed. Its prediction allowance "
            "may be exhausted. Use local_predict() explicitly for "
            "fallback estimates."
        ) from error
