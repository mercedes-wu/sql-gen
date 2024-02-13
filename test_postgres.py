import psycopg2
import sqlparse
import pandas as pd

def generate_table_ddl(conn, table_name):
    ddl_query = f"SELECT table_name, table_schema, column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = '{table_name}'"
    with conn.cursor() as cursor:
        cursor.execute(ddl_query)
        columns = cursor.fetchall()

    ddl = f"CREATE TABLE {table_name} (\n"
    for column in columns:
        column_name = column[2]
        data_type = column[3]
        is_nullable = column[4]
        ddl += f"    {column_name} {data_type}"
        if is_nullable == 'NO':
            ddl += " NOT NULL"
        ddl += ",\n"
    ddl = ddl[:-2]  # Remove the trailing comma and newline
    ddl += "\n);"
    
    return ddl

try:
    # Connect to your PostgreSQL database
    conn = psycopg2.connect(database="app",
                        host="db",
                        user="app_user",
                        password="app_password",
                        port="5432")

    query = """
    SELECT SUM(c.number_of_orders) AS total_orders
    FROM analytics.customers c
    WHERE c.first_name ILIKE '%Michael%'
        AND c.last_name ILIKE '%P%';
    """
    df = pd.read_sql_query(query, conn)
    print(df)
    
    # Generate DDL for a specific table
    table_name = "customers"
    ddl = generate_table_ddl(conn, table_name)
    # print(ddl)

except psycopg2.Error as e:
    print("Error connecting to PostgreSQL:", e)
finally:
    if conn is not None:
        conn.close()



