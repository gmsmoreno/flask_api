## Authentication and Query on Farms

This API works as follows:

The user passes a JSON with user key and password through the POST method, a request is made to access the PostgreSQL database via the /login route.

Post response with the Postman API client:

![image info](https://github.com/gmsmoreno/flask_api/blob/main/flask_apicar/login.png)

If you successfully log in and access the session, it is possible to apply a query using the GET method and check environmental overlap information for the CAR of interest.

This farm intersects with government bases, such as: quilombola areas, conservation units, indigenous lands, settlements, embargoes and INPE deforestation.

Get response with the Postman API client:

![image info](https://github.com/gmsmoreno/flask_api/blob/main/flask_apicar/query.png)

Finally, the user can log out of the session:

Get response with the Postman API client:

![image info](https://github.com/gmsmoreno/flask_api/blob/main/flask_apicar/logout.png)

In this API it is possible to cross-reference geospatial information with PostGIS tools from the PostgreSQL database.
VIEWs are generated that do not allocate memory in the system and the query takes place ON-DEMAND, the entire process of checking for overlapping environmental irregularities on the farm is done at the time of the request. Through the session carried out in the Flask framework, it is possible to create an encrypted authentication and then validate it with the user's registration in the database.

If the user tries to GET the query followed by the logout request. The 401 unauthorized status will appear in response.

![image info](https://github.com/gmsmoreno/flask_api/blob/main/flask_apicar/unauthorized.png)

The information consulted is in the following order:

CAR code,
situation of the rural property,
rural property area,
detection of deforestation on the farm perimeter,
overlapping conservation unit,
overlapping embargoes,
overlapping indigenous lands,
overlapping settlements,
overlapping quilombola areas,
County,
State.