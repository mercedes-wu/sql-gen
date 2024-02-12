import psycopg2
import sqlparse
import pandas as pd

conn = psycopg2.connect(database="app",
                        host="db",
                        user="app_user",
                        password="app_password",
                        port="5432")

query = "select * from analytics.customers"

df = pd.read_sql_query(query, conn)

print(df)