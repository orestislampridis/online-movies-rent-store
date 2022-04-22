# Online Movies Rent Store REST API

This is a proof of concept app of an online Video Club utilizing a RESTful API. Users can register/login and perform
various requests in
order to search, rent and pay for an online movie.

The app is built using Flask. It comprises three Docker containers included in Docker-Compose which is used to deploy
the app. Gunicorn is used
as a WSGI server and NGINX as a reverse proxy. Finally, PostgreSQL is used as database.

The app also utilizes JWT authentication. Thus, to use most request the user needs to use an appropriate token.

`nginx` contains the configuration used by the nginx container

`app` contains the source code of the flask app

`tests` contains the unit tests

`docker-compose.yml` contains instructions used to build and connect the containers

`.env` contains environment variables that are passed to docker-compose


## Dataset

The dataset, located in `app\API\dataset\tmdb_5000_movies.csv` was taken from
[Kaggle](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata). It contains ~5,000 movies and after appropriate
data cleaning and transformations, it is used to populate the database.

## Install

First, please use git clone to get a copy of the repo:

    git clone https://github.com/orestislampridis/online-movies-rent-store.git

## Run the app

After ensuring you have the latest Docker version installed, enter the cloned dir and simply run:

    docker-compose up --build -d

## Run the tests

Go inside the tests dir and run the following:

    pip install unittest
    pip install requests
    python test_unittest_api.py    

# REST API

The REST API to the app is documented in detail below.

## Create a new account

### Request

`Post http://127.0.0.1/create_user`

### Body Example

    {
        "email": "john@email.com",
        "password": "1234",
        "first_name": "john",
        "last_name": "marston"
    }

### Success-Response

    HTTP 201 CREATED
    {
        "message": "User successfully created!",
        "ok": true
    }

### Error 4xx

    HTTP 400 BAD REQUEST
    {
        "message": "Current email already exists!",
        "ok": False
    }

    HTTP 400 BAD REQUEST
    {
        "message": "email and / or password is missing",
        "ok": False
    }

## Login

### Request

`Post http://127.0.0.1/login`

### Body Example

    {
        "email": "john@email.com",
        "password": "1234"
    }

### Success-Response

    HTTP 201 CREATED
    
    {
        "ok": true,
        "token": "eJiOiOiJ1J9.ey1c22zh9.03Pbp-fbj7rZWPCy-rY2Da74FE"
    }

### Error 4xx

    HTTP 400 BAD REQUEST
    {
        "message": "email and / or password is missing",
        "ok": False
    }

    HTTP 403 FORBIDDEN
    {
        "message": "Could not verify. Incorrect password given",
        "ok": False
    }

    HTTP 404 NOT FOUND
    {
        "message": "User does not exist",
        "ok": False
    }

## Get list of all available movies

### Request

`GET http://127.0.0.1/get_all_movie_titles`

### Header

| Key              | Value    | Description                  |
|:-----------------|:---------|:-----------------------------|
| `x-access-token` | `string` | **Required**. Your JWT token |

### Success-Response

    HTTP 200 OK
    
    {
    "movies": [
        {
            "movie_id": 0,
            "title": "Avatar"
        },
        {
            "movie_id": 1,
            "title": "Pirates of the Caribbean: At World's End"
        },
        ...
        ]
    }

## Get list of available movies based on category

### Request

`GET http://127.0.0.1/get_movies_by_category?category=History`

### Header

| Key              | Value    | Description                  |
|:-----------------|:---------|:-----------------------------|
| `x-access-token` | `string` | **Required**. Your JWT token |

### Parameters

| Key        | Value    | Description                 |
|:-----------|:---------|:----------------------------|
| `category` | `string` | Category/genre of the movie |

### Success-Response

    HTTP 200 OK
    
    {
    "movies": [
        {
            "movie_id": 109,
            "title": "Pearl Harbor"
        },
        {
            "movie_id": 111,
            "title": "Alexander"
        },
        ...
        ]
    }

### Error 4xx

    HTTP 400 BAD REQUEST
    {
        "message": "Category parameter is missing",
        "ok": False
    }

    HTTP 404 NOT FOUND
    {
        "message": "Genre does not exist",
        "ok": False
    }

## Navigate and get the details/info of a specific movie

### Request

`GET http://127.0.0.1/navigate?title=Pulp+Fiction`

### Header

| Key              | Value    | Description                  |
|:-----------------|:---------|:-----------------------------|
| `x-access-token` | `string` | **Required**. Your JWT token |

### Parameters

| Key     | Value    | Description                             |
|:--------|:---------|:----------------------------------------|
| `title` | `string` | Title of the movie. Add '+' for spaces. |

### Success-Response

    HTTP 200 OK
    
    {
        "budget": "$8,000,000",
        "genres": "Thriller,Crime",
        "original_language": "en",
        "original_title": "Pulp Fiction",
        "overview": "A burger-loving hit man, his philosophical partner, ...
        "popularity": 121.463076,
        "release_date": "1994-10-08",
        "revenue": "$213,928,762",
        "runtime": "154 minutes",
        "title": "Pulp Fiction",
        "vote_average": 8.3,
        "vote_count": 8428
    }

### Error 4xx

    HTTP 400 BAD REQUEST
    {
        "message": "Title parameter is missing",
        "ok": False
    }

    HTTP 404 NOT FOUND
    {
        "message": "Movie does not exist",
        "ok": False
    }

## Rent a specific movie

### Request

`POST http://127.0.0.1/rent`

### Header

| Key              | Value    | Description                  |
|:-----------------|:---------|:-----------------------------|
| `x-access-token` | `string` | **Required**. Your JWT token |

### Body Example

    {
        "title": "Pulp Fiction"
    }

### Success-Response

    HTTP 200 OK
    
    {
        "message": "Pulp Fiction successfully rented!",
        "ok": true
    }

### Error 4xx

    HTTP 400 BAD REQUEST
    {
        "message": "Body title is missing",
        "ok": False
    }

    HTTP 400 BAD REQUEST
    {
        "message": "You are already renting this movie!",
        "ok": False
    }

    HTTP 404 NOT FOUND
    {
        "message": "Movie does not exist",
        "ok": False
    }

## Return a specific movie

### Request

`POST http://127.0.0.1/return_movie`

### Header

| Key              | Value    | Description                  |
|:-----------------|:---------|:-----------------------------|
| `x-access-token` | `string` | **Required**. Your JWT token |

### Body Example

    {
        "title": "Pulp Fiction"
    }

### Success-Response

    HTTP 200 OK
    
    {
        "message": "Pulp Fiction (rental id: 1) successfully returned!",
        "ok": true
    }

### Error 4xx

    HTTP 400 BAD REQUEST
    {
        "message": "Body title is missing",
        "ok": False
    }

    HTTP 404 NOT FOUND
    {
        "message": "You have not rented this movie!",
        "ok": False
    }

    HTTP 404 NOT FOUND
    {
        "message": "Movie does not exist",
        "ok": False
    }

## Get all rentals made by current user

Note: Contains both paid and unpaid rentals

### Request

`GET http://127.0.0.1/get_rentals`

### Header

| Key              | Value    | Description                  |
|:-----------------|:---------|:-----------------------------|
| `x-access-token` | `string` | **Required**. Your JWT token |

### Success-Response

    HTTP 200 OK
    
    {
    "rentals": [
        {
            "date_end": "Thu, 21 Apr 2022 00:00:00 GMT",
            "date_start": "Thu, 21 Apr 2022 00:00:00 GMT",
            "movie_id": 2573,
            "paid": true,
            "rental_id": 1,
            "user_id": 1
        },
        ...
        ]
    }

## Get the charge (“amount of money owed”) based on days

Note: This is calculated by adding up the charge of all the movies the current
user has not returned yet. The user is charged 1 euro per day for the first three days and 0,5 euro per
day for the days after the first three.

### Request

`GET http://127.0.0.1/get_charge`

### Header

| Key              | Value    | Description                  |
|:-----------------|:---------|:-----------------------------|
| `x-access-token` | `string` | **Required**. Your JWT token |

### Success-Response

    HTTP 200 OK
    
    {
        "charge": "€1.0"
    }

