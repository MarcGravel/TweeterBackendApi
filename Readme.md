# Tweeter API

Tweeter API allows users to access multiple endpoints and perform basic CRUD requests based on specific endpoints and data passed. This API is currently under construction and not deployed.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install.

```bash
click==8.0.1
colorama==0.4.4
decorator==5.1.0
Flask==2.0.2
Flask-Cors==3.0.10
itsdangerous==2.0.1
Jinja2==3.0.2
mariadb==1.0.7
MarkupSafe==2.0.1
six==1.16.0
validators==0.18.2
Werkzeug==2.0.2
```

# Usage

## User Login: /api/login
The login end point supports only the POST and DELETE methods.


### POST
HTTP success code: 201

POST will log a user in if the username / password combo match.
Return data contains confirmation information about the user as well as a login token
An error will be returned if the login information is invalid.
Client can send either username OR email along with the password for login validation

```json
Example Data:

JSON Data Sent:
    { 
      "email": "example@gmail.com",
      "password": "anypass123"
    }

JSON Data Returned: 
    { 
        "userId": 23,
        "email": "example@gmail.com",
        "username": "TheUser",
        "bio": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
        "birthdate": "1993-07-26",
        "loginToken": "LIAbfvh341uNAS314",
        "imageUrl": null,
        "bannerUrl": "https://i.picsum.photos/id/223/1080/640.jpg?hmac=1zRXJhkXy6EdeYC-WYatZnnmpkqINeYTiJ4-74E6t1o"
    }
    
```
### DELETE
HTTP success code: 204

DELETE will destroy the login token
An error will be returned if the loginToken is invalid
No data returned
```json
Example Data:

JSON Data Sent:
    { 
      "loginToken": "LIAbfvh341uNAS314"
    }

No Data Returned
```

## Users: /api/users
The login end point supports GET, POST, PATCH and DELETE methods.

### GET
HTTP success code: 200

GET will send all users information OR only a specific users information.
For all users, make a request with no params. If you want a specific users info, send the user id.
The value for bannerUrl and imageUrl will either contain the URL of their profile image or null if the user has no images.
An error will be returned if a userId does not exist.
```json
Example Data:

JSON Params Sent:
    { 
      "userId": 1 
    }

JSON Data Returned: 
    [
      { 
          "userId": 1,
          "email": "grinch@suess.com",
          "username": "TheGrinch",
          "bio": "There will be no holly, jolly, christmas!",
          "birthdate": "1988-04-07",
          "imageUrl": null,
          "bannerUrl": "https://i.picsum.photos/id/223/1080/640.jpg?hmac=1zRXJhkXy6EdeYC-WYatZnnmpkqINeYTiJ4-74E6t1o"
      }
    ]
```

### POST
HTTP success code: 201
POST will create a new user if no conflicting current user
When sending valid data about user, you are sent back conformation information about the new user. Along with a loginToken
Optional data to send over: imageURL and bannerURL. 
Required data to send over: email, username, password, bio and birthdate
An error will be returned if a username or email already exists.

```json
Example Data:

JSON Data Sent:
    { 
      "email": "CindyLou@suess.com",
      "username": "CindyLou",
      "password": "IStoleChristmas",
      "bio": "I just want everyone to be together on christmas.",
      "birthdate": "1993-07-26",
      "imageUrl": "https://unsplash.com/photos/DCVMd_NOpro/download?force=true&w=640",
      "bannerUrl": "https://i.picsum.photos/id/223/1080/640.jpg?hmac=1zRXJhkXy6EdeYC-WYatZnnmpkqINeYTiJ4-74E6t1o"
    }

JSON Data Returned: 
    { 
        "userId": 23,
        "email": "cindyLou@suess.com",
        "username": "CindyLou",
        "bio": "I just want everyone to be together on christmas.",
        "birthdate": "1993-07-26",
        "imageUrl": "https://unsplash.com/photos/DCVMd_NOpro/download?force=true&w=640",
        "bannerUrl": "https://i.picsum.photos/id/223/1080/640.jpg?hmac=1zRXJhkXy6EdeYC-WYatZnnmpkqINeYTiJ4-74E6t1o",
        "loginToken": "LIAbfvh341uNAS314"
    }
```

### PATCH
HTTP success code: 200
PATCH will update user if no conflicts exist
Conflicts include username or email that already exist or out of range values 
Login token is required for all updates
Example shows just bio being updated, but you can send multiple values to update at once as long as they are: bio, birthdate, email, username, bannerUrl or imageUrl
Password and user id cannot be updated
An error will be returned if you try to change the username or email to one that already exists or if you send invalid data.

```json
Example Data:

JSON Data Sent:
    { 
      "loginToken": "LIAbfvh341uNAS314",
      "bio": "Everyone is finally together for christmas!"
    }

JSON Data Returned: 
    { 
        "userId": 23,
        "email": "cindyLou@suess.com",
        "username": "CindyLou",
        "bio": "Everyone is finally together for christmas!",
        "birthdate": "1993-07-26",
        "imageUrl": "https://unsplash.com/photos/DCVMd_NOpro/download?force=true&w=640",
        "bannerUrl": "https://i.picsum.photos/id/223/1080/640.jpg?hmac=1zRXJhkXy6EdeYC-WYatZnnmpkqINeYTiJ4-74E6t1o"
    }
```

### DELETE
HTTP success code: 204
DELETE will delete the user if valid information is sent. Login token must belong to user with matching password
No data is returned on a valid delete.
An error will be returned if the loginToken and password combo are not valid.

```json
Example Data:

JSON Data Sent:
    { 
      "loginToken": "LIAbfvh341uNAS314",
      "password": "ISavedChristmas"
    }

No Data Returned
```

## Contributing
No Contributions