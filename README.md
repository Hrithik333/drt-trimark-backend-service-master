# DRT Trimark Backend Service

To use any API,
Start the service, and open postman and use the following:

URL: http://localhost:1125/login

Body: {
    "email": "amarnath.tangudu@aniccadata.com",
    "password": "Amar@1995"
}

Copy the "token" value from the response.

While hitting the API, in the headers add the following:

x-access-tokens: "the token that we got from the first step"

and then hit the request.ok