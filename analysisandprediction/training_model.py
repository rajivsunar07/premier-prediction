from random import seed
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import MinMaxScaler
import joblib
import pandas as pd
import numpy as np
import xgboost as xgb

def logistic_modelling(fixtures_df):
    completed_cleaned_fixtures_df = fixtures_df.drop(['event', 'finished', 'id', 'kickoff_time', 'started', 'team_a', 'team_a_score', 'team_h', 'team_h_score', 'stats'], axis=1).copy()
    train_val_df, test_df = train_test_split(completed_cleaned_fixtures_df, test_size=0.1, random_state=42)
    train_df, val_df = train_test_split(train_val_df, test_size=0.15, random_state=42)
    input_cols = train_df.columns.tolist()
    input_cols.remove('ftr')
    target_col = 'ftr'
    train_inputs = train_df[input_cols].copy()
    train_targets = train_df[target_col].copy()

    val_inputs = val_df[input_cols].copy()
    val_targets = val_df[target_col].copy()

    test_inputs = test_df[input_cols].copy()
    test_targets = test_df[target_col].copy()
    numeric_cols = train_inputs.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = train_inputs.select_dtypes('object').columns.tolist()

    ### Scaling

    scaler = MinMaxScaler()
    scaler.fit(completed_cleaned_fixtures_df[numeric_cols])
    train_inputs[numeric_cols] = scaler.transform(train_inputs[numeric_cols])
    val_inputs[numeric_cols] = scaler.transform(val_inputs[numeric_cols])
    test_inputs[numeric_cols] = scaler.transform(test_inputs[numeric_cols])

    ## modelling

    model = xgb.XGBClassifier(seed=82)

    model.fit(train_inputs[numeric_cols], train_targets)

    X_train = train_inputs[numeric_cols]
    X_val = val_inputs[numeric_cols]
    X_test = test_inputs[numeric_cols]
    train_preds = model.predict(X_train)

    model.score(X_val, val_targets)

    joblib.dump(model, './analysisandprediction/model')
