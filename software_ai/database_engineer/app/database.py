
import pymysql


class Database:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.last_error = None

    def connect(self):
        try:
            connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=pymysql.cursors.DictCursor
            )
            return connection
        except pymysql.MySQLError as e:
            self.last_error = f"Error connecting to the database: {e}"
            print(self.last_error)
            return None

    def execute_query(self, query, params=None, fetch_mode = 'all'):
        connection = self.connect()
        if connection is None:
            return None

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                if fetch_mode == 'all':
                    result = cursor.fetchall()
                elif fetch_mode == 'one':
                    result = cursor.fetchone()
                else:
                    result = None
            #connection.commit()
            return result
        except pymysql.MySQLError as e:
            self.last_error = f"Error executing query: {e}"
            print(self.last_error)
            return None
        finally:
            connection.close()

    def has_database(self):
        connection = self.connect()
        if connection is None:
            return False

        return True

    def get_database_tables(self):
        query = "SHOW TABLES"
        return self.execute_query(query, fetch_mode='all')

    def count_database_rows_from_all_tables(self):
        tables = self.get_database_tables()
        if tables is None:
            return 0

        total_rows = 0
        for table in tables:
            table_name = list(table.values())[0]
            query = f"SELECT COUNT(*) AS row_count FROM {table_name}"
            result = self.execute_query(query, fetch_mode='one')
            print(f"Table: {table_name}, Row Count: {result['row_count'] if result else 'Error'}")
            if result is not None:
                total_rows += result['row_count']

        return total_rows
