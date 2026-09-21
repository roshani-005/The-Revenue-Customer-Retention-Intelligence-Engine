"""
Plotly Chart Components for Streamlit Dashboard
High-contrast, publication-grade interactive visualizations.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def plot_cohort_heatmap(pivot_df):
    """
    Renders an interactive triangular cohort retention heatmap.
    """
    z_values = pivot_df.values
    x_labels = [f"M+{c}" for c in pivot_df.columns]
    y_labels = list(pivot_df.index)

    # Custom text annotations
    text_values = []
    for row in z_values:
        text_row = []
        for val in row:
            if np.isnan(val):
                text_row.append("")
            else:
                text_row.append(f"{val:.1f}%")
        text_values.append(text_row)

    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=x_labels,
        y=y_labels,
        text=text_values,
        texttemplate="%{text}",
        textfont={"size": 11, "color": "white"},
        colorscale="Viridis",
        hoverongaps=False,
        colorbar=dict(title="Retention %")
    ))

    fig.update_layout(
        title="<b>Monthly Cohort Retention Heatmap (12-Month Horizon)</b>",
        xaxis_title="Months Since First Subscription",
        yaxis_title="Signup Cohort Month",
        height=520,
        margin=dict(l=40, r=40, t=60, b=40),
        template="plotly_dark"
    )
    return fig

def plot_feature_importance(df_importance):
    """
    Horizontal bar chart of leading churn drivers.
    """
    top10 = df_importance.head(8).copy()
    top10["clean_feature"] = top10["feature"].str.replace("_", " ").str.title()
    top10 = top10.sort_values(by="importance", ascending=True)

    fig = go.Figure(go.Bar(
        x=top10["importance"] * 100,
        y=top10["clean_feature"],
        orientation="h",
        marker=dict(
            color=top10["importance"],
            colorscale="Tealgrn",
            showscale=False
        ),
        text=[f"{v:.1f}%" for v in (top10["importance"] * 100)],
        textposition="outside"
    ))

    fig.update_layout(
        title="<b>Primary Churn Drivers (Relative Feature Impact %)</b>",
        xaxis_title="Relative Impact on Churn Probability (%)",
        yaxis_title="",
        height=380,
        margin=dict(l=40, r=40, t=50, b=30),
        template="plotly_dark"
    )
    return fig

def plot_support_vs_churn(df):
    """
    Binned support ticket resolution time vs churn rate.
    """
    df_copy = df.copy()
    df_copy["res_bin"] = pd.cut(
        df_copy["avg_resolution_time_hrs"],
        bins=[0, 12, 24, 48, 120],
        labels=["< 12h (Fast)", "12-24h (Normal)", "24-48h (Delayed)", "> 48h (Critical Lag)"]
    )
    grouped = df_copy.groupby("res_bin", observed=False).agg(
        churn_rate=("churn_label", lambda x: x.mean() * 100),
        accounts=("customer_id", "count")
    ).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped["res_bin"],
        y=grouped["churn_rate"],
        text=[f"{v:.1f}%" for v in grouped["churn_rate"]],
        textposition="outside",
        marker_color=["#2ecc71", "#3498db", "#e67e22", "#e74c3c"]
    ))

    fig.update_layout(
        title="<b>Support SLA Impact: Resolution Time vs. Churn Rate</b>",
        xaxis_title="Average Ticket Resolution Window",
        yaxis_title="Observed Churn Rate (%)",
        height=380,
        margin=dict(l=40, r=40, t=50, b=30),
        template="plotly_dark"
    )
    return fig

def plot_mrr_by_tier(df):
    """
    Donut chart of ARR distribution across Customer Tiers.
    """
    grouped = df[df["status"] == "Active"].groupby("tier")["mrr"].sum().reset_index()
    grouped["arr"] = grouped["mrr"] * 12

    fig = px.pie(
        grouped,
        names="tier",
        values="arr",
        hole=0.55,
        title="<b>Active ARR Distribution by Customer Tier</b>",
        color_discrete_sequence=["#636EFA", "#00CC96", "#AB63FA"],
        template="plotly_dark"
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(height=380, margin=dict(l=40, r=40, t=50, b=30))
    return fig
