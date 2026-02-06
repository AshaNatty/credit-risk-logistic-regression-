# Credit Risk Prediction using Logistic Regression

This project demonstrates an end-to-end **Logistic Regression** pipeline to predict **credit card default risk** using a real-world banking dataset.  
The focus is on **data cleaning, feature selection, model interpretability, and business relevance**, rather than just model accuracy.

---

## Problem Statement

Financial institutions need to assess the risk of a customer defaulting on a loan or credit card payment.

**Objective:**  
Predict whether a customer will **default on their next payment** using historical financial and demographic data.

**Type of problem:**  
Binary Classification  
- `1` → Default  
- `0` → No Default

---

## 📊 Dataset

- **Source:** UCI Machine Learning Repository  
- **Dataset Name:** Default of Credit Card Clients Dataset  
- **Records:** 30,000 customers  
- **Domain:** Banking / Credit Risk Analytics  

> Note: The dataset file is not committed to the repository.  
> Please download it manually from the UCI repository and place it in the `data/` directory.

---

## Features Used

The following features were selected based on **industry relevance and interpretability**:

| Feature Name | Description |
|-------------|------------|
| `LIMIT_BAL` | Credit limit assigned to the customer |
| `AGE` | Customer age |
| `PAY_0` | Repayment status of the most recent month |
| `BILL_AMT1` | Last bill amount |
| `PAY_AMT1` | Last payment amount |

**Target Variable**
- `default` → Whether the customer defaults next month

---

## Data Preprocessing

Real-world datasets are rarely clean. This project includes:
- Fixing incorrect Excel headers
- Renaming columns for clarity
- Converting string values to numeric
- Handling missing values
- Explicit feature and target separation

These steps ensure the dataset is **model-ready and reproducible**.

---

## Model Used

### Logistic Regression

Logistic Regression is chosen because:
- It outputs **probabilities**, not just predictions
- Coefficients are **interpretable**
- Widely used in **regulated domains** like banking and finance

The model estimates the probability of default and applies a decision threshold for classification.

---

## Visualizations

The project includes data visualizations to:
- Understand feature impact on default risk
- Explore relationships between variables
- Communicate insights clearly to non-technical stakeholders

Examples:
- Credit limit vs default
- Age distribution by default status
- Probability curves for selected features

---

## Model Evaluation

The model is evaluated using:
- Accuracy
- Confusion Matrix
- Probability predictions (`predict_proba`)

This aligns with **business-driven evaluation**, where risk probabilities matter more than raw accuracy.

---

## 📁 Project Structure

