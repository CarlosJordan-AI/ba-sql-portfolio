-- Report: Monthly Revenue, Cost, Margin, and Margin % by Region
-- Description: Aggregates monthly revenue and cost data per region
--              and calculates profit margin percentage.

SELECT
    strftime('%Y-%m', o.order_date) AS month,
    c.region,
    ROUND(SUM(o.revenue), 2) AS total_revenue,
    ROUND(SUM(o.cost), 2) AS total_cost,
    ROUND(SUM(o.revenue - o.cost), 2) AS margin,
    ROUND((SUM(o.revenue - o.cost) * 100.0 / NULLIF(SUM(o.revenue), 0)), 2) AS margin_pct
FROM
    orders o
JOIN
    customers c ON o.customer_id = c.customer_id
GROUP BY
    month, c.region
ORDER BY
    month, c.region;
