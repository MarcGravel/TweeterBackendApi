import re

# Regular expression for email string
def check_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False

#checks length is valid on input
def check_length(input, min_len, max_len):
    if len(input) >= min_len and len(input) <= max_len:
        return True
    else:
        return False

#populates dict FROM SQL QUERY tuples or lists
def pop_dict_query(data):
    user = {
        "userId": data[0],
        "email": data[1],
        "username": data[2],
        "bio": data[3],
        "birthdate": data[4],
        "imageUrl": data[5],
        "bannerUrl": data[6] 
    }
    return user

#populates dict FROM JSON DATA REQ and removes leading and trailing whitespaces
def pop_dict_req(data):
    new_dict = {
    }
    for k, v in data.items():
        new_dict[k] = str(v).strip()

    return new_dict

#checks json request for allowed keys only
def allowed_data(data, allowed_keys):
    for key in list(data.keys()):
                if key not in allowed_keys:
                    del data[key]
    return data

#populates a tweet dict FROM SQL QUERY tuples or lists
def pop_dict_tweet(data):
    tweet = {
        "tweetId": data[0],
        "userId": data[1],
        "username": data[2],
        "content": data[3],
        "createdAt": data[4],
        "userImageUrl": data[5],
        "tweetImageUrl": data[6] 
    }
    return tweet

#populates a tweet like dict FROM SQL QUERY
def pop_tweet_like(data):
    like = {
        "tweetId": data[0],
        "userId": data[1],
        "username": data[2],
    }
    return like

#populates a comment dict FROM SQL QUERY
def pop_dict_comment(data):
    comment = {
        "commentId": data[0],
        "tweetId": data[1],
        "userId": data[2],
        "username": data[3],
        "content": data[4],
        "createdAt": data[5]
    }
    return comment

#populates a comment like dict FROM SQL QUERY
def pop_comment_like(data):
    like = {
        "commentId": data[0],
        "userId": data[1],
        "username": data[2],
    }
    return like

#populates a notification dict
def pop_dict_note(data):
    note = {
        "notificationId": data[0],
        "ownerId": data[1],
        "othersId": data[2],
        "typeOf": data[3],
        "isSeen": data[4],
        "tweetId": data[5],
        "commentId": data[6] 
    }
    return note