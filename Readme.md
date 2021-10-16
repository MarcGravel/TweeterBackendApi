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
# Content

### User Login
### Users
### Follows
### Followers
### Tweets
### Tweet Likes
### Comments
### Comment Likes

# Usage

## User Login: /api/login
The login end point supports only the POST and DELETE methods.


### POST
HTTP success code: 201

POST will log a user in if the username / password combo match.

Return data contains confirmation information about the user as well as a login token.

An error will be returned if the login information is invalid.

Client can send either username OR email along with the password for login validation.  
  
Required data: {"email", "password"} OR {"username", "password"}

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

DELETE will destroy the login token.

An error will be returned if the loginToken is invalid.

No data returned.    
  
Required data: {"loginToken"}
```json
Example Data:

JSON Data Sent:
    { 
      "loginToken": "LIAbfvh341uNAS314"
    }

No Data Returned
```

## Users: /api/users
The users end point supports GET, POST, PATCH, and DELETE methods.

### GET
HTTP success code: 200

GET will send all users information OR only a specific users information.

For all users, make a request with no params. If you want a specific users info, send the user id.

The value for bannerUrl and imageUrl will either contain the URL of their profile image or null if the user has no images.

An error will be returned if a userId does not exist.  
  
Required params: None OR {"userId"}
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

POST will create a new user if no conflicting current user.

When sending valid data about user, you are sent back conformation information about the new user. Along with a loginToken.

An error will be returned if a username or email already exists.  
  
Required Data: {"email", "username", "password", "bio", "birthdate"}

Optional Data: {"imageUrl"} AND/OR {"bannerUrl"}
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

PATCH will update user if no conflicts exist.

Conflicts include username or email that already exist or out of range values.

Login token is required for all updates.

Example shows just bio being updated, but you can send multiple values to update at once as long as they are: bio, birthdate, email, username, bannerUrl or imageUrl.

Password and user id cannot be updated.

An error will be returned if you try to change the username or email to one that already exists or if you send invalid data.  
  
Required Data: {"loginToken"}

Optional Data: Any combination of {"email", "username", "bio", "birthdate", "imageUrl", "bannerUrl"}
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

DELETE will delete the user if valid information is sent. Login token must belong to user with matching password.

No data is returned on a valid delete.

An error will be returned if the loginToken and password combo are not valid.  
  
Required Data: {"loginToken", "password"}
```json
Example Data:

JSON Data Sent:
    { 
      "loginToken": "LIAbfvh341uNAS314",
      "password": "ISavedChristmas"
    }

No Data Returned
```

## Follows: /api/follows
The follows end point supports GET, POST, and DELETE methods.

### GET
HTTP success code: 200

GET requires a user id to be sent. GET will return information about all users that the user id follows.

An error will be returned if the userId does not exist or is invalid.  
  
Required Data: {"userId"}
```json
Example Data:

JSON Params Sent:
    { 
      "userId": 3 
    }

JSON Data Returned: 
    [
      { 
          "userId": 1,
          "email": "lorax@suess.com",
          "username": "TheLorax",
          "bio": "I am the Lorax, I speak for the trees",
          "birthdate": "1971-06-23",
          "imageUrl": null,
          "bannerUrl": "https://i.picsum.photos/id/223/1080/640.jpg?hmac=1zRXJhkXy6EdeYC-WYatZnnmpkqINeYTiJ4-74E6t1o"
      },
      { 
          "userId": 2,
          "email": "grinch@suess.com",
          "username": "TheGrinch",
          "bio": "There will be no holly, jolly, christmas!",
          "birthdate": "1988-04-07",
          "imageUrl": "https://unsplash.com/photos/DCVMd_NOpro/download?force=true&w=640",
          "bannerUrl": "https://i.picsum.photos/id/223/1080/640.jpg?hmac=1zRXJhkXy6EdeYC-WYatZnnmpkqINeYTiJ4-74E6t1o"
      },
    ]
```

### POST 
HTTP success code: 204

POST will create a follow relationship between two users.

An error will be returned if the loginToken or followId are invalid.  
  
Required Data: {"loginToken", "followId"}
```json
Example Data:

JSON Data Sent:
    { 
      "loginToken": "LIAbfvh341uNAS314",
      "followId": "4"
    }

No data returned
```

### DELETE
HTTP success code: 204

DELETE will destroy follow relationship between user and user with userId matching sent followId (unfollow).

An error will be returned if the loginToken or followId are invalid.  
  
Required Data: {"loginToken", "followId"}
```json
Example Data:

JSON Data Sent:
    { 
      "loginToken": "LIAbfvh341uNAS314",
      "followId": "4"

    }

No data returned
```

## Followers: /api/followers
The followers end point supports GET method.

### GET
HTTP success code: 200

GET requires a user id to be sent. GET will return information about all users that follow the specified user.

An error will be returned if the userId does not exist or is invalid.  
  
Required Data: {"userId"}
```json
Example Data:

JSON Params Sent:
    { 
      "userId": 3 
    }

JSON Data Returned: 
    [
      { 
          "userId": 1,
          "email": "lorax@suess.com",
          "username": "TheLorax",
          "bio": "I am the Lorax, I speak for the trees",
          "birthdate": "1971-06-23",
          "imageUrl": null,
          "bannerUrl": "https://i.picsum.photos/id/223/1080/640.jpg?hmac=1zRXJhkXy6EdeYC-WYatZnnmpkqINeYTiJ4-74E6t1o"
      },
      { 
          "userId": 2,
          "email": "grinch@suess.com",
          "username": "TheGrinch",
          "bio": "There will be no holly, jolly, christmas!",
          "birthdate": "1988-04-07",
          "imageUrl": "https://unsplash.com/photos/DCVMd_NOpro/download?force=true&w=640",
          "bannerUrl": "https://i.picsum.photos/id/223/1080/640.jpg?hmac=1zRXJhkXy6EdeYC-WYatZnnmpkqINeYTiJ4-74E6t1o"
      },
    ]
```

## Tweets: /api/tweets
The tweets end point supports GET, POST, PATCH, DELETE methods.

### GET
HTTP success code: 200

GET will send all tweets data OR only a specific tweet data.

For all tweets, make a request with no params. If you want a specific tweets data, send the tweet id. And if you want all tweets from a specific user, send the user id.

An error will be returned if any userId or tweetId does not exist.

Required params: None OR {"userId"} OR {"tweetId"} 
```json
Example Data:

JSON Params Sent:
    { 
      "userId": 1 
    }

JSON Data Returned: 
    [
      { 
          "tweetId": 1,
          "userId": 1,
          "username": "TheLorax",
          "content": "Stop cutting down my trees!",
          "createdAt": "2020-06-11",
          "userImageUrl": "https://unsplash.com/photos/DCVMd_NOpro/download?force=true&w=640",
          "tweetImageUrl": "https://i.picsum.photos/id/223/1080/640.jpg?hmac=1zRXJhkXy6EdeYC-WYatZnnmpkqINeYTiJ4-74E6t1o"
      },
      { 
          "tweetId": 2,
          "userId": 1,
          "username": "TheLorax",
          "content": "Cut it off! Leave my trees alone!",
          "createdAt": "2020-06-13",
          "userImageUrl": "https://unsplash.com/photos/DCVMd_NOpro/download?force=true&w=640",
          "tweetImageUrl": "https://i.picsum.photos/id/223/1080/640.jpg?hmac=1zRXJhkXy6EdeYC-WYatZnnmpkqINeYTiJ4-74E6t1o"
      },
    ]
```

### POST
HTTP success code: 201

POST will create a new tweet for current user

Must send valid login token. Tweet will be created for user with matching valid token

Content is required to be sent, with a limit of 140 characters. Optional to send an imageUrl as well.

An error will be returned if the loginToken token invalid, content length invalid, or imageUrl length or url invalid.

Required Data: {"loginToken", "content"}

Optional Data: {"imageUrl"}
```json
Example Data:

JSON Data Sent:
    { 
      "loginToken": "LIAbfvh341uNAS314",
      "content": "The Grinch is going to come for Christmas dinner!",
      "imageUrl": "https://unsplash.com/photos/DCVMd_NOpro/download?force=true&w=640"
    }

JSON Data Returned
    {
      "tweetId": 5,
      "userId": 3,
      "username": "CindyLou",
      "userImageUrl": "https://unsplash.com/photos/DCVMd_NOpro/download?force=true&w=640",
      "content": "The Grinch is going to come for Christmas dinner!",
      "createdAt": "2020-04-15",
      "imageUrl": "https://unsplash.com/photos/DCVMd_NOpro/download?force=true&w=640"
    }
```

### PATCH
HTTP success code: 200

PATCH will update the tweet

The login token must match the same user that the tweet belongs to.

An error will be returned if the loginToken and tweetId combo are not valid (the user does not own that tweet or that tweet does not exist).

Required Data: {"loginToken", "tweetId"}
```json
Example Data: 

JSON Data Sent:
    { 
      "loginToken": "LIAbfvh341uNAS314",
      "tweetId": 2,
      "content": "FOR REAL! Cut it off! Leave my trees alone!"
    }

JSON Data Returned: 
    { 
      "tweetId": 2,
      "content": "FOR REAL! Cut it off! Leave my trees alone!"
    }
```

### DELETE
HTTP success code: 204

DELETE will delete the tweet

The login token must match the same user that the tweet belongs to.

An error will be returned if the loginToken and tweetId combo are not valid (the user does not own that tweet or that tweet does not exist).

Required Data: {"loginToken", "tweetId"}
```json
Example Data: 

JSON Data Sent:
    { 
      "loginToken": "LIAbfvh341uNAS314",
      "tweetId": "2"

    }

No data returned
```

## Tweet-Likes: /api/tweet-likes
The tweet-likes end point supports GET, POST, and DELETE methods.

### GET
HTTP success code: 200

GET will return either all likes or specified likes based on tweet

If you want all likes, send no data

If you want likes specific to a tweet, send the tweetId

An error will be returned if tweetId does not exist.

Required Params: None OR {"tweetId"}
```json
Example Data:

JSON Params Sent:
    { 
      "tweetId": 1 
    }

JSON Data Returned: 
    [
      { 
          "tweetId": 1,
          "userId": 1,
          "username": "TheLorax"
      },
      { 
          "tweetId": 1,
          "userId": 2,
          "username": "TheGrinch"
      },
    ]
```

### POST 
HTTP success code: 201

POST will create a new like for a specific tweet

Like will be created by user matching loginToken and like will be created for the tweet matching tweetId

An error will be returned if either the loginToken or tweetId are invalid. An error will also be sent if the user has already 'liked' the tweet.

Required Data: {"loginToken", "tweetId"}
```json
Example Data:

JSON Data Sent:
    { 
      "loginToken": "LIAbfvh341uNAS314",
      "tweetId": 4
    }

No Data Returned
```

### DELETE
HTTP success code: 204

DELETE will remove the like for a specific tweet

Like will be removed by user matching loginToken and like will be removed on the tweet matching tweetId

An error will be returned if either the loginToken or tweetId are invalid. An error will also be sent if the user has not yet 'liked' the tweet.

Required Data: {"loginToken", "tweetId"}
```json
Example Data:

JSON Data Sent:
    { 
      "loginToken": "LIAbfvh341uNAS314",
      "tweetId": "2"
    }

No JSON Returned
```

## Comments: /api/comments
The comments end point supports GET, POST, PATCH, and DELETE methods.

### GET
HTTP success code: 200

GET will return all comments based on tweetId sent.

For example, send the tweet id of 2 in params, the API will return all comments on tweet 2.

An error will be returned if the tweetId does not exist.

Required Data: {"tweetId"}
```json
Example Data:

JSON Data Sent:
    { 
      "tweetId": 2 
    }

JSON Data Returned: 
    [
      { 
          "commentId": 1,
          "tweetId": 2,
          "userId": 1,
          "username": "TheLorax",
          "content": "I agree! Give this guy some money to save trees!",
          "createdAt": "2020-07-12"
      },
      { 
          "commentId": 2,
          "tweetId": 2,
          "userId": 1,
          "username": "TheLorax",
          "content": "Why hasn't anyone given money yet?",
          "createdAt": "2020-07-13"
      },
    ]
```

### POST
HTTP success code: 201

POST will create a new comment from the current user on a specified tweet.

Login token and tweetId sent will tie the user and the tweet to the comment created.

Data about the comment, user, and tweet will be returned on success.

An error will be returned if the loginToken or tweetId are invalid. 

Comments have a limit of 150 characters.

Required Data: {"loginToken", "tweetId", "content"}
```json
Example Data:

JSON Data Sent:
    { 
      "loginToken": "LIAbfvh341uNAS314",
      "tweetId": 4,
      "content": "I agree, roast beast is good."
    }

JSON Data Returned:
    { 
        "commentId": 5,
        "tweetId": 4,
        "userId": 3,
        "username": "CindyLou",
        "content": "I agree, roast beast is good.",
        "createdAt": "2020-07-13"
    }
```

### PATCH
HTTP success code: 200

PATCH will update a comment if the loginToken is owned by the same user as the comment

Send an object with the loginToken, commentId and content. On success, you will be sent back conformation information about the updated comment.

An error will be returned if content character passes 150 limit or the login token does not own the comment being edited.

Required Data: {"loginToken", "commentId", "content"}
```json
Example Data:

JSON Data Sent:
    { 
      "loginToken": "LIAbfvh341uNAS314",
      "commentId": 5,
      "content": "I agree, roast beast is great."
    }

JSON Data Returned: 
      { 
        "commentId": 5,
        "tweetId": 4,
        "userId": 3,
        "username": "CindyLou",
        "content": "I agree, roast beast is great.",
        "createdAt": "2020-07-13"
    }
```

### DELETE
HTTP success code: 204

DELETE will delete a comment if the loginToken is owned by the same user as the comment.

No data is sent back on a valid delete.

An error will be returned if the loginToken and comment combo are not valid.

Required Data: {"loginToken", "commentId"}
```json
Example Data

JSON Data Sent:
    { 
      "loginToken": "LIAbfvh341uNAS314",
      "commentId": "1"
    }

No JSON Returned
```

## Contributing
No Contributions