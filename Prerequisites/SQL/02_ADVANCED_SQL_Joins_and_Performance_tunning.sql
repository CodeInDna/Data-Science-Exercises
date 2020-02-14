 /*
Write a query with FULL OUTER JOIN to see:
- each account who has a sales rep and each sales rep that 
has an account (all of the columns in these returned rows 
will be full)
- but also each account that does not have a sales rep and 
each sales rep that does not have an account (some of the 
columns in these returned rows will be empty)
*/
SELECT *
  FROM accounts
 FULL JOIN sales_reps ON accounts.sales_rep_id = sales_reps.id


SELECT o.id,
o.occurred_at as order_date,
we.*
FROM orders o
LEFT JOIN web_events we
ON we.account_id = o.account_id
AND we.occurred_at < o.occurred_at
WHERE DATE_TRUNC('month', o.occurred_at) = 
(SELECT DATE_TRUNC('month', MIN(orders.occurred_at))
FROM orders)
ORDER BY o.account_id, o.occurred_at;

-- The primary point of contact's full name comes before the sales representative's name alphabetically
-- All entries from left table but entries from the right table would be as written in the above statement.
SELECT accounts.name as account_name,
       accounts.primary_poc as poc_name,
       sales_reps.name as sales_rep_name
  FROM accounts
  LEFT JOIN sales_reps
    ON accounts.sales_rep_id = sales_reps.id
   AND accounts.primary_poc < sales_reps.name


-- Appending Data via UNION
/*
Write a query that uses UNION ALL on two instances (and selecting
all columns) of the accounts table. 
*/
SELECT *
FROM accounts

UNION ALL

SELECT * 
FROM accounts;

/*
Add a WHERE clause to each of the tables that you unioned in the 
query above, filtering the first table where name equals Walmart 
and filtering the second table where name equals Disney.
*/
SELECT *
FROM accounts
WHERE name='Walmart'

UNION ALL

SELECT * 
FROM accounts
WHERE name='Disney'


/*
Perform the union in your first query (under the Appending Data via 
UNION header) in a common table expression and name it double_accounts. 
Then do a COUNT the number of times a name appears in the 
double_accounts table. If you do this correctly, your query results 
should have a count of 2 for each name.
*/
WITH double_accounts as (SELECT *
FROM accounts

UNION ALL

SELECT * 
FROM accounts)

SELECT
name,
COUNT(*)
FROM double_accounts
GROUP BY name;