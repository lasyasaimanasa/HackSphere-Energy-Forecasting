
import pandas as pd
from predict import local_predict

test_df = pd.read_csv("sample_test_input.csv").head(10)

try:
    predictions = local_predict(test_df)

    print("\nLocal fallback test successful!")
    print("Input rows:", len(test_df))
    print("Predictions:", len(predictions))
    print("First 3 estimates:", predictions[:3])

except Exception as error:
    print("\nLocal fallback test failed.")
    print(type(error).__name__ + ":", error)
