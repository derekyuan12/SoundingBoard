SOUNDING BOARD DESIGN DOCUMENT

!!!! LINK TO FORMATTED DESIGN DOCUMENT: https://docs.google.com/document/d/1x4kgT2TlYOJlZ3YddKyFmAW8HSxdluiANYUO3vFtqyc/edit?usp=sharing (way prettier and easier to read :D)

CONTENTS:
I. INTRODUCTION
II. STYLE
III. ACCESSING THE WEBSITE
IV. PLAYING AND RECORDING SOUNDS
V. DOCUMENTING PLAY HISTORY
VI. SOCIAL
VII. PROFILE

I. INTRODUCTION
Overall, we used Python, Flask, HTML, CSS and Javascript to implement this web application. Flask and Javascript were used for the more function based processes, whereas HTML created the structure of the website and CSS determined the style of the website. 

II. STYLE
Stylistically, we wanted our page to be clean and minimalistic, but we wanted it to revolve around a centralized color scheme. To achieve this, we created a SoundingBoard logo, which you can see in the top left corner, a SoundingBoard banner style logo which is featured on the home page, and a new favicon for the website displayed in browser tabs. The main SoundingBoard logo features 5 colors as the buttons spelling out BOARD. In order to integrate this aesthetically with the rest of the website, the 5 main pages — Home, Soundboard, Play History, Social, and Audio  — each feature a banner at the top that is colored in one of those 5 colors, in order of appearance. 

III. ACCESSING THE WEBSITE
Register
Our registration page has a form in the html side, which delivers data through a post request to our server. Then, in app.py, we have checks in place that ensure the username and email address have been filled out and are not already taken, also making sure that the passwords are filled out and match. It then inserts this information into the users table in our database. We have additionally taken care to ensure the password is stored as a hash in order to prevent security issues. We then use Javascript to send an email to the specified email address confirming that the account has been created. We then send the user to the registered.html page which displays a confirmation message for registration.

Log In
The log in page is also a HTML form that delivers data through a POST request to the server. In app.py, we have checks to make sure that the username and password hash combination match that of an existing user in the database. 

Home
In order to access most of the website, the user must be logged in which we ensured through the @login_required decorator before most of the routes in the page. In the home page, we also display a welcome message that passes in the current user’s username in order to personalize the experience. We also have a SQL query that determines which sound has been played the most in the entire history of the website, among all users. We passed username into all of the pages separately because it would have been impossible to create a global variable for username (until the user had already logged in). Session user ID necessarily requires the @login_required decorator function, meaning the user must already be logged in for the user ID to exist.

IV. PLAYING AND RECORDING SOUNDS
In order to create a button for every potential sound, we passed the sounds SQL table into soundboard.html and then used Jinja syntax to loop through every sound, creating a button for each one in the process. This way, we wouldn’t have to hard code any specific sounds as buttons into the website. Then, we wrote code such that when the button is clicked, the specified audio plays. Since SQL databases can’t store audio files efficiently or well, we devised a workaround, storing the file pathway or location of the audio file in the sounds SQL table, instead of attempting to store the audio file itself. That way, when we reference the audio file, we reference its location instead of the actual file, which has the same effect.

The website comes with pre-uploaded sounds that have already been inserted into the SQL sounds table. However, users also have the option to upload sounds of their own. To do this, we created a form in ‘audio.html’ that allows a file to be uploaded and a name to be inputted, which is sent via a post request to a function called ‘uploaded’ in app.py. Then, within this uploaded function, we save the file into the static folder, using f.save, os.path.join, and a specified path to the static folder. Then, we run a SQL query that inputs the name of the sound and the file location into the sounds table, before inputting the sound table into render_template and going back to soundboard.html to display the soundboard with the new sound added.

V. DOCUMENTING PLAY HISTORY

For play history, we wanted a table that would display the name of the sound played as well as the date and time of the play for each time a sound button was pressed on the soundboard. Thus, within app.py in the soundboard function, because the id and value of the button clicked was written to be the same as the name of the sound in our database, we could, in our app.py for POST requests, find the value of the button clicked. Then, using this, we found the sound_id related to that sound and inputted both that and the user id into the plays SQL table. As a side note, we then used this updated plays SQL table to run SQL queries to determine the most played song of the current user, the number of times that most played song occurred in the plays table for the current user, and the last played song of the current user. We later display this information in the profile section, where it is actually used, but we update this information each time a sound is clicked.

Then, to actually display the play history, we run a SQL query on the plays table to select the name and date_time elements from all the rows in the table, organized in descending order of date_time, which means the last played element is listed first. Then, we pass the resultant list of dicts into the render_template for the history.html page. In this page, we then loop through each dict in this list, displaying in a table both the properties for each click in one row.

VI. SOCIAL

Again, we passed a list of dicts into render_template for our social page. Specifically, each of these dicts corresponded to one of the existing user’s data from the table users, which we obtained through a SELECT SQL query in app.py of all the information in the users table. Then, we looped through this list in the social.html page so that a row in the table on that webpage would display the relevant characteristics for each valid user.

Through the social page, users can also see each others’ public profiles by clicking on the username, which we made into buttons with the value of the username, in the table. Then, with a POST request and a SQL query, we selected the information from the users table for the user with that specified username. We then passed that information into render_template into the “otherprofile.html” page, which is displays the most played sound, bio, email, and last played sound of the selected user to any user who clicks on the page.

VII. PROFILE

For our profile page, we accessed the most played sound from before. We also had a textarea place where users can input the bio, which we updated with a POST request and an addition to the bio property in the users table in app.py. We also have a dropdown menu through which users can select their favorite sound, and then this also gets updated in the users table through app.py. We wanted to have these values associated with the user in the table so that they can be referenced in multiple places throughout the website. We had to place a condition to make sure that they only updated each value if something was inputted through the form because otherwise if only the bio but not the favorite sound was changed for example, the favorite sound through the post request would be updated to be None.

Changing Password
To change the password, we have a HTML form that has space for the current password and new password (and a confirmation of the new password). We have flask code that makes sure that these inputs are not blank, that the current password is correct, and that the new password and its confirmation match. If this is true, then the user table is updated with the new password through a SQL query.

Changing Email
To change the email, we have a HTML form that has space for a current email and a new email. Through app.py, we confirm that the current email is accurate and that the new emails match. Then, we use Javascript to send a confirmation email to the old email that the email has now been changed. If this all works, then the user table is updated with the new email through a SQL query.


