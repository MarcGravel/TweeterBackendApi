from datetime import datetime
import validators
from app_package import app
from app_package.dataManFunctions import allowed_data, pop_dict_req, check_length, pop_dict_tweet
from app_package.queryFunctions import db_fetchall_args, db_index_fetchone, db_fetchone, db_fetchall, db_commit
from flask import request, Response
import json

@app.route('/api/tweets', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def api_tweets():
    if request.method == 'GET':
        params = request.args
        
        # checks length of json dict (2 different requests are accepted), if values do not match correct amount, returns error message
        if len(params.keys()) == 0:
            all_tweets = db_fetchall("SELECT t.id, user_id, username, content, created_at, image_url, tweet_image_url FROM tweet t \
                            INNER JOIN user u ON t.user_id = u.id")
            all_tweets_list = []

            #adds all tweets to a key formatted dict to return
            for t in all_tweets: 
                tweet = pop_dict_tweet(t)
                all_tweets_list.append(tweet)

            # default=str in json.dumps handles the date object and sends as string
            # due to date obj not being serializable.
            return Response(json.dumps(all_tweets_list, default=str), mimetype="application/json", status=200)

        #if client sends over a userid param. checks proper key amount and then key name    
        elif len(params.keys()) == 1:
            if {"userId"} <= params.keys():
                param_id = params.get("userId")

                #checks if valid positive integer 
                if param_id.isdigit() == False:
                    return Response("Not a valid id number", mimetype="text/plain", status=400)
                
                #checks if param id exists as a user id
                check_id_valid = db_index_fetchone("SELECT EXISTS(SELECT * FROM user where id=?)", [param_id])

                if check_id_valid == 1:
                    user_tweets = db_fetchall_args("SELECT t.id, user_id, username, content, created_at, image_url, tweet_image_url FROM tweet t \
                            INNER JOIN user u ON t.user_id = u.id WHERE u.id=?", [param_id])
                    all_tweets_list = []

                    #populates response dict
                    for u in user_tweets:
                        tweet = pop_dict_tweet(u)
                        all_tweets_list.append(tweet)

                    return Response(json.dumps(all_tweets_list, default=str), mimetype="application/json", status=200)
                else:
                    return Response("User id does not exist", mimetype="text/plain", status=400)
            
            #if client sends over a tweetid param. checks key name
            elif {"tweetId"} <= params.keys():
                param_id = params.get("tweetId")

                #checks if valid positive integer 
                if param_id.isdigit() == False:
                    return Response("Not a valid id number", mimetype="text/plain", status=400)
                
                #checks if param id exists as a user id
                check_id_valid = db_index_fetchone("SELECT EXISTS(SELECT * FROM tweet where id=?)", [param_id])

                if check_id_valid == 1:
                    selected_tweet = db_fetchone("SELECT t.id, user_id, username, content, created_at, image_url, tweet_image_url FROM tweet t \
                                    INNER JOIN user u ON t.user_id = u.id WHERE t.id=?", [param_id])
                    resp_tweet = pop_dict_tweet(selected_tweet)
                    return Response(json.dumps(resp_tweet, default=str), mimetype="application/json", status=200)

                else: 
                    return Response("Tweet id does not exist", mimetype="text/plain", status=400)
            else:
                return Response("Incorrect json data sent", mimetype="text/plain", status=400)
        else:
            return Response("Too much data submitted", mimetype='text/plain', status=400)

    elif request.method == 'POST':
        data = request.json
        
        #checks if correct amount of keys for requests
        if len(data.keys()) == 2:
            if {"loginToken", "content"} <= data.keys():
                #populates a new dict with removed leading and trailing whitespaces
                new_tweet = pop_dict_req(data)
            else:
                return Response("Incorrect keys submitted.", mimetype='text/plain', status=400)
        
        #checks if correct amount of keys for requests
        elif len(data.keys()) == 3:
            if {"loginToken", "content", "imageUrl"} <= data.keys():
                #populates a new dict with removed leading and trailing whitespaces
                new_tweet = pop_dict_req(data)
            else:
                return Response("Incorrect keys submitted.", mimetype='text/plain', status=400)
        else: 
            return Response("Not a valid amount of data sent", mimetype="text/plain", status=400)
        
        #check token valid
        token = new_tweet["loginToken"]
        if token != None:
            #checks if token exists. 
            token_valid = db_index_fetchone("SELECT EXISTS(SELECT login_token FROM user_session WHERE login_token=?)", [token])

            if token_valid == 0:
                return Response("Not a valid login token", mimetype="text/plain", status=400)
        else:
            return Response("Invalid login token", mimetype="text/plain", status=400)

        #check content length
        if not check_length(new_tweet["content"], 1, 140):
            return Response("Content must be between 1 and 140 characters", mimetype="text/plain", status=400)
        
        #create a post timestamp for date
        created_date =  datetime.now()

        #get userId from token
        user_id = db_index_fetchone("SELECT user_id from user_session WHERE login_token=?", [new_tweet["loginToken"]])

        #add data to new row
        db_commit("INSERT INTO tweet(user_id, content, created_at) VALUES(?,?,?)", \
                        [user_id, new_tweet["content"], created_date])

        #checks if client sent info for image url, checks validity of url link then update.
        if "imageUrl" in new_tweet:
            if validators.url(new_tweet["imageUrl"]) and len(new_tweet["imageUrl"]) <= 200:
                db_commit("UPDATE tweet SET tweet_image_url=? WHERE user_id=?", [new_tweet["imageUrl"], user_id])

        #get all required return data
        ret_data = db_fetchone("SELECT t.id, u.id, username, u.image_url, content, created_at, tweet_image_url FROM tweet t \
                        INNER JOIN user u ON t.user_id = u.id WHERE t.user_id=? ORDER BY t.id DESC LIMIT 1", [user_id])     

        #create response data obj
        resp = {
            "tweetId": ret_data[0],
            "userId": ret_data[1],
            "username": ret_data[2],
            "userImageUrl": ret_data[3],
            "content": ret_data[4],
            "createdAt": ret_data[5],
            "imageUrl": ret_data[6]
        }
        return Response(json.dumps(resp, default=str), mimetype="application/json", status=201)

    elif request.method == 'PATCH':
        data = request.json
        token = data.get("loginToken")
        tweet_id = data.get("tweetId")

        #checks tweetId is positive integer
        if str(tweet_id).isdigit() == False:
            return Response("Not a valid tweet id number", mimetype="text/plain", status=400)

        if token != None:
            token_valid = db_index_fetchone("SELECT EXISTS(SELECT login_token FROM user_session WHERE login_token=?)", [token])

            if token_valid == 1:
                #check tweet id exists in db
                tweet_id_valid = db_index_fetchone("SELECT EXISTS(SELECT id FROM tweet WHERE id=?)", [tweet_id])

                if tweet_id_valid == 1:
                    #check login token matches user of tweet
                    rel_exists = db_index_fetchone("SELECT EXISTS (SELECT t.id FROM user_session u INNER JOIN \
                                    tweet t ON u.user_id = t.user_id WHERE login_token=? AND t.id=?)", [token, tweet_id])
                    
                    #if no relationship exists, send error
                    if rel_exists == 0:
                        return Response("Unauthorized to update this tweet", mimetype="text/plain", status=401)
                    
                    #removes any keys that should not exist in request
                    allowed_keys = {"loginToken", "tweetId", "content", "imageUrl"}
                    allowed_data(data, allowed_keys)

                    #populates a new dict that handles all leading and trailing whitespaces
                    upd_tweet = pop_dict_req(data)

                    #check content length
                    if not check_length(upd_tweet, 1, 140):
                        return Response("Content must be between 1 and 140 characters", mimetype="text/plain", status=400)

                    #runs update query if content check passes
                    db_commit("UPDATE tweet SET content=? WHERE id=?", [upd_tweet["content"], tweet_id])

                    #checks for imageUrl and validates if required
                    if "imageUrl" in upd_tweet:
                        if validators.url(upd_tweet["imageUrl"]) and len(upd_tweet["imageUrl"]) <= 200:
                            #runs update query if imageUrl check passes
                            db_commit("UPDATE tweet SET tweet_image_url=? WHERE id=?", [upd_tweet["imageUrl"], tweet_id])
                    
                    #collect and format response for return
                    updated_t = db_fetchone("SELECT id, content, tweet_image_url FROM tweet WHERE id=?", [tweet_id])

                    resp = {
                        "tweetId": updated_t[0],
                        "content": updated_t[1],
                        "imageUrl": updated_t[2]
                    }

                    return Response(json.dumps(resp), mimetype="application/json", status=200)

                else:
                    return Response("Tweet id does not exist", mimetype="text/plain", status=400)
            else:
                return Response("Invalid Login Token", mimetype="text/plain", status=400)
        else:
            return Response("A login token is required", mimetype="text/plain", status=400)

    elif request.method == 'DELETE':
        data = request.json
        tweet_id = data.get("tweetId")
        token = data.get("loginToken")
        
        if len(data.keys()) == 2 and {"loginToken", "tweetId"} <= data.keys():
            #checks tweetId is positive integer
            if str(tweet_id).isdigit() == False:
                return Response("Not a valid tweet id number", mimetype="text/plain", status=400)
            
            #checks if token valid
            if token != None:
                #checks if token exists. 
                token_valid = db_index_fetchone("SELECT EXISTS(SELECT login_token FROM user_session WHERE login_token=?)", [token])

                if token_valid == 1:
                    #checks tweetId exists
                    check_tweet_id = db_index_fetchone("SELECT EXISTS(SELECT id FROM tweet WHERE id=?)", [tweet_id])

                    if check_tweet_id == 1:
                        #check login token matches user of tweet
                        rel_exists = db_index_fetchone("SELECT EXISTS (SELECT t.id FROM user_session u INNER JOIN \
                                        tweet t ON u.user_id = t.user_id WHERE login_token=? AND t.id=?)", [token, tweet_id])
                        
                        if rel_exists == 1:
                            db_commit("DELETE FROM tweet WHERE id=?", [tweet_id])
                            return Response(status=204)

                        else:
                            return Response("Unauthorized to delete this tweet", mimetype="text/plain", status=401)
                    else:
                        return Response("Invalid tweet id", mimetype="text/plain", status=400)
                else:
                    return Response("Invalid login token", mimetype="text/plain", status=400)
            else:
                return Response("Invalid login token", mimetype="text/plain", status=400)
        else:
            return Response("Invalid Json data", mimetype="text/plain", status=400)
    else:
        print("Something went wrong at tweets request.method")
        return Response("Something went wrong at request.method", mimetype='text/plain', status=500) 

