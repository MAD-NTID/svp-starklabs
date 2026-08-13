from flask import Flask, render_template, request, redirect, session, jsonify
import requests
from database import Database
from security_check import check_hacker_snippet_removed
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
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
    #if the user is not login redirect them to the login page
    if "user" not in session:
        return redirect('/login')

    #otherwise the user is already login so we send them to the dashboard page
    return redirect('/dashboard')

#This section handles the user login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    # if the user is already logged in then we skip the login page and send them to the 
    # dashboard page
    if "user" in session:
        return redirect('/dashboard')

    error = None

    #the user is not logged in so we continue the check here
    #the user is attempting to login so we need to check their username and password
    if request.method == 'POST':
        #get the username and password from what the user typed in the login form
        username = request.form['username']
        password = request.form['password']

        #we will leave this in to skip the database check, this is easy for testing and debugging
        #if this match the testing login info we skip the database
        if username =="admin" and password =="adminTesting1234":
            session['user'] = {"username": username}
            return redirect('/dashboard')

        #check the database to see if the username and password are correct
        user = database.get_user(username, password)

        # if the user is found then we store the user session and send them to the dashboard page
        if user:
            #store the session for the user so we can keep them logged in
            session['user'] = user # remove this as part of student exercise
            #send to the dashboard page
            return redirect('/dashboard')

        #user is not found
        error = database.get_last_error() or "Invalid username or password"

    return render_template('login.html', error=error)

#This section handles the dashboard page
@app.route('/dashboard', methods=['GET'])
def dashboard():
    #if the user is not login redirect them to the login page
    if "user" not in session:
        return redirect('/login')

    announcements = database.get_announcements()
    robots = database.get_robots()
    projects = database.get_projects()


    #otherwise the user is already login so we send them to the dashboard page
    return render_template('dashboard.html', announcements=announcements, robots=robots, projects=projects)

#this section logout the user and remove their session so they are no longer logged in
@app.route('/logout')
def logout():
    #remove the user session so they are logged out
    session.pop('user', None)
    return redirect('/login')

@app.route('/api/is_restored', methods=['GET'])
def is_login_restored_status():
    is_restored = False

    if not API_KEY or not API_ENDPOINT:
        return jsonify({
            "error": "Missing API configuration. Set API_KEY and API_ENDPOINT."
        }), 500

    is_restored = check_hacker_snippet_removed()

    headers = {
        'Authorization': f'Token {API_KEY}',
        'Content-Type': 'application/json'
    }
    body = {
        "card": "software_ai",
        "task": "secure_login_access",
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
        print(f"Error occurred while updating the dashboard: {e}")
        return jsonify({"error": str(e), "is_restored": False}), 502
    
    return {"is_restored": is_restored}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

