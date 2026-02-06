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
    return model


def evaluate_model(model, X_test, y_test):
    """
    Evaluate trained model.
    """
    y_pred = model.predict(X_test)

    print("\nModel Evaluation")
    print("----------------")
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))


def main():
    # File path (update if needed)
    file_path = "data/default of credit card clients.xls"

    # Load and preprocess data
    X, y = load_and_preprocess_data(file_path)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    # Feature scaling (important for Logistic Regression)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train model
    model = train_model(X_train_scaled, y_train)

    # Evaluate model
    evaluate_model(model, X_test_scaled, y_test)

    # Display learned coefficients
    coef_df = pd.DataFrame({
        "Feature": X.columns,
        "Coefficient": model.coef_[0]
    }).sort_values(by="Coefficient")

    print("\nModel Coefficients (Interpretability):")
    print(coef_df)


if __name__ == "__main__":
    main()
