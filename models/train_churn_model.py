"""
Machine Learning & Churn Explainability Pipeline
Trains an interpretable Random Forest classifier to predict customer churn,
evaluates performance metrics (ROC-AUC, Precision, Recall), and computes feature importances.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def train_churn_pipeline(data_path="data/master_retention_data.csv", output_dir="models"):
    os.makedirs(output_dir, exist_ok=True)
    print("Loading SaaS master retention dataset...")
    df = pd.read_csv(data_path)

    # Feature definitions
    num_features = [
        "license_utilization_rate",
        "feature_adoption_score",
        "weekly_active_days",
        "api_calls_monthly",
        "last_active_days_ago",
        "total_tickets",
        "avg_resolution_time_hrs",
        "escalated_tickets_count",
        "csat_score",
        "mrr",
        "seats_purchased"
    ]
    
    cat_features = [
        "tier",
        "billing_cycle",
        "industry"
    ]

    target = "churn_label"

    X = df[num_features + cat_features]
    y = df[target]

    # Stratified Train-Test Split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print(f"Train size: {len(X_train)} | Test size: {len(X_test)}")

    # Preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_features),
            ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), cat_features)
        ]
    )

    from sklearn.ensemble import GradientBoostingClassifier

    # Build Pipeline with Gradient Boosting Classifier
    gb_classifier = GradientBoostingClassifier(
        n_estimators=180,
        learning_rate=0.08,
        max_depth=4,
        subsample=0.85,
        random_state=42
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", gb_classifier)
    ])

    print("Fitting model...")
    pipeline.fit(X_train, y_train)

    # Predictions & Probabilities
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    # Performance Metrics
    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_proba)), 4),
        "precision": round(float(precision_score(y_test, y_pred)), 4),
        "recall": round(float(recall_score(y_test, y_pred)), 4),
        "f1_score": round(float(f1_score(y_test, y_pred)), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
    }

    print("=" * 45)
    print(f"MODEL PERFORMANCE RESULTS:")
    print(f"ROC-AUC Score: {metrics['roc_auc'] * 100:.2f}%")
    print(f"Recall (At-Risk Caught): {metrics['recall'] * 100:.2f}%")
    print(f"Precision: {metrics['precision'] * 100:.2f}%")
    print(f"F1-Score: {metrics['f1_score']:.4f}")
    print("=" * 45)

    # Save metrics JSON
    with open(os.path.join(output_dir, "model_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=4)

    # Extract Feature Importances
    encoder = pipeline.named_steps["preprocessor"].named_transformers_["cat"]
    cat_feature_names = encoder.get_feature_names_out(cat_features).tolist()
    all_feature_names = num_features + cat_feature_names

    importances = pipeline.named_steps["classifier"].feature_importances_
    df_importances = pd.DataFrame({
        "feature": all_feature_names,
        "importance": importances
    }).sort_values(by="importance", ascending=False)

    df_importances.to_csv(os.path.join(output_dir, "feature_importance.csv"), index=False)
    print("\nTop 5 Leading Drivers of Churn:")
    print(df_importances.head(5).to_string(index=False))

    # Save trained pipeline model
    joblib.dump(pipeline, os.path.join(output_dir, "churn_model.pkl"))
    print(f"\nModel pipeline saved to {os.path.join(output_dir, 'churn_model.pkl')}")

    return pipeline, metrics

if __name__ == "__main__":
    train_churn_pipeline()
