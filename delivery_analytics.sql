-- ============================================================
-- CLIENT DELIVERY INTELLIGENCE — SQL ANALYTICS SUITE
-- IT Services Project Health & SLA Analytics
-- Author: Keerthi RK
-- ============================================================


-- ─────────────────────────────────────────────────────────────
-- QUERY 1: Client Health Scorecard
-- Business: Rank all accounts by delivery health in one query
-- ─────────────────────────────────────────────────────────────
SELECT
    c.client_id,
    c.client_name,
    c.industry,
    c.tier,
    COUNT(DISTINCT p.project_id)                                AS total_projects,
    ROUND(100.0 * SUM(CASE WHEN p.status = 'On Track' THEN 1 ELSE 0 END) / COUNT(p.project_id), 1) AS on_track_pct,
    ROUND(AVG(p.cost_overrun_pct), 1)                          AS avg_cost_overrun_pct,
    COUNT(DISTINCT t.ticket_id)                                AS total_tickets,
    ROUND(100.0 * SUM(t.sla_breached) / COUNT(t.ticket_id), 1) AS sla_breach_rate_pct,
    ROUND(AVG(t.csat_score), 2)                                AS avg_csat,
    CASE
        WHEN AVG(t.csat_score) >= 4.2
         AND 100.0 * SUM(t.sla_breached)/COUNT(t.ticket_id) <= 5
         AND AVG(p.cost_overrun_pct) <= 10
        THEN 'HEALTHY'
        WHEN 100.0 * SUM(t.sla_breached)/COUNT(t.ticket_id) > 20
          OR AVG(p.cost_overrun_pct) > 25
        THEN 'CRITICAL'
        ELSE 'AT RISK'
    END                                                         AS health_status
FROM clients c
LEFT JOIN projects  p ON c.client_id = p.client_id
LEFT JOIN tickets   t ON c.client_id = t.client_id
GROUP BY c.client_id, c.client_name, c.industry, c.tier
ORDER BY sla_breach_rate_pct DESC, avg_cost_overrun_pct DESC;


-- ─────────────────────────────────────────────────────────────
-- QUERY 2: SLA Breach Early Warning — 4-Week Trend
-- Business: Which accounts are trending TOWARD an SLA breach?
-- This is the 14-day early warning signal.
-- ─────────────────────────────────────────────────────────────
WITH weekly_breach AS (
    SELECT
        client_id,
        week,
        COUNT(*)                                                AS tickets,
        SUM(sla_breached)                                       AS breaches,
        ROUND(100.0 * SUM(sla_breached) / COUNT(*), 1)         AS breach_rate_pct
    FROM tickets
    GROUP BY client_id, week
),
recent_vs_prior AS (
    SELECT
        client_id,
        AVG(CASE WHEN week >= (SELECT MAX(week) FROM tickets) - 3
                 THEN breach_rate_pct END)                      AS recent_4wk_breach_rate,
        AVG(CASE WHEN week BETWEEN (SELECT MAX(week) FROM tickets) - 11
                              AND  (SELECT MAX(week) FROM tickets) - 4
                 THEN breach_rate_pct END)                      AS prior_8wk_breach_rate
    FROM weekly_breach
    GROUP BY client_id
)
SELECT
    r.client_id,
    c.client_name,
    c.tier,
    ROUND(r.prior_8wk_breach_rate, 1)                          AS prior_breach_rate_pct,
    ROUND(r.recent_4wk_breach_rate, 1)                         AS recent_breach_rate_pct,
    ROUND(r.recent_4wk_breach_rate - r.prior_8wk_breach_rate, 1) AS trend_change_pct,
    CASE
        WHEN r.recent_4wk_breach_rate - r.prior_8wk_breach_rate > 10 THEN '🔴 ESCALATING — Intervene Now'
        WHEN r.recent_4wk_breach_rate - r.prior_8wk_breach_rate > 5  THEN '🟡 WARNING — Monitor Closely'
        ELSE '🟢 STABLE'
    END                                                         AS sla_trend_status
FROM recent_vs_prior r
JOIN clients c ON r.client_id = c.client_id
ORDER BY trend_change_pct DESC;


-- ─────────────────────────────────────────────────────────────
-- QUERY 3: Revenue Leakage Report
-- Business: How much billable revenue is being lost to unbilled hours?
-- ─────────────────────────────────────────────────────────────
SELECT
    t.client_id,
    c.client_name,
    c.tier,
    ROUND(SUM(t.billable_hrs), 0)                              AS total_billable_hrs,
    ROUND(SUM(t.unbilled_hrs), 0)                              AS total_unbilled_hrs,
    ROUND(100.0 * SUM(t.unbilled_hrs) /
          NULLIF(SUM(t.billable_hrs + t.unbilled_hrs), 0), 1) AS leakage_rate_pct,
    ROUND(SUM(t.unbilled_hrs) * 2.5, 1)                       AS est_revenue_lost_lakh,
    CASE
        WHEN 100.0 * SUM(t.unbilled_hrs) /
             NULLIF(SUM(t.billable_hrs + t.unbilled_hrs),0) > 15 THEN 'HIGH LEAKAGE'
        WHEN 100.0 * SUM(t.unbilled_hrs) /
             NULLIF(SUM(t.billable_hrs + t.unbilled_hrs),0) > 8  THEN 'MEDIUM LEAKAGE'
        ELSE 'ACCEPTABLE'
    END                                                        AS leakage_category
FROM timesheets t
JOIN clients c ON t.client_id = c.client_id
GROUP BY t.client_id, c.client_name, c.tier
ORDER BY est_revenue_lost_lakh DESC;


-- ─────────────────────────────────────────────────────────────
-- QUERY 4: Resource Utilisation — Over/Under Allocation
-- Business: Who is burning out and who is sitting idle?
-- ─────────────────────────────────────────────────────────────
SELECT
    con.consultant_id,
    con.grade,
    con.primary_skill,
    ROUND(AVG(ts.utilisation_pct), 1)                          AS avg_utilisation_pct,
    SUM(CASE WHEN ts.utilisation_pct > 100 THEN 1 ELSE 0 END)  AS weeks_overloaded,
    SUM(CASE WHEN ts.utilisation_pct < 60  THEN 1 ELSE 0 END)  AS weeks_underutilised,
    ROUND(SUM(ts.overtime_hrs), 0)                             AS total_overtime_hrs,
    CASE
        WHEN AVG(ts.utilisation_pct) > 105 THEN '🔴 BURNOUT RISK'
        WHEN AVG(ts.utilisation_pct) > 95  THEN '🟡 OVERLOADED'
        WHEN AVG(ts.utilisation_pct) >= 75 THEN '🟢 OPTIMAL'
        WHEN AVG(ts.utilisation_pct) >= 50 THEN '🟡 UNDERUTILISED'
        ELSE '🔴 IDLE — Revenue Leakage'
    END                                                        AS utilisation_status
FROM consultants con
JOIN timesheets ts ON con.consultant_id = ts.consultant_id
GROUP BY con.consultant_id, con.grade, con.primary_skill
ORDER BY avg_utilisation_pct DESC;


-- ─────────────────────────────────────────────────────────────
-- QUERY 5: Watermelon Account Detection
-- Business: Find accounts that look green on delivery status
--           but have worsening SLA/revenue signals underneath
-- ─────────────────────────────────────────────────────────────
WITH delivery_surface AS (
    SELECT
        client_id,
        ROUND(100.0 * SUM(CASE WHEN status='On Track' THEN 1 ELSE 0 END) / COUNT(*), 1) AS surface_health_pct
    FROM projects
    GROUP BY client_id
),
underlying_signals AS (
    SELECT
        client_id,
        ROUND(100.0 * SUM(sla_breached) / COUNT(*), 1)         AS breach_rate_pct,
        ROUND(AVG(csat_score), 2)                              AS avg_csat,
        SUM(escalated)                                         AS total_escalations
    FROM tickets
    GROUP BY client_id
)
SELECT
    d.client_id,
    c.client_name,
    c.tier,
    d.surface_health_pct                                       AS projects_on_track_pct,
    u.breach_rate_pct,
    u.avg_csat,
    u.total_escalations,
    CASE
        WHEN d.surface_health_pct >= 60
         AND (u.breach_rate_pct > 20 OR u.avg_csat < 3.5 OR u.total_escalations > 10)
        THEN '🍉 WATERMELON — Looks healthy, is at risk'
        WHEN d.surface_health_pct < 40
        THEN '🔴 VISIBLY STRUGGLING'
        ELSE '🟢 GENUINELY HEALTHY'
    END                                                        AS account_reality
FROM delivery_surface d
JOIN underlying_signals u ON d.client_id = u.client_id
JOIN clients c ON d.client_id = c.client_id
ORDER BY
    CASE WHEN d.surface_health_pct >= 60
          AND (u.breach_rate_pct > 20 OR u.avg_csat < 3.5)
         THEN 0 ELSE 1 END,
    u.breach_rate_pct DESC;
