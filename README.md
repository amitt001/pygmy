Pygmy
=====

Open source easily deployable URL shortner.

Easy design. Not added a serializer.

Motivation behind this project:
===============================

Lightweight and fast.


Create User:

    curl -XPOST http://127.0.0.1:9119/api/user/1 -H 'Content-Type: application/json' -d '{
    "email": "00amit99@gmail.com",
    "f_name": "Amit",
    "l_name": "Tripathi",
    "password": "amit@123"
    }'

Get User:

Get All User Link:

Create Link:

Get Link:

How Auth Token Works:

It uses JWT. When user logs in using username and password a token is generated that is amrked as fresh and it has a time period of 30 minutes. After 30 minutes. When a request comes with the old token and new token is generated from the refresh token api. This refreshed token has a new field `fresh=False`. This new token can only shorten the url and refresh the token for further user. It CAN'T reset the password, disable the link and change the secret key of the url.

Secret: base62 of email and secret key in settings file
