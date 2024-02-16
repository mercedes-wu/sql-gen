import psycopg2
import sqlparse
import pandas as pd

class Query:
    def __init__(self, database, host, user, password, port):
        _database = database
        