from flask import Flask, render_template, request, redirect, session, jsonify
from database import Database
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
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
    if not API_KEY or not API_ENDPOINT:
        return jsonify({
            "error": "Missing API configuration. Set API_KEY and API_ENDPOINT."
        }), 500

    port = 3306
    headers = {
        'Authorization': f'Token {API_KEY}',
        'Content-Type': 'application/json'
    }
    body = {
        "host": os.getenv('DB_HOST'),
        "port": port
    }

    endpoint = f"{API_ENDPOINT.rstrip('/')}/check/"

    try:
        response = requests.post(endpoint, headers=headers, timeout=5, json=body)
        response.raise_for_status()
        try:
            payload = response.json()
        except ValueError:
            payload = {"raw_response": response.text}

        return jsonify(payload), response.status_code
    except requests.RequestException as e:
        print(f"Error occurred while pinging the database: {e}")
        return jsonify({"error": str(e)}), 502

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

@app.route('/api/database/is_restored', methods=['GET'])
def get_database_is_restored_status():
    tables = database.get_database_tables()
    if tables is not None:
            tables = [list(table.values())[0] for table in tables]
    else:
        tables = []

    if tables is not None and len(tables) >= 5:
        is_restored = True
    else:
        is_restored = False

    if is_restored:
        row_counts = database.count_database_rows_from_all_tables()
        if row_counts is not None and row_counts >= 23:
            is_restored = True
        else:
            is_restored = False

    if not API_KEY or not API_ENDPOINT:
        return jsonify({
            "error": "Missing API configuration. Set API_KEY and API_ENDPOINT."
        }), 500

    headers = {
        'Authorization': f'Token {API_KEY}',
        'Content-Type': 'application/json'
    }
    body = {
        "card": "software_ai",
        "task": "restore_db",
        "complete": is_restored
    }

    # Skip external update when restore state is unchanged for this session.
    if session.get("restore_last_state") == body:
        return jsonify({
            "cached": True,
            "message": "State unchanged. Skipped external task update API call.",
            "is_restored": is_restored,
            "data": session.get("restore_last_response")
        }), session.get("restore_last_status", 200)

    endpoint = f"{API_ENDPOINT.rstrip('/')}/task/update/"

    try:
        response = requests.post(endpoint, headers=headers, timeout=5, json=body)
        response.raise_for_status()
        try:
            payload = response.json()
        except ValueError:
            payload = {"raw_response": response.text}

        session["restore_last_state"] = body
        session["restore_last_response"] = payload
        session["restore_last_status"] = response.status_code

        return jsonify(payload), response.status_code
    except requests.RequestException as e:
        print(f"Error occurred while pinging the database: {e}")
        return jsonify({"error": str(e), "is_restored": False}), 502
    
    return {"is_restored": is_restored}
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

