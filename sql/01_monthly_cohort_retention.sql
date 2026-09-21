-- ====================================================================
-- 01_monthly_cohort_retention.sql
-- Enterprise Cohort Retention Matrix (12-Month Window)
-- Computes signup cohorts and tracks month-over-month account retention.
-- ====================================================================

WITH customer_cohorts AS (
    -- Step 1: Assign each customer to their initial signup cohort month
    SELECT
        customer_id,
        STRFTIME('%Y-%m', signup_date) AS cohort_month,
        signup_date
    FROM customers
),

user_activities AS (
    -- Step 2: Determine months where customer was actively subscribed
    SELECT
        s.customer_id,
        c.cohort_month,
        STRFTIME('%Y-%m', s.start_date) AS sub_start_month,
        COALESCE(STRFTIME('%Y-%m', s.end_date), '2026-01') AS sub_end_month,
        s.status
    FROM subscriptions s
    JOIN customer_cohorts c ON s.customer_id = c.customer_id
),

cohort_size AS (
    -- Step 3: Count total new accounts in each signup cohort (Month 0 base)
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_id) AS total_cohort_accounts
    FROM customer_cohorts
    GROUP BY cohort_month
),

cohort_retention_raw AS (
    -- Step 4: Calculate active accounts across subsequent calendar months
    SELECT
        c.cohort_month,
        -- Calculate the relative month index (0 = signup month, 1 = month 1, etc.)
        (CAST(STRFTIME('%Y', s.start_date) AS INT) - CAST(SUBSTR(c.cohort_month, 1, 4) AS INT)) * 12 +
        (CAST(STRFTIME('%m', s.start_date) AS INT) - CAST(SUBSTR(c.cohort_month, 6, 2) AS INT)) AS month_number,
        COUNT(DISTINCT s.customer_id) AS active_accounts
    FROM subscriptions s
    JOIN customer_cohorts c ON s.customer_id = c.customer_id
    WHERE s.status = 'Active' OR s.end_date IS NULL OR s.end_date > s.start_date
    GROUP BY c.cohort_month, month_number
)

-- Step 5: Final Cohort Retention Matrix with Retention Rates (%)
SELECT
    r.cohort_month,
    cs.total_cohort_accounts,
    r.month_number,
    r.active_accounts,
    ROUND(CAST(r.active_accounts AS FLOAT) / cs.total_cohort_accounts * 100.0, 2) AS retention_rate_pct
FROM cohort_retention_raw r
JOIN cohort_size cs ON r.cohort_month = cs.cohort_month
WHERE r.month_number BETWEEN 0 AND 12
ORDER BY r.cohort_month ASC, r.month_number ASC;
