
-- =====================================================
-- 1. LATEST STOCK PRICES
-- =====================================================

SELECT
    ticker,
    date,
    close,
    adj_close,
    volume
FROM stock_prices
WHERE (ticker, date) IN (
    SELECT ticker, MAX(date)
    FROM stock_prices
    GROUP BY ticker
)
ORDER BY ticker;


-- =====================================================
-- 2. TOTAL STOCK RETURN
-- Using CTEs and ROW_NUMBER()
-- =====================================================

WITH ranked_prices AS (

    SELECT
        ticker,
        date,
        adj_close,

        ROW_NUMBER() OVER (
            PARTITION BY ticker
            ORDER BY date ASC
        ) AS first_day,

        ROW_NUMBER() OVER (
            PARTITION BY ticker
            ORDER BY date DESC
        ) AS last_day

    FROM stock_prices

),

first_prices AS (

    SELECT ticker, adj_close
    FROM ranked_prices
    WHERE first_day = 1

),

last_prices AS (

    SELECT ticker, adj_close
    FROM ranked_prices
    WHERE last_day = 1

)

SELECT
    f.ticker,

    ROUND(
        (l.adj_close - f.adj_close)
        / f.adj_close * 100,
        2
    ) AS total_return_pct

FROM first_prices f

JOIN last_prices l
    ON f.ticker = l.ticker

ORDER BY total_return_pct DESC;


-- =====================================================
-- 3. DAILY RETURN STATISTICS
-- =====================================================

SELECT
    ticker,

    ROUND(AVG(daily_return_pct), 4)
        AS avg_daily_return,

    ROUND(MIN(daily_return_pct), 4)
        AS worst_daily_return,

    ROUND(MAX(daily_return_pct), 4)
        AS best_daily_return

FROM stock_prices

GROUP BY ticker

ORDER BY avg_daily_return DESC;


-- =====================================================
-- 4. TOP 10 HIGHEST TRADING VOLUMES
-- =====================================================

SELECT
    ticker,
    date,
    volume

FROM stock_prices

ORDER BY volume DESC

LIMIT 10;


-- =====================================================
-- 5. DUPLICATE RECORD CHECK
-- =====================================================

SELECT
    ticker,
    date,
    COUNT(*) AS duplicate_count

FROM stock_prices

GROUP BY ticker, date

HAVING COUNT(*) > 1;


-- =====================================================
-- 6. 7-DAY MOVING AVERAGE
-- Using a window function
-- =====================================================

SELECT
    ticker,
    date,
    adj_close,

    ROUND(
        AVG(adj_close) OVER (
            PARTITION BY ticker
            ORDER BY date
            ROWS BETWEEN 6 PRECEDING
            AND CURRENT ROW
        ),
        2
    ) AS moving_average_7d

FROM stock_prices

ORDER BY ticker, date;
