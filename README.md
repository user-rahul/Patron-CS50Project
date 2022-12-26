# **PATRON**
> Patron is a web application where one can ask for lift. The goal is to serve as a platform that makes it easier for  people to  move  across the places without any worry for resources. In layman's term, it is a platform where one can ask for lift.

## **For video demo** [click here](https://www.youtube.com/watch?v=IZOCvviNcQA)
#
## **Tools Used**

* [FLASK](https://flask.palletsprojects.com/en/2.1.x/)
* [SQLITE3](https://www.sqlite.org/index.html)
* [OPENROUTESERVICE](https://openrouteservice.org/)
* [FOLIUM](https://python-visualization.github.io/folium/)
#
## **FILES**
#
  Patron helpers.py, app.py *(for backend)*, project.db *(for database)* as well as few html pages along with stylesheets and scripts.
  * **HTML PAGES :**
    1. layout *(The basic template which will be used by other page using jinja)*.
    2. about *(It will be used to describle about us and our work)*.
    3. ask & help *(Prompt route)*.
    4. forgot *(It will be used to let user change their password)*.
    5. index *(The main page where one can request some-one or help some-one)*.
    6. map *(Auto generate by folium which is then send to wait)*.
    7. wait *(Confirm their request while searching the perfect-match in the backend)*.
    8. match *(If found a perfect-match display credentials)*.

  * **CSS PAGES :**
    1. index *(basic stylesheet for templating all the other pages)*.
    2. register *(few add-ons such as form for registering the user in)*.
    3. styles *(Main page for users to decide whether they want help or want to help)*.

  * **JAVASCRIPT FILES :**
    1. index *(For the basic animations along the pages)*
    2. register *(For signup / login)*

#
### **DESCRIPTION**
#
Users can register using their email id and password. Then, the input is passed to the flask file to check if the input is valid or not. If the input is valid, then the email is loaded into the database along with hashed password (using werkzeug.security).

         # Check if the email already exists
        if len(db.execute('SELECT * FROM users WHERE email = ?', EMAIL)) != 0:
            flash("EMAIL ADDRESS ALREADY EXISTS")
            return redirect('/')

        # Register the user
        db.execute('INSERT INTO users (email, password) VALUES (?, ?)', EMAIL, generate_password_hash(PASSWORD, method='pbkdf2:sha256', salt_length=8))

Then, the user is redirected to the index page where they get two options i.e., request someone for help, help someone who requests.

CASE 1 (HELP SOMEONE):
 If clicked on the help button, the user is redirected to the page where they are prompted for their origin(from where) and destination(to where) locations. Once, enterred , the data is sent to the geopy library which convert the locations to the longitude and latitude.

    geolocator = Nominatim(user_agent="helpers.py")
    startLoc = geolocator.geocode(origin)
    endLoc = geolocator.geocode(destination)

    if startLoc is None or endLoc is None:
        return -1

    start_latitude = startLoc.latitude
    start_longitude = startLoc.longitude

    end_latitude = endLoc.latitude
    end_longitude = endLoc.longitude
 Then the long and lat is sent to the openrouteservice API which outputs the directions from
 the origin to the destinations in the form of longitude and latitude. This output is used to generate map using folium and is added to the database.

 CASE 2 (ASK SOMEONE):
 If clicked on the ask button, the user is redirected to the page where they are prompted for their origin
 and destination location and the process repeats as in the CASE 1.

 BACKEND STUFF:
 Using time library in python, a function is repeated after every few seconds which check if there atleast one person in the help table (in the database) who is going through same path or superpath of a person in the ask table (in the database). If that exists, then they are matched and connected.

#
### **REQUIREMENTS**
#
  * Download all the files and folders from my github account.
  * To run the project, all you have to do is type "flask run" in your terminal window our your editor.
  * You are good to go now.

#
### **DIRECTIONS TO USE IT**
#
* First register your account by going into the signup account.
* Click on help / ask button according to your requirements.
* Enter the required credentials.
* To logout, click on the setting icon in the vertical navbar present in the index page.



