# Tweeter API

Tweeter API allows users to access multiple endpoints and perform basic CRUD requests based on specific endpoints and data passed. This API is currently under construction and not deployed.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install.

```bash
click==8.0.1
colorama==0.4.4
Flask==2.0.2
Flask-Cors==3.0.10
itsdangerous==2.0.1
Jinja2==3.0.2
mariadb==1.0.7
MarkupSafe==2.0.1
six==1.16.0
Werkzeug==2.0.2
bjoern==3.1.0
```

# Usage

## User Login: /api/login
The login end point supports only the POST and DELETE methods.


### POST
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
```json
Example Data:

JSON Data Sent:
    { 
      "loginToken": "LIAbfvh341uNAS314"
    }

No Data Returned
```


## Contributing
No Contributions