
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

    def get_user(self, username, password):
        query = "SELECT * FROM interns WHERE username = %s AND password = %s"
        params = (username, password)
        return self.execute_query(query, params, fetch_mode='one')

    def get_all_users(self):
        query = "SELECT * FROM interns"
        return self.execute_query(query, fetch_mode='all')

    def get_announcements(self):
        query = "SELECT * FROM announcements ORDER BY posted_date DESC"
        return self.execute_query(query, fetch_mode='all')

    def get_projects(self):
        query = "SELECT * FROM projects"
        return self.execute_query(query, fetch_mode='all')

    def get_robots(self):
        query = "SELECT * FROM robots"
        return self.execute_query(query, fetch_mode='all')

    def get_last_error(self):
        return self.last_error


# # Test
# if __name__ == "__main__":
#     db = Database(host="127.0.0.1", user="root", password="topSecretPassword#1!", database="starklab_portal")
#     users = db.get_all_users()
#     print(users)
#     announcements = db.get_announcements()
#     print(announcements)
#     projects = db.get_projects()
#     print(projects)
#     robots = db.get_robots()
#     print(robots)


    


    