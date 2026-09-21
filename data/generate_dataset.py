"""
Realistic B2B SaaS Dataset Generator
Generates relational customer, subscription, usage, and support data with realistic business correlations.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set seeds for reproducibility
np.random.seed(42)
random.seed(42)

def generate_saas_dataset(num_customers=5000, output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    print(f"Generating realistic SaaS dataset with {num_customers} customer accounts...")

    # Company name elements
    prefixes = ["Apex", "Cloud", "Data", "Nova", "Pulse", "Stratum", "Sync", "Vanguard", "Omni", "Hyper", "Zenith", "Quantum", "Nexus", "Vertex", "Blue"]
    suffixes = ["Logic", "Scale", "Stack", "Flow", "Sphere", "Analytics", "Works", "Hub", "Systems", "AI", "Corp", "Labs", "Tech", "Security", "Pay"]
    
    company_names = []
    for i in range(num_customers):
        name = f"{prefixes[i % len(prefixes)]} {suffixes[(i * 7) % len(suffixes)]} {100 + (i // len(prefixes))}"
        company_names.append(name)

    # 1. Customers Table
    customer_ids = [f"CUST-{10000 + i}" for i in range(num_customers)]
    tiers = np.random.choice(["Enterprise", "Mid-Market", "SMB"], size=num_customers, p=[0.15, 0.35, 0.50])
    industries = np.random.choice(
        ["Fintech", "Healthcare", "E-Commerce", "SaaS / Tech", "Logistics & Supply Chain", "Cybersecurity"],
        size=num_customers,
        p=[0.25, 0.20, 0.20, 0.15, 0.10, 0.10]
    )
    countries = np.random.choice(
        ["United States", "United Kingdom", "Canada", "Germany", "India", "Australia"],
        size=num_customers,
        p=[0.50, 0.18, 0.12, 0.08, 0.07, 0.05]
    )

    # Signup dates spanning 24 months (Jan 2024 to Dec 2025)
    start_anchor = datetime(2024, 1, 1)
    signup_dates = [start_anchor + timedelta(days=int(np.random.uniform(0, 720))) for _ in range(num_customers)]
    signup_dates.sort()

    df_customers = pd.DataFrame({
        "customer_id": customer_ids,
        "company_name": company_names,
        "tier": tiers,
        "industry": industries,
        "country": countries,
        "signup_date": [d.strftime("%Y-%m-%d") for d in signup_dates]
    })

    # 2. Subscriptions Table
    plan_types = []
    billing_cycles = []
    mrr_values = []
    seats_list = []

    for tier in tiers:
        if tier == "Enterprise":
            plan = np.random.choice(["Scale", "Enterprise Plus"], p=[0.3, 0.7])
            cycle = np.random.choice(["Annual", "Monthly"], p=[0.85, 0.15])
            mrr = round(float(np.random.uniform(4500, 18000)), 2)
            seats = int(np.random.uniform(100, 500))
        elif tier == "Mid-Market":
            plan = np.random.choice(["Growth", "Scale"], p=[0.6, 0.4])
            cycle = np.random.choice(["Annual", "Monthly"], p=[0.55, 0.45])
            mrr = round(float(np.random.uniform(900, 3800)), 2)
            seats = int(np.random.uniform(25, 100))
        else: # SMB
            plan = np.random.choice(["Starter", "Growth"], p=[0.7, 0.3])
            cycle = np.random.choice(["Annual", "Monthly"], p=[0.25, 0.75])
            mrr = round(float(np.random.uniform(120, 750)), 2)
            seats = int(np.random.uniform(5, 25))

        plan_types.append(plan)
        billing_cycles.append(cycle)
        mrr_values.append(mrr)
        seats_list.append(seats)

    # 3. Product Usage Table
    license_utilization = []
    feature_adoption_scores = []
    weekly_active_days = []
    api_calls_monthly = []
    last_active_days_ago = []

    for i in range(num_customers):
        # Base distributions
        util = np.clip(np.random.normal(0.70, 0.22), 0.05, 1.0)
        feat = np.clip(int(np.random.normal(68, 20)), 10, 100)
        days = np.clip(int(np.random.normal(4.5, 1.6)), 0, 7)
        api = int(np.random.exponential(25000)) + 500
        days_ago = int(np.random.exponential(6))

        license_utilization.append(round(util, 3))
        feature_adoption_scores.append(feat)
        weekly_active_days.append(days)
        api_calls_monthly.append(api)
        last_active_days_ago.append(min(days_ago, 90))

    # 4. Support Tickets Table
    total_tickets = []
    avg_resolution_hrs = []
    escalations = []
    csat_scores = []

    for i in range(num_customers):
        t_count = np.random.poisson(lam=4)
        if t_count == 0:
            res_hrs = 4.0
            esc = 0
            csat = round(float(np.random.uniform(4.2, 5.0)), 1)
        else:
            # Latency spike for some accounts
            if random.random() < 0.25:
                res_hrs = round(float(np.random.uniform(48, 120)), 1) # delayed support
                esc = np.random.binomial(n=t_count, p=0.4)
                csat = round(float(np.random.uniform(1.2, 3.2)), 1)
            else:
                res_hrs = round(float(np.random.uniform(2, 24)), 1)
                esc = 0
                csat = round(float(np.random.uniform(3.8, 5.0)), 1)

        total_tickets.append(t_count)
        avg_resolution_hrs.append(res_hrs)
        escalations.append(esc)
        csat_scores.append(csat)

    # 5. Determine Churn with realistic business logic
    churn_flags = []
    churn_dates = []
    churn_reasons = []

    for i in range(num_customers):
        signup = signup_dates[i]
        util = license_utilization[i]
        res_time = avg_resolution_hrs[i]
        cycle = billing_cycles[i]
        tier = tiers[i]
        csat = csat_scores[i]
        days_ago = last_active_days_ago[i]

        # Calculate churn probability based on empirical factors
        churn_prob = 0.08 # baseline 8%
        if util < 0.40:
            churn_prob += 0.30
        if res_time > 48.0:
            churn_prob += 0.28
        if csat < 2.5:
            churn_prob += 0.25
        if days_ago > 21:
            churn_prob += 0.35
        if cycle == "Monthly":
            churn_prob += 0.10
        if tier == "Enterprise":
            churn_prob -= 0.12 # higher switching costs

        churn_prob = np.clip(churn_prob, 0.02, 0.92)
        is_churn = 1 if (random.random() < churn_prob) else 0
        churn_flags.append(is_churn)

        if is_churn:
            # Churned between 30 and 360 days after signup
            lifespan_days = int(np.random.uniform(30, 360))
            churn_dt = signup + timedelta(days=lifespan_days)
            if churn_dt > datetime(2025, 12, 31):
                churn_dt = datetime(2025, 12, 31)
            churn_dates.append(churn_dt.strftime("%Y-%m-%d"))

            # Reason
            if res_time > 48.0 or csat < 2.5:
                reason = "Support / SLA Frustration"
            elif util < 0.40 or days_ago > 21:
                reason = "Low Adoption & License Waste"
            elif tier == "SMB":
                reason = np.random.choice(["Price / Budget Cuts", "Competitor Alternative", "Switched Tool"])
            else:
                reason = np.random.choice(["Leadership Transition", "Competitor Alternative", "Internal Restructuring"])
            churn_reasons.append(reason)
        else:
            churn_dates.append(None)
            churn_reasons.append(None)

    df_subscriptions = pd.DataFrame({
        "subscription_id": [f"SUB-{20000 + i}" for i in range(num_customers)],
        "customer_id": customer_ids,
        "plan_type": plan_types,
        "billing_cycle": billing_cycles,
        "mrr": mrr_values,
        "seats_purchased": seats_list,
        "start_date": [d.strftime("%Y-%m-%d") for d in signup_dates],
        "end_date": churn_dates,
        "status": ["Churned" if c == 1 else "Active" for c in churn_flags],
        "churn_reason": churn_reasons
    })

    df_usage = pd.DataFrame({
        "customer_id": customer_ids,
        "license_utilization_rate": license_utilization,
        "feature_adoption_score": feature_adoption_scores,
        "weekly_active_days": weekly_active_days,
        "api_calls_monthly": api_calls_monthly,
        "last_active_days_ago": last_active_days_ago
    })

    df_support = pd.DataFrame({
        "customer_id": customer_ids,
        "total_tickets": total_tickets,
        "avg_resolution_time_hrs": avg_resolution_hrs,
        "escalated_tickets_count": escalations,
        "csat_score": csat_scores
    })

    # Combined analytical master table
    df_master = df_customers.merge(df_subscriptions, on="customer_id")
    df_master = df_master.merge(df_usage, on="customer_id")
    df_master = df_master.merge(df_support, on="customer_id")
    df_master["churn_label"] = churn_flags

    # Save to CSV files
    df_customers.to_csv(os.path.join(output_dir, "customers.csv"), index=False)
    df_subscriptions.to_csv(os.path.join(output_dir, "subscriptions.csv"), index=False)
    df_usage.to_csv(os.path.join(output_dir, "product_usage.csv"), index=False)
    df_support.to_csv(os.path.join(output_dir, "support_tickets.csv"), index=False)
    df_master.to_csv(os.path.join(output_dir, "master_retention_data.csv"), index=False)

    print(f"Generated {len(df_master)} records.")
    print(f"Overall Churn Rate: {df_master['churn_label'].mean() * 100:.2f}%")
    print(f"Total Annual Recurring Revenue (ARR): ${(df_master[df_master['status']=='Active']['mrr'].sum() * 12):,.2f}")
    return df_master

if __name__ == "__main__":
    generate_saas_dataset(num_customers=5000, output_dir="data")
