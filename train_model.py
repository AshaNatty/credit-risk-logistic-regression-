import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler


def load_and_preprocess_data(file_path):
    """
    Load the credit default dataset and perform preprocessing.
    """

    # Load Excel file
    df = pd.read_excel(file_path, header=None)

    # Fix header issue (first row contains column names)
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)

    # Rename target column
    df.rename(columns={"default payment next month": "default"}, inplace=True)

    # Selected features
    features = [
        "LIMIT_BAL",
        "AGE",
        "PAY_0",
        "BILL_AMT1",
        "PAY_AMT1"
    ]

    # Convert columns to numeric
    for col in features + ["default"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with missing values
    df = df.dropna(subset=features + ["default"])

    X = df[features]
    y = df["default"]

    return X, y


def train_model(X_train, y_train):
    """
    Train Logistic Regression model.
    """
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    return m
