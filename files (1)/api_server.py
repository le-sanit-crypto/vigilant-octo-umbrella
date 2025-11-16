from fastapi import FastAPI
import joblib
import pandas as pd

app = FastAPI()

@app.post("/predict")
def predict(payload: dict):
    df = pd.DataFrame([payload["features"]])
    model = joblib.load("./models/btcusd_best.pkl")
    signal = model.predict(df)[0]
    return {"signal": signal}