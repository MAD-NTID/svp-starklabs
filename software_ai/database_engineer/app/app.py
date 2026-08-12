from flask import Flask, render_template, request, redirect, session
from database import Database
import requests
import os

app = Flask(__name__)
API_KEY = os.getenv('API_KEY')
API_ENDPOINT = os.getenv('API_ENDPOINT')


#setting up the database connection
database = Database(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)


#user visit the home page (index page)
@app.route('/')
def home():
    return render_template('index.html', database_host=os.getenv('DB_HOST'))

@app.route('/api/database/ping', methods=['GET'])
def get_database_ping_status():
    port = 3306 
    headers = {
        'Authorization': f'Token {API_KEY}',
        'Content-Type': 'application/json'
    }
    body = {
        "host": os.getenv('DB_HOST'),
        "port": port
    }

    try:
        response = requests.post(API_ENDPOINT+"/check/", headers=headers, timeout=5, json=body)
        return response.json()
    except requests.RequestException as e:
        print(f"Error occurred while pinging the database: {e}")
        return {"error":e}

    # return {
    #     "ok": True,
    #     "port": port,
    #     "reachable": True,
    #     "response_time_ms":42
    # }

@app.route('/api/database/exists', methods=['GET'])
def get_database_exists_status():
    exists = database.has_database()
    return {"exists": exists}


@app.route('/api/database/tables', methods=['GET'])
def get_database_tables():
    tables = database.get_database_tables()
    if tables is not None:
        tables = [list(table.values())[0] for table in tables]
    else:
        tables = []

    return {"tables": tables}

@app.route('/api/database/row_counts', methods=['GET'])
def get_database_row_counts():
    row_counts = database.count_database_rows_from_all_tables()
    return {"row_counts": row_counts}


    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

