import psycopg2
import sqlparse
import pandas as pd

class Connection:
    def __init__(self, database, host, user, password, port):
        self._database = database
        self._host = host
        self._user = user
        self._password = password
        self._port = port

    def create_connection(self):
        conn = psycopg2.connect(
            database = self._database,
            host = self._host,
            user = self._user,
            password = self._password,
            port = self._port
        )
        return conn
    
    def generate_table_ddl(self, table_name):
        try:
            conn = self.create_connection()
            ddl_query = f"""
                SELECT 
                    table_name, 
                    table_schema, 
                    column_name, 
                    data_type, 
                    is_nullable 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
            """
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
            if conn is not None:
                conn.close()
            return ddl

        except psycopg2.Error as e:
            print("Error connecting to PostgreSQL:", e)
            return            
            
    def query_to_df(self, query):
        try:
            conn = self.create_connection()
            df = pd.read_sql_query(query, conn)
            if conn is not None:
                conn.close()
        except psycopg2.Error as e:
            print("Error connecting to PostgreSQL:", e)
            return
        return df
    