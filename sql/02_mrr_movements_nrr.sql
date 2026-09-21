-- ====================================================================
-- 02_mrr_movements_nrr.sql
-- Monthly MRR Bridge & Net Revenue Retention (NRR) Analysis
-- Breaks down Starting MRR, New MRR, Expansion, Contraction, and Churn.
-- ====================================================================

WITH monthly_subscriptions AS (
    SELECT
        customer_id,
        STRFTIME('%Y-%m', start_date) AS active_month,
        mrr,
        status,
        billing_cycle
    FROM subscriptions
),

customer_monthly_mrr AS (
    SELECT
        customer_id,
        active_month,
        SUM(mrr) AS current_mrr,
        LAG(SUM(mrr), 1, 0.0) OVER (PARTITION BY customer_id ORDER BY active_month) AS prior_mrr
    FROM monthly_subscriptions
    GROUP BY customer_id, active_month
),

mrr_categories AS (
    SELECT
        active_month,
        customer_id,
        current_mrr,
        prior_mrr,
        -- New MRR: First time billing
        CASE WHEN prior_mrr = 0.0 AND current_mrr > 0.0 THEN current_mrr ELSE 0.0 END AS new_mrr,
        -- Expansion MRR: Increased contract value
        CASE WHEN prior_mrr > 0.0 AND current_mrr > prior_mrr THEN current_mrr - prior_mrr ELSE 0.0 END AS expansion_mrr,
        -- Contraction MRR: Downgraded contract value
        CASE WHEN prior_mrr > 0.0 AND current_mrr < prior_mrr AND current_mrr > 0.0 THEN prior_mrr - current_mrr ELSE 0.0 END AS contraction_mrr,
        -- Churned MRR: Completely lost account
        CASE WHEN current_mrr = 0.0 AND prior_mrr > 0.0 THEN prior_mrr ELSE 0.0 END AS churned_mrr
    FROM customer_monthly_mrr
)

-- Summary Bridge & Net Revenue Retention (NRR) Rate
SELECT
    active_month,
    ROUND(SUM(prior_mrr), 2) AS starting_mrr,
    ROUND(SUM(new_mrr), 2) AS new_mrr,
    ROUND(SUM(expansion_mrr), 2) AS expansion_mrr,
    ROUND(SUM(contraction_mrr), 2) AS contraction_mrr,
    ROUND(SUM(churned_mrr), 2) AS churned_mrr,
    ROUND(SUM(current_mrr), 2) AS ending_mrr,
    -- NRR = (Starting MRR + Expansion - Contraction - Churn) / Starting MRR * 100
    ROUND(
        CASE
            WHEN SUM(prior_mrr) > 0 THEN
                ((SUM(prior_mrr) + SUM(expansion_mrr) - SUM(contraction_mrr) - SUM(churned_mrr)) / SUM(prior_mrr)) * 100.0
            ELSE 100.0
        END,
        2
    ) AS net_revenue_retention_pct
FROM mrr_categories
GROUP BY active_month
ORDER BY active_month ASC;
