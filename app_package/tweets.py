from datetime import datetime

import validators
from werkzeug.datastructures import MIMEAccept
from werkzeug.wrappers import response
from app_package import app
from app_package.users import allowed_data, pop_dict_req, check_length
import dbcreds
import mariadb
from flask import Flask, request, Response
import json

@app.route('/api/tweets', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def api_tweets():
    try:
        conn = mariadb.connect(
                        user=dbcreds.user,
                        password=dbcreds.password,
                        host=dbcreds.host,
                        port=dbcreds.port,
                        database=dbcreds.database
                        )
        cursor = conn.cursor()

        if request.method == 'GET':
            params = request.args
            
            # checks length of json dict (2 different requests are accepted), if values do not match correct amount, returns error message
            if len(params.keys()) == 0:
                cursor.execute("SELECT t.id, user_id, username, content, created_at, user_image_url, tweet_image_url FROM tweet t \
                                INNER JOIN user u ON t.user_id = u.id")
                all_tweets = cursor.fetchall()
                all_tweets_list = []

                #adds all tweets to a key formatted dict to return
                for t in all_tweets: 
                    tweet = pop_dict_tweet(t)
                    all_tweets_list.append(tweet)

                # default=str in json.dumps handles the date object and sends as string
                # due to date obj not being serializable.
                return Response(json.dumps(all_tweets_list, default=str), mimetype="application/json", status=201)

            #if client sends over a userid param. checks proper key amount and then key name    
            elif len(params.keys()) == 1:
                if {"userId"} <= params.keys():
                    param_id = params.get("userId")

                    #checks if valid positive integer 
                    if param_id.isdigit() == False:
                        return Response("Not a valid id number", mimetype="text/plain", status=400)
                    
                    #checks if param id exists as a user id
                    cursor.execute("SELECT EXISTS(SELECT * FROM user where id=?)", [param_id])
                    check_id_valid = cursor.fetchone()[0]

                    if check_id_valid == 1:
                        cursor.execute("SELECT t.id, user_id, username, content, created_at, user_image_url, tweet_image_url FROM tweet t \
                                INNER JOIN user u ON t.user_id = u.id WHERE u.id=?", [param_id])
                        user_tweets = cursor.fetchall()
                        all_tweets_list = []

                        #populates response dict
                        for u in user_tweets:
                            tweet = pop_dict_tweet(u)
                            all_tweets_list.append(tweet)

                        return Response(json.dumps(all_tweets_list, default=str), mimetype="application/json", status=201)
                    else:
                        return Response("User id does not exist", mimetype="text/plain", status=400)
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
                        cursor.execute("SELECT EXISTS(SELECT login_token FROM user_session WHERE login_token=?)", [token])
                        token_valid = cursor.fetchone()[0]

                        if token_valid == 0:
                            return Response("Not a valid login token", mimetype="text/plain", status=400)
            else:
                return Response("Invalid login token", mimetype="text/plain", status=400)

            #check content length
            if not check_length(new_tweet["content"], 1, 140):
                return Response("Content must be between 1 and 140 characters", mimetype="text/plain", status=400)
            
            #create a post timestamp for date only
            created_date =  datetime.now()

            #get userId from token
            cursor.execute("SELECT user_id from user_session WHERE login_token=?", [new_tweet["loginToken"]])
            user_id = cursor.fetchone()[0]

            #add data to new row
            cursor.execute("INSERT INTO tweet(user_id, content, created_at) VALUES(?,?,?)", \
                            [user_id, new_tweet["content"], created_date])
            conn.commit()

            #checks if client sent info for image url, checks validity of url link then update.
            if "imageUrl" in new_tweet:
                if validators.url(new_tweet["imageUrl"]) and len(new_tweet["imageUrl"]) <= 200:
                    cursor.execute("UPDATE tweet SET tweet_image_url=? WHERE user_id=?", [new_tweet["imageUrl"], user_id])
                    conn.commit()

            #get all required return data
            cursor.execute("SELECT t.id, u.id, username, u.image_url, content, created_at, tweet_image_url FROM tweet t \
                            INNER JOIN user u ON t.user_id = u.id WHERE t.user_id=? ORDER BY t.id DESC LIMIT 1", [user_id]) 
            ret_data = cursor.fetchone()  
            print(ret_data)     

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
            tweetId = data.get("tweetId")

            #checks tweetId is positive integer
            if str(tweetId).isdigit() == False:
                return Response("Not a valid tweet id number", mimetype="text/plain", status=400)

            if token != None:
                cursor.execute("SELECT EXISTS(SELECT login_token FROM user_session WHERE login_token=?)", [token])
                token_valid = cursor.fetchone()[0]

                if token_valid == 1:
                    #check tweet id exists in db
                    cursor.execute("SELECT EXISTS(SELECT id FROM tweet WHERE id=?)", [tweetId])
                    tweet_id_valid = cursor.fetchone()[0]

                    if tweet_id_valid == 1:
                        #checks that login token matches user of tweet
                        cursor.execute("SELECT t.id FROM user_session u INNER JOIN \
                                        tweet t ON u.user_id = t.user_id WHERE login_token=?", [token])
                        valid_match_tpl = cursor.fetchall()
                        match_list = []
                        
                        #extract tweetIds from tuples and check if any match
                        for v in valid_match_tpl:
                            value = v[0]
                            match_list.append(value)

                        #returns error if tweetid does not belong to same user as login token
                        if not int(tweetId) in match_list:
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
                        cursor.execute("UPDATE tweet SET content=? WHERE id=?", [upd_tweet["content"], tweetId])
                        conn.commit()

                        #checks for imageUrl and validates if required
                        if "imageUrl" in upd_tweet:
                            if validators.url(upd_tweet["imageUrl"]) and len(upd_tweet["imageUrl"]) <= 200:
                                #runs update query if imageUrl check passes
                                cursor.execute("UPDATE tweet SET tweet_image_url=? WHERE id=?", [upd_tweet["imageUrl"], tweetId])
                                conn.commit()
                        
                        #collect and format response for return
                        cursor.execute("SELECT id, content, tweet_image_url FROM tweet WHERE id=?", [tweetId])
                        updated_t = cursor.fetchone()

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
            data = request.data
            pass

        else:
            print("Something went wrong, bad request method")
            return Response("Method Not Allowed", mimetype='text/plain', status=405)

    except mariadb.DataError:
        print("Something is wrong with your data")
        return Response("Something is wrong with the data", mimetype='text/plain', status=404)
    except mariadb.OperationalError:
        print("Something is wrong with your connection")
        return Response("Something is wrong with the connection", mimetype='text/plain', status=500)

    
    finally:
        if (cursor != None):
            cursor.close()
        if (conn != None):
            conn.rollback()
            conn.close()

#populates a tweet dict FROM SQL QUERY tuples or lists
def pop_dict_tweet(data):
    user = {
        "tweetid": data[0],
        "userId": data[1],
        "username": data[2],
        "content": data[3],
        "createdAt": data[4],
        "userImageUrl": data[5],
        "tweetImageUrl": data[6] 
    }
    return user