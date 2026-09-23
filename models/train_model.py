"""
=============================================================================
Supermarket Sales Analysis - Machine Learning Model Training
=============================================================================
This script trains a supervised Machine Learning model to PREDICT
the total Sales revenue of a supermarket transaction.

WHAT IS MACHINE LEARNING?
--------------------------
Machine Learning teaches a computer to make predictions based on patterns
it has learned from historical data — just like how a human learns from
past experience.

In our project:
  ✅ Input features: Branch, Category, Customer Type, Quantity, Unit Price
  🎯 Target to predict: Sales ($) = Quantity × Unit Price (but the model
     learns to predict this from real transaction patterns including category
     trends and customer behavior)

ML WORKFLOW:
  1. Load and prepare the cleaned dataset
  2. Select important "feature" columns (inputs) and the "target" column (output)
  3. Encode categorical variables (text → numbers via One-Hot Encoding)
  4. Split data: 80% for training, 20% for testing
  5. Train multiple models and pick the best performer
  6. Evaluate performance using R² Score, MAE, and RMSE
  7. Save the trained model pipeline to a .pkl file for API use

MODELS TRAINED:
  - Linear Regression (Simple baseline)
  - Random Forest Regressor (Ensemble learning — very powerful!)
  - Gradient Boosting Regressor (Sequential boosting — usually best!)
"""

import os
import sys
import json

# Ensure the root project directory is in path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import pandas as pd
import numpy as np
import joblib  # For saving/loading trained model to disk

# Sklearn imports for building the ML pipeline
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from backend.data_analysis import SupermarketAnalytics


def train_and_evaluate():
    """
    Main training function that:
    1. Loads the cleaned supermarket dataset
    2. Prepares features and target variable
    3. Trains three different ML models
    4. Evaluates each model on the test set
    5. Saves the best model as a .pkl file
    6. Saves metadata (feature columns, model info) as JSON
    """

    # ---------------------------------------------------------------
    # STEP 1: Load & Clean the dataset via our existing engine
    # ---------------------------------------------------------------
    print("=" * 60)
    print("  SUPERMARKET SALES - ML MODEL TRAINING")
    print("=" * 60)

    data_file = os.path.join(root_dir, "data", "supermarket_sales.csv")
    analytics = SupermarketAnalytics(csv_path=data_file)
    df = analytics.cleaned_df.copy()

    print(f"\n✅ Dataset loaded: {len(df)} clean transaction records")

    # ---------------------------------------------------------------
    # STEP 2: Select Features (X) and Target Variable (y)
    # ---------------------------------------------------------------
    # Categorical features (text values that need encoding)
    categorical_features = ["Branch", "City", "Customer Type", "Gender", "Category", "Payment Method"]

    # Numerical features (already numeric, ready to use)
    numerical_features = ["Unit Price", "Quantity", "Rating"]

    # 🎯 Target variable: what we want the model to predict
    target = "Sales"

    # Keep only selected columns to build a clean training DataFrame
    feature_columns = categorical_features + numerical_features
    df_model = df[feature_columns + [target]].dropna()

    X = df_model[feature_columns]   # Input features (the "question")
    y = df_model[target]            # Target label  (the "answer" / ground truth)

    print(f"✅ Features selected: {feature_columns}")
    print(f"✅ Target column:     '{target}'")
    print(f"✅ Total samples for training: {len(X)}")

    # ---------------------------------------------------------------
    # STEP 3: Split Data → 80% Train, 20% Test
    # ---------------------------------------------------------------
    # We train on 80% of the data and evaluate on the remaining 20%
    # (so the model is tested on data it has NEVER seen before)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )
    print(f"\n✅ Train samples: {len(X_train)} | Test samples: {len(X_test)}")

    # ---------------------------------------------------------------
    # STEP 4: Build a Preprocessing Pipeline
    # ---------------------------------------------------------------
    # WHY PREPROCESSING?
    # - ML models only understand numbers, not text like "Branch A"
    # - OneHotEncoder converts each category into a set of 0/1 binary columns
    # - StandardScaler normalizes numeric values so large numbers don't dominate

    preprocessor = ColumnTransformer(
        transformers=[
            # Convert categorical columns to binary (0/1) numerical columns
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
            # Scale numerical columns to a similar range (mean=0, std=1)
            ("num", StandardScaler(), numerical_features)
        ]
    )

    # ---------------------------------------------------------------
    # STEP 5: Define Models to Compare
    # ---------------------------------------------------------------
    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=150,    # Build 150 decision trees
            max_depth=8,         # Limit tree depth to prevent overfitting
            random_state=42
        ),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=150,    # Build 150 sequential boosted trees
            learning_rate=0.08,  # Slower learning rate = better generalization
            max_depth=5,
            random_state=42
        )
    }

    # ---------------------------------------------------------------
    # STEP 6: Train Each Model & Evaluate Performance
    # ---------------------------------------------------------------
    results = {}
    best_model_name = None
    best_r2 = -999
    best_pipeline = None

    print("\n" + "-" * 60)
    print("  TRAINING & EVALUATING MODELS...")
    print("-" * 60)

    for model_name, model in models.items():
        # Combine preprocessing + model into a single clean pipeline
        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ])

        # FIT (train) the pipeline on training data
        pipeline.fit(X_train, y_train)

        # PREDICT on the test set (data the model has NEVER seen)
        y_pred = pipeline.predict(X_test)

        # EVALUATE performance metrics
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        # 5-Fold Cross-Validation for more robust evaluation
        cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring="r2")
        cv_mean = cv_scores.mean()

        results[model_name] = {
            "r2_score": round(float(r2), 4),
            "mae": round(float(mae), 4),
            "rmse": round(float(rmse), 4),
            "cv_r2_mean": round(float(cv_mean), 4)
        }

        print(f"\n🔹 {model_name}")
        print(f"   R² Score:         {r2:.4f}  {'✅ Excellent' if r2 > 0.95 else '✅ Good' if r2 > 0.80 else '⚠️ Moderate'}")
        print(f"   MAE  (avg error): ${mae:.2f}")
        print(f"   RMSE:             ${rmse:.2f}")
        print(f"   5-Fold CV R²:     {cv_mean:.4f}")

        # Track the best-performing model by R² score
        if r2 > best_r2:
            best_r2 = r2
            best_model_name = model_name
            best_pipeline = pipeline

    # ---------------------------------------------------------------
    # STEP 7: Save the Best Model Pipeline to Disk (.pkl)
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print(f"  🏆 BEST MODEL: {best_model_name} (R² = {best_r2:.4f})")
    print("=" * 60)

    # Create the models/ folder if it doesn't exist
    models_dir = os.path.join(root_dir, "models")
    os.makedirs(models_dir, exist_ok=True)

    model_path = os.path.join(models_dir, "sales_predictor.pkl")
    joblib.dump(best_pipeline, model_path)
    print(f"\n💾 Model saved to: {model_path}")

    # Save metadata JSON alongside the model (for API and dashboard use)
    metadata = {
        "best_model_name": best_model_name,
        "best_r2_score": round(float(best_r2), 4),
        "feature_columns": feature_columns,
        "categorical_features": categorical_features,
        "numerical_features": numerical_features,
        "target_column": target,
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "feature_options": {
            "Branch": sorted(df["Branch"].unique().tolist()),
            "City": sorted(df["City"].unique().tolist()),
            "Customer Type": sorted(df["Customer Type"].unique().tolist()),
            "Gender": sorted(df["Gender"].unique().tolist()),
            "Category": sorted(df["Category"].unique().tolist()),
            "Payment Method": sorted(df["Payment Method"].unique().tolist()),
            "Unit Price": {
                "min": round(float(df["Unit Price"].min()), 2),
                "max": round(float(df["Unit Price"].max()), 2),
                "mean": round(float(df["Unit Price"].mean()), 2)
            },
            "Quantity": {
                "min": int(df["Quantity"].min()),
                "max": int(df["Quantity"].max())
            },
            "Rating": {
                "min": round(float(df["Rating"].min()), 1),
                "max": round(float(df["Rating"].max()), 1),
                "mean": round(float(df["Rating"].mean()), 1)
            }
        },
        "all_results": results
    }

    metadata_path = os.path.join(models_dir, "model_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"📋 Metadata saved to: {metadata_path}")

    # ---------------------------------------------------------------
    # STEP 8: Quick Prediction Test to Verify the Model Works
    # ---------------------------------------------------------------
    print("\n" + "-" * 60)
    print("  🧪 SAMPLE PREDICTION TEST")
    print("-" * 60)

    sample_input = pd.DataFrame([{
        "Branch": "Branch B",
        "City": "Mandalay",
        "Customer Type": "Member",
        "Gender": "Female",
        "Category": "Fashion accessories",
        "Payment Method": "E-wallet",
        "Unit Price": 75.0,
        "Quantity": 3,
        "Rating": 8.5
    }])

    predicted_sales = best_pipeline.predict(sample_input)[0]
    actual_sales = 75.0 * 3  # True Sales = Qty × Unit Price

    print(f"  Sample Transaction:")
    print(f"    Branch: Branch B | Category: Fashion accessories")
    print(f"    Unit Price: $75.00 | Quantity: 3 | Rating: 8.5")
    print(f"    Customer: Member | Payment: E-wallet")
    print(f"\n  📊 True Sales:      ${actual_sales:.2f}")
    print(f"  🤖 ML Predicted:    ${predicted_sales:.2f}")
    print(f"  📉 Difference:      ${abs(actual_sales - predicted_sales):.2f}")

    print("\n✅ Model training completed successfully!")
    return best_pipeline, metadata


if __name__ == "__main__":
    train_and_evaluate()
