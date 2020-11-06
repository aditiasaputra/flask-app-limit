# Flask App with Limit (Rest API)

This project is a simple Rest API with Flask, Redis, and MongoDB. This project is still in development.

Step by step for running this application:

1. Install virtual environment (like: `pipenv` & `virtualenv`). This project use `virtualenv`
2. Create environment with command `virutalenv myenv` and enter
3. Activate environment with `source myenv/bin/activate` and enter
4. Install pip package with command `pip install -r requirements.txt`
5. Config `.env` file to connect with database and JWT for authentication
6. And run application with command `flask run`

To consume API, you can request an on-base URL endpoint and you get a `token` to request other endpoints.

For instance:

> Request
`GET` [http://localhost:5000](http://localhost:5000)
> Response
`{
    "IP_info": "127.0.0.1 - 2020-11-06 22:40:58 - GET /",
    "hit_count": 1,
    "message": "Hello world",
    "token": "abc123"
}` STATUS 200 (OK)

Request to api endpoint
> Request
`GET` [http://localhost:/api](http://localhost:5000/api)
> Response
`{
    "IP_info": "127.0.0.1 - 2020-11-06 23:18:46 - GET /api 200",
    "current_user": "Hello",
    "hit_count": 1,
    "message": "Hello world from api"
}` STATUS 200 (OK)

This request setting with a limit of 3 per day. If too many requests, you get a response status 429
> `{
    "code_status": "429",
    "error": "Too much request! Rate limit exceeded 3 per 1 day",
    "hit_count": 3
}` STATUS 429 (TOO MANY REQUESTS)
