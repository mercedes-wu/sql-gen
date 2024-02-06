SELECT products.name,
       SUM(sales.quantity * product_suppliers.supply_price) AS revenue
FROM sales
INNER JOIN products ON sales.product_id = products.product_id
INNER JOIN product_suppliers ON products.product_id = product_suppliers.product_id
WHERE sales.sale_date > '2020-01-01'
GROUP BY products.name
ORDER BY revenue DESC