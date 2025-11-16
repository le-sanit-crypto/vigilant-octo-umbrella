import joblib

class ModelRegistry:
    def __init__(self, path='./models'):
        self.path = path

    def get_model(self, symbol):
        try:
            return joblib.load(f"{self.path}/{symbol}_best.pkl")
        except:
            return None

    def save_model(self, symbol, model):
        joblib.dump(model, f"{self.path}/{symbol}_best.pkl")