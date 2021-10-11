from werkzeug.wrappers.response import ResponseStream
from app_package import app
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
                print("Too much JSON data submitted")
                return Response("Too much data submitted", mimetype='text/plain', status=400)

        elif request.method == 'POST':
            data = request.data
            pass
        elif request.method == 'PATCH':
            data = request.data
            pass
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