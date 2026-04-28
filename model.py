import numpy as np

units = np.array([50, 100, 200, 300, 400, 500], dtype=float)
bills = np.array([150, 400, 900, 1600, 2500, 4000], dtype=float)

# Fit a simple line y = m*x + c using NumPy to keep dependencies minimal.
slope, intercept = np.polyfit(units, bills, 1)

def predict_bill_ml(units_input):
    prediction = (slope * float(units_input)) + intercept
    return round(prediction, 2)