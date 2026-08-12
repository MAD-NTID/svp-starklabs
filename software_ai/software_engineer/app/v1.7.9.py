from flask import Flask, render_template, request, redirect, session
from database import Database
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')


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
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

