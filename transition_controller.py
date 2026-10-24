
from datetime import datetime


def determine_grid_state(timestamp, predicted_demand_kw):
    """
    Determine grid mode and overload status for one forecast hour.

    Rules:
    - Demand > 160 kW OR hour between 18 and 22 inclusive:
      Renewable Storage Mode.
    - Otherwise: Main Grid Mode.
    - Demand >= 200 kW: Critical Overload Alert.
    """

    if predicted_demand_kw is None or predicted_demand_kw < 0:
        raise ValueError("Predicted demand must be a non-negative number.")

    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp)

    hour = timestamp.hour

    if predicted_demand_kw > 160 or 18 <= hour <= 22:
        grid_mode = "Renewable Storage Mode"
    else:
        grid_mode = "Main Grid Mode"

    overload_alert = predicted_demand_kw >= 200

    return {
        "timestamp": timestamp.isoformat(sep=" "),
        "predicted_demand_kw": float(predicted_demand_kw),
        "grid_mode": grid_mode,
        "overload_alert": overload_alert,
        "alert_message": (
            "CRITICAL OVERLOAD ALERT"
            if overload_alert
            else "Normal"
        ),
    }
