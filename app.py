from flask import Flask, flash,  redirect, render_template, request,  session
from flask_session import Session
from helpers import path, check
import folium
import openrouteservice
import os
from cs50 import SQL
import time
from werkzeug.security import  generate_password_hash, check_password_hash



# Configure app
app = Flask(__name__)
# app.secret_key = 'many random bytes'


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


# Login the user in
@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    # Get the user input
    EMAIL = request.form.get('email')
    PASSWORD = request.form.get('password')
    CONFIRMATION = request.form.get('confirmation')

    # IF the confirmation is not provided, therefore the user must have tried to log in
    if CONFIRMATION == None:
        # Login attempt - Check whether it's an existing user
        ROWS = db.execute('SELECT * FROM users WHERE email = ?', EMAIL)

        # Incorrect input
        if len (ROWS) != 1 or not check_password_hash(ROWS[0]['password'], PASSWORD):
            flash("We didn't recognize you")
            return redirect('/')

    # Signup the user
    else:
        # Check whether the password matches
        if PASSWORD != CONFIRMATION:
            flash("PASSWORD DOESN'T MATCH")
            return redirect('/')

        # Check if the email already exists
        if len(db.execute('SELECT * FROM users WHERE email = ?', EMAIL)) != 0:
            flash("EMAIL ADDRESS ALREADY EXISTS")
            return redirect('/')

        # Register the user
        db.execute('INSERT INTO users (email, password) VALUES (?, ?)', EMAIL, generate_password_hash(PASSWORD, method='pbkdf2:sha256', salt_length=8))

    # Store into the session
    session['email'] = EMAIL
    return redirect('/index')



# Find whether the user wants to help or wants help
@app.route('/index', methods=['GET', 'POST'])
def index():

    # Check whether the user has been logged in
    if not session.get('email'):
        return redirect('/')


    if request.method == 'GET':
        return render_template('index.html')

    REQ = request.form.get('request')
    HELP = request.form.get('help')


    # For the users coming back from wait.html
    CANCEL = request.form.get('cancel')
    SEARCH = request.form.get('search')


    if CANCEL != None:
        # The user cancelled their request
        current_request(session['coordinates'], 'CANCEL')
        return render_template('index.html')



    # For the users looking for/to  help
    if REQ != None:
        # Need help
        return redirect('/ask')

    # Ready to help others
    return redirect('/help')




# The user needs help
@app.route('/ask', methods=['GET', 'POST'])
def ask():


    # Check whether the user has been logged in
    if not session.get('email'):
        return redirect('/')


    if request.method == 'GET':
        return render_template('ask.html')

    # Get the user's origin and destination

    origin = request.form.get('origin')
    destination = request.form.get('destination')


    # Use the helper module to find out whether the data is valid
    route = path(origin, destination)

    if route == -1:
        # Flash the msg that wrong invalid location has been enterred
        flash('ERROR', 'info')
        return redirect('/ask')

    # Got back the string format of the GeoJson - convert into the dict and store the value of the key coordinates
    current_request(route, 'ask')


    # Send the coordinates to the wait function to display the map using folium
    session['coordinates'] = route

    # Redirect the user to the waiting page where they have option to cancel their request
    return redirect('/wait')




@app.route('/help', methods=['GET', 'POST'])
def help():


    # Check whether the user has been logged in
    if not session.get('email'):
        return redirect('/')


    if request.method == 'GET':
        return render_template('help.html')

    # Get the user's origin and destination
    origin = request.form.get('origin')
    destination = request.form.get('destination')

    # Use the helper module to find out whether the data is valid
    route = path(origin, destination)


    if route == -1:
        # Flash the msg that wrong  location has been enterred
        flash('ERROR', 'info')
        return redirect('/ask')

    # Sent the coordinates to current_request func where we can store the geospatial coordinates in the db
    current_request(route, 'help')


    # Send the coordinates to the wait function to display the map using folium
    session['coordinates'] = route

    # Redirect the user to the waiting page where they have option to cancel their request
    return redirect('/wait')




# Display the matched users
@app.route('/match', methods=['POST'])
def match():

    # Check whether the user has been logged in
    if not session.get('email'):
        return redirect('/')


    if request.form.get('cancel') != None:
        return index()
    # Found someone
    find_someone = const_check()

    # Match them and remove their request from db
    for person in find_someone:
        HELPERSMAIL = db.execute('SELECT email FROM users WHERE id = ?', person['helperuserid'])[0]['email']
        ASKMAIL = db.execute('SELECT email FROM users WHERE id = ?', person['askuserid'])[0]['email']
        db.execute('DELETE FROM ask WHERE askuserid = ?', person['askuserid'])
        db.execute('DELETE FROM helpers WHERE helperuserid = ?', person['helperuserid'])
        return render_template('match.html', HELP = HELPERSMAIL, ASK = ASKMAIL)



# Waiting page for the users where we will pair them with the like
@app.route('/wait', methods=['GET', 'POST'])
def wait():

    # Check whether the user has been logged in
    if not session.get('email'):
        return redirect('/')


    # Display the folium map
    if request.method == 'GET':
        # Store the coordinates for the active_user
        coordinates = session['coordinates']


        # Start point
        start = coordinates[0]

        # Stop point
        stop = coordinates[-1]

        # Get the api_key from the memory (for tmp purpose left it be in the code)
        API_KEY = os.environ.get("API_KEY")

        client = openrouteservice.Client(key=API_KEY)

        # Store the start and end coordinates
        coordinates = []
        coordinates.append(start)
        coordinates.append(stop)

        # directions
        route = client.directions(coordinates=coordinates, profile='driving-car', format='geojson')


        # The folium map needs input as lat, long unlike open route service
        begin = start
        begin.reverse()
        end = stop
        end.reverse()


        folium_map = folium.Map(location=begin, zoom_start=15)

        # add geojson to map
        folium.GeoJson(route, name='route').add_to(folium_map)


        # add marker to the origin and the destination
        folium.Marker(begin, tooltip='ORIGIN').add_to(folium_map)
        folium.Marker(end,  tooltip='DESTINATION').add_to(folium_map)

        # add layer control to map (allows layer to be turned on or off)
        folium.LayerControl().add_to(folium_map)

        # Save the map into the wait html file
        folium_map.save('templates/map.html')

        # Show waiting page while commuting the perfect match in the backend
        return render_template('wait.html')





# Display the about page
@app.route('/about')
def about():
    return render_template('about.html')


# The autogenerate map using folium
@app.route('/map')
def map():
    return render_template('map.html')

# Log the user out
@app.route('/logout')
def logout():
    session.clear()
    flash('LOGGED OUT SUCCESSFULLY.')
    return redirect('/')


# Change the password
@app.route('/changepassword', methods = ['GET', 'POST'])
def changepassword():
    if request.method == 'GET':
        return render_template('forgot.html')

    # Update the credentials of the user
    EMAIL = request.form.get('email')
    PASSWORD = request.form.get('newpassword')
    CONFIRMATION = request.form.get('newconfirmation')

    if PASSWORD != CONFIRMATION:
        flash("PASSWORD DOESN'T MATCH")
        return redirect('/')

    ROWS = db.execute('SELECT * FROM users WHERE email = ?', EMAIL)

    if len(ROWS) != 1:
        flash('No such email exists')
        return redirect('/')

    db.execute('UPDATE users SET password = ? WHERE email = ?', generate_password_hash(PASSWORD, method='pbkdf2:sha256', salt_length=8), EMAIL)
    flash('PASSWORD CHANGED.')
    return redirect('/')

'''================================================================================================================================================'''

# function for showing folium map to the waiting users
def folium_map_generate():

        # Store the coordinates for the active_user
        coordinates = session['coordinates']


        # Start point
        start = coordinates[0]

        # Stop point
        stop = coordinates[-1]

        # Get the api_key from the memory
        API_KEY = os.environ['api_key']
        client = openrouteservice.Client(key=API_KEY)

        # Store the start and end coordinates
        coordinates = []
        coordinates.append(start)
        coordinates.append(stop)

        # directions
        route = client.directions(coordinates=coordinates, profile='driving-car', format='geojson')


        # The folium map needs input as lat, long unlike ors
        begin = start
        begin.reverse()
        end = stop
        end.reverse()


        folium_map = folium.Map(location=begin, zoom_start=15)

        # add geojson to map
        folium.GeoJson(route, name='route').add_to(folium_map)


        # add marker to the origin and the destination
        folium.Marker(begin, popup="<i>Mt. Hood Meadows</i>", tooltip='origin').add_to(folium_map)
        folium.Marker(end, popup="<i>Mt. Hood Meadows</i>", tooltip='origin').add_to(folium_map)

        # add layer control to map (allows layer to be turned on or off)
        folium.LayerControl().add_to(folium_map)

        # Save the map into the wait html file
        # Since, Folium map takes input as lat, long unlike open route service
        folium_map.save('templates/map.html')
        # Store the coordinates with the start and the
        return 0




# The function accepts 2 parameters : coordinates, query(q)
def current_request(coordinates, q):

    coordinates = str(coordinates)

    ID  = db.execute('SELECT id FROM users WHERE email = ?', session['email'])[0]['id']

    if q == 'ask':
        # The user need's help - store the coordinates in the ask database
        db.execute('INSERT INTO ask (askuserid, askid, geo) VALUES (?, ?, ?)', ID, session['email'], coordinates)

    elif q == 'help':
        # The user is ready to help others - store the coordinates in the help database
        db.execute('INSERT INTO helpers (helperuserid, helperid, geo) VALUES (?,?, ?)', ID, session['email'], coordinates)

    else:
        # The user has cancelled the request - find their request and delete it from the database
        db.execute('DELETE FROM helpers WHERE helperid = ?', session['email'])
        db.execute('DELETE FROM ask WHERE askid = ?', session['email'])


def const_check():
    MATCH = check()
    if len(MATCH) != 0:
        return MATCH

    time.sleep(10)
    const_check()




