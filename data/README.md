# Dataset Information

This project uses a real-world banking dataset for **credit default prediction**.

---

## Dataset Name

**Default of Credit Card Clients Dataset**

---

## Source

UCI Machine Learning Repository  
https://archive.ics.uci.edu/ml/datasets/default+of+credit+card+clients

---

## Description

The dataset contains information on **30,000 credit card customers**, including:

- Credit limits
- Demographic data
- Payment history
- Billing amounts
- Default status

The goal is to predict whether a customer will **default on their next credit card payment**.

---

## Target Variable

- **Column name:** `default payment next month`
- **Values:**
  - `1` → Customer will default
  - `0` → Customer will not default

In the project code, this column is renamed to `default` for clarity.

---

## How to Use This Dataset

1. Download the dataset from the UCI repository
2. The file name will be:
3. Place the file inside this directory:

 **Do NOT rename the file**, as the training script expects this exact name.

---

## Notes

- The dataset is **not included** in this repository due to licensing restrictions
- Some preprocessing is required because the column headers are stored in the first row
- All necessary preprocessing steps are handled in the project code

---

## License

Please refer to the UCI Machine Learning Repository for dataset licensing and usage terms.


