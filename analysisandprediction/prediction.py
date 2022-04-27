import joblib

def predict(predict_df):
    model = joblib.load('./analysisandprediction/model')
    prediction = model.predict(predict_df)
    return prediction