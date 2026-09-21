-- ====================================================================
-- 03_customer_health_score.sql
-- Composite Customer Health Index & Retention Segmentation
-- Combines Product Usage (40%), CSAT (30%), and Support SLA (30%).
-- ====================================================================

WITH account_metrics AS (
    SELECT
        c.customer_id,
        c.company_name,
        c.tier,
        c.industry,
        s.mrr,
        s.billing_cycle,
        s.status,
        u.license_utilization_rate,
        u.feature_adoption_score,
        u.weekly_active_days,
        u.last_active_days_ago,
        t.avg_resolution_time_hrs,
        t.escalated_tickets_count,
        t.csat_score
    FROM customers c
    JOIN subscriptions s ON c.customer_id = s.customer_id
    JOIN product_usage u ON c.customer_id = u.customer_id
    JOIN support_tickets t ON c.customer_id = t.customer_id
),

scored_accounts AS (
    SELECT
        customer_id,
        company_name,
        tier,
        industry,
        mrr,
        status,
        last_active_days_ago,
        avg_resolution_time_hrs,
        -- Sub-score 1: Product Engagement Score (0 - 40 points)
        (
            (license_utilization_rate * 20.0) +
            (feature_adoption_score / 100.0 * 12.0) +
            (weekly_active_days / 7.0 * 8.0)
        ) AS engagement_score,

        -- Sub-score 2: Customer Satisfaction Score (0 - 30 points)
        (
            (csat_score / 5.0 * 30.0)
        ) AS satisfaction_score,

        -- Sub-score 3: Support SLA Health (0 - 30 points, penalized by latency and escalations)
        (
            CASE
                WHEN avg_resolution_time_hrs <= 12.0 THEN 30.0
                WHEN avg_resolution_time_hrs <= 24.0 THEN 22.0
                WHEN avg_resolution_time_hrs <= 48.0 THEN 14.0
                ELSE 4.0
            END - (escalated_tickets_count * 5.0)
        ) AS support_health_score
    FROM account_metrics
),

composite_health AS (
    SELECT
        customer_id,
        company_name,
        tier,
        industry,
        mrr,
        status,
        last_active_days_ago,
        ROUND(engagement_score, 1) AS engagement_score,
        ROUND(satisfaction_score, 1) AS satisfaction_score,
        ROUND(support_health_score, 1) AS support_health_score,
        ROUND(
            engagement_score + satisfaction_score +
            CASE WHEN support_health_score < 0 THEN 0 ELSE support_health_score END,
            1
        ) AS total_health_score
    FROM scored_accounts
)

-- Final Segment Categorization
SELECT
    customer_id,
    company_name,
    tier,
    industry,
    mrr,
    status,
    total_health_score,
    CASE
        WHEN total_health_score >= 80.0 THEN 'Healthy (Champion)'
        WHEN total_health_score >= 60.0 THEN 'Neutral (Monitor)'
        WHEN total_health_score >= 40.0 THEN 'At-Risk (Action Required)'
        ELSE 'Critical Risk (Immediate Escalation)'
    END AS health_category,
    CASE
        WHEN total_health_score < 40.0 AND tier = 'Enterprise' THEN 'Priority CSM Call + Executive Outreach'
        WHEN total_health_score < 40.0 AND tier = 'Mid-Market' THEN 'Onboarding Audit + Technical Review'
        WHEN total_health_score < 40.0 THEN 'Automated Re-engagement + Discount Offer'
        ELSE 'Quarterly Business Review'
    END AS recommended_retention_playbook
FROM composite_health
ORDER BY total_health_score ASC, mrr DESC;
