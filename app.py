
from flask import Flask, render_template, request, redirect, url_for, flash
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import os

from predict import predict
from forecast_controller import apply_transition_rules

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

if not app.secret_key:
    raise RuntimeError(
        "FLASK_SECRET_KEY is missing. Set it in your .env file."
    )

BASE_DIR = Path(__file__).resolve().parent
FORECAST_FILE = BASE_DIR / "forecast_results.csv"

REQUIRED_COLUMNS = [
    "timestamp",
    "ambient_temp_c",
    "humidity_pct",
    "solar_irradiance_wm2",
]


@app.route("/", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        uploaded_file = request.files.get("telemetry_file")

        if not uploaded_file or not uploaded_file.filename:
            flash("Please select a CSV file.")
            return redirect(url_for("dashboard"))

        if not uploaded_file.filename.lower().endswith(".csv"):
            flash("Only CSV files are allowed.")
            return redirect(url_for("dashboard"))

        try:
            df = pd.read_csv(uploaded_file)

            missing_columns = [
                column for column in REQUIRED_COLUMNS
                if column not in df.columns
            ]

            if missing_columns:
                flash(
                    "Missing required columns: "
                    + ", ".join(missing_columns)
                )
                return redirect(url_for("dashboard"))

            if df.empty:
                flash("The uploaded CSV contains no data rows.")
                return redirect(url_for("dashboard"))

            if len(df) > 5000:
                flash("Please upload a CSV with at most 5000 rows.")
                return redirect(url_for("dashboard"))

            df = df[REQUIRED_COLUMNS].copy()

            df["timestamp"] = pd.to_datetime(
                df["timestamp"], errors="coerce"
            )

            numeric_columns = [
                "ambient_temp_c",
                "humidity_pct",
                "solar_irradiance_wm2",
            ]

            for column in numeric_columns:
                df[column] = pd.to_numeric(
                    df[column], errors="coerce"
                )

            if df.isnull().any().any():
                flash(
                    "The CSV contains missing or invalid values. "
                    "Please correct them and upload again."
                )
                return redirect(url_for("dashboard"))

            if not df["timestamp"].is_monotonic_increasing:
                df = df.sort_values("timestamp").reset_index(drop=True)

            if df["timestamp"].duplicated().any():
                flash("Please remove duplicate timestamps.")
                return redirect(url_for("dashboard"))

            # Generate predictions using the existing prediction module.
            predictions = predict(df[REQUIRED_COLUMNS])

            if len(predictions) != len(df):
                raise ValueError(
                    "The prediction count does not match the CSV row count."
                )

            if not all(pd.notna(value) for value in predictions):
                raise ValueError("Predictions contain invalid values.")

            df["predicted_demand_kw"] = predictions

            # Apply the project's required grid-switching rules.
            results = apply_transition_rules(df)

            for column in numeric_columns:
                results[column] = df[column].to_numpy()

            results.to_csv(FORECAST_FILE, index=False)

            flash(
                f"Forecast generated successfully for {len(results)} rows."
            )
            return redirect(url_for("dashboard"))

        except Exception as error:
            app.logger.exception("Telemetry processing failed")
            flash(f"Could not process the CSV: {error}")
            return redirect(url_for("dashboard"))

    if not FORECAST_FILE.exists():
        records = []
    else:
        df = pd.read_csv(FORECAST_FILE)
        records = df.to_dict(orient="records")

    critical_count = sum(
        str(row.get("overload_alert", "")).lower()
        in ("true", "1", "yes")
        for row in records
    )

    renewable_count = sum(
        row.get("grid_mode") == "Renewable Storage Mode"
        for row in records
    )

    latest = records[-1] if records else {}

    battery_soc = (
        float(latest.get("battery_soc_pct", 0))
        if latest
        else 0
    )

    return render_template(
        "dashboard.html",
        records=records,
        critical_count=critical_count,
        renewable_count=renewable_count,
        latest=latest,
        battery_soc=battery_soc,
    )


if __name__ == "__main__":
    app.run(debug=True)
