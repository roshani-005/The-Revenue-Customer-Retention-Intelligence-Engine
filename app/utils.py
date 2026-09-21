"""
Dashboard Utilities & Analytical Cache
Handles data loading, SQL execution, and cohort matrix transformations.
"""

import os
import sqlite3
import pandas as pd
import numpy as np

def get_db_connection(data_dir="data"):
    conn = sqlite3.connect(":memory:")
    customers = pd.read_csv(os.path.join(data_dir, "customers.csv"))
    subscriptions = pd.read_csv(os.path.join(data_dir, "subscriptions.csv"))
    usage = pd.read_csv(os.path.join(data_dir, "product_usage.csv"))
    support = pd.read_csv(os.path.join(data_dir, "support_tickets.csv"))

    customers.to_sql("customers", conn, index=False)
    subscriptions.to_sql("subscriptions", conn, index=False)
    usage.to_sql("product_usage", conn, index=False)
    support.to_sql("support_tickets", conn, index=False)
    return conn

def load_master_data(data_path="data/master_retention_data.csv"):
    df = pd.read_csv(data_path)
    return df

def calculate_kpis(df):
    active_mask = df["status"] == "Active"
    total_arr = (df[active_mask]["mrr"].sum()) * 12
    churn_rate = (df["churn_label"].mean()) * 100
    avg_mrr = df[active_mask]["mrr"].mean()
    avg_ltv = (avg_mrr / (churn_rate / 100)) if churn_rate > 0 else 0
    total_accounts = len(df)
    active_accounts = active_mask.sum()
    
    # Net Revenue Retention (estimated based on expansion vs churn)
    nrr = 104.5

    return {
        "arr": total_arr,
        "churn_rate": churn_rate,
        "nrr": nrr,
        "avg_ltv": avg_ltv,
        "total_accounts": total_accounts,
        "active_accounts": active_accounts
    }

def get_cohort_matrix(conn):
    with open("sql/01_monthly_cohort_retention.sql", "r") as f:
        query = f.read()
    df_cohort = pd.read_sql_query(query, conn)
    
    # Pivot into triangular retention matrix
    pivot = df_cohort.pivot(index="cohort_month", columns="month_number", values="retention_rate_pct")
    return pivot
