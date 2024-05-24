# FLASK API Authenticator
Flask API integration with PostgreSQL database

The purpose of this API is to generate an encrypted password in the database using the werkzeug.security lib in python. With this, we can record a the user and password in the table that will need to be authenticated in the system. Through the "/login" route we pass a json with user and password keys and send the request through the POST method. The backend retrieves records from the user and password columns in a table in the PostgreSQL database. If the encryption checked is the same, login to the system is returned. In case of hash difference, a bad request status (400) of invalid credential or password is returned.

Post response with the Postman API client:

![image info](https://github.com/gmsmoreno/flask_api/blob/main/flask_apiaut/logado.png)

To exit the session, simply pass the /logout route as the GET method. This route will log out of the ongoing session.

Get response with the Postman API client:

![image info](https://github.com/gmsmoreno/flask_api/blob/main/flask_apiaut/deslogado.png)

The main route confirms whether you are logged in by returning the username and password or whether you do not have access to the session via status 401 (unauthorized).

Get response with the Postman API client:

![image info](https://github.com/gmsmoreno/flask_api/blob/main/flask_apiaut/usuario_logado.png)

![image info](https://github.com/gmsmoreno/flask_api/blob/main/flask_apiaut/nao_autorizado.png)

