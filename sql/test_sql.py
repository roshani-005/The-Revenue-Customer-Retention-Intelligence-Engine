import sqlite3
import pandas as pd

def test_sql():
    conn = sqlite3.connect(":memory:")
    
    # Load CSVs
    customers = pd.read_csv("data/customers.csv")
    subscriptions = pd.read_csv("data/subscriptions.csv")
    usage = pd.read_csv("data/product_usage.csv")
    support = pd.read_csv("data/support_tickets.csv")

    customers.to_sql("customers", conn, index=False)
    subscriptions.to_sql("subscriptions", conn, index=False)
    usage.to_sql("product_usage", conn, index=False)
    support.to_sql("support_tickets", conn, index=False)

    print("Loaded tables into SQLite.")

    for sql_file in ["sql/01_monthly_cohort_retention.sql", "sql/02_mrr_movements_nrr.sql", "sql/03_customer_health_score.sql"]:
        with open(sql_file, "r") as f:
            query = f.read()
        res = pd.read_sql_query(query, conn)
        print(f"[PASS] {sql_file}: {len(res)} rows returned.")

    conn.close()

if __name__ == "__main__":
    test_sql()
