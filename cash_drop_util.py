import pandas as pd

def _cash_drop(input_data) -> pd.DataFrame:
     if isinstance(input_data, pd.DataFrame):
          output_data = input_data.drop(columns=["CASH-USD"], errors="ignore")
     elif isinstance(input_data, pd.Series):
           output_data = input_data.drop(index=["CASH-USD"], errors="ignore")
     return output_data
