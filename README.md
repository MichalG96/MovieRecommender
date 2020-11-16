# < Work in progress >

## Introduction
The idea for this project came from my master's thesis, which focused on movie recommendation algorithms. Having implemented a command line system, which allowed the users to rate the movies, and receive recommendations, I thought it will be fun to do it in a more user-friendly way, in a form of a web application

## Technologies
* Python 3.x
* Django 3.x
* HTML
* CSS
* NumPy
## Installation
1. Inside *mysite/static/* directory, create new folder, called 'private'. Inside this newly created folder, create a new file, called 'passes.txt'. This file should contain three lines:
* first line should be Django's [secret key](https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-SECRET_KEY)
* second line should contain your email
* third line should contain your email password (or your [application password](https://support.google.com/accounts/answer/185833?hl=pl))
(Unless you want to test the password reset functionality, lines 2 and 3 may contain completly bogus information)
2. Install required dependencies, by running:
```
python install -r requirements.txt
```
## Functionalities
* User authentication:
    * Registration
    * Logging in
    * Password reset via email
* All movies are displayed, they can be sorted by each column, and filtered by decades
* Searching movies by the title:

![](readme_imgs/movie_list.png)
* A user can view all of his/her rated movies, and sort them, or filter them by decade, rating, or date:

![](readme_imgs/profile.png)
* A user can add, update, and remove rating for a movie:

![](readme_imgs/rating.png)
* Movie overviews and posters are loaded from TMDb, using [TMDb API](https://developers.themoviedb.org/3/getting-started/introduction)
* A user can view information about his/her ratings:

![](readme_imgs/stats.png)


 

## Todos 
* More tests
* Enhance recommendation algorithm by using collaborative filltering
* Run recommendations in the background
* More detailed user stats (display most similar users with links to their profiles)
* Prettier CSS