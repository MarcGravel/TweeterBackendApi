from werkzeug.datastructures import MIMEAccept
from app_package import app
import dbcreds
import mariadb
from flask import Flask, request, Response
import json

@app.route('/api/tweet-likes', methods=['GET', 'POST', 'DELETE'])
def api_tweet_likes():
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
            print(len(params.keys()))
            
            #checks length of request. 2 lengths accepted. 
            #no data returns all likes
            if len(params.keys()) == 0:
                cursor.execute("SELECT t.tweet_id, u.id, u.username FROM tweet_like t INNER JOIN user u ON t.user_id = u.id")
                all_tweet_likes = cursor.fetchall()
                all_likes_list = []
                    #skip next elif/else statments to continue

            #id returns all likes of that tweet id
            elif len(params.keys()) == 1 and {"tweetId"} <= params.keys():
                tweet_id = params.get("tweetId")

                #checks if valid positive integer 
                if tweet_id.isdigit() == False:
                    return Response("Not a valid id number", mimetype="text/plain", status=400)

                #checks if tweet_id exists in db
                cursor.execute("SELECT EXISTS(SELECT * FROM tweet WHERE id=?)", [tweet_id])
                check_id_valid = cursor.fetchone()[0]

                if check_id_valid == 1:
                    cursor.execute("SELECT t.tweet_id, u.id, u.username FROM tweet_like t INNER JOIN user u ON t.user_id = u.id \
                                    WHERE t.tweet_id=?", [tweet_id])
                    all_tweet_likes = cursor.fetchall()
                    all_likes_list = []
                        #skip else statments to continue
                else:
                    return Response("Tweet id does not exist", mimetype="text/plain", status=400)
            else:
                return Response("Incorrect Json data sent", mimetype='text/plain', status=400)
            
            # for either request above return all likes in a key formatted dict
            for l in all_tweet_likes:
                like = pop_tweet_like(l)
                all_likes_list.append(like)
            return Response(json.dumps(all_likes_list), mimetype="application/json", status=200)

        elif request.method == 'POST':
            data = request.json
            token = data.get("loginToken")
            tweet_id = data.get("tweetId")

            #checks correct keys sent
            if len(data.keys()) == 2 and {"loginToken", "tweetId"} <= data.keys():
                
                #checks tweetId is positive integer
                if str(tweet_id).isdigit() == False:
                    return Response("Not a valid tweet id number", mimetype="text/plain", status=400)
                
                #checks if token valid
                if token != None:
                    #checks if token exists. 
                    cursor.execute("SELECT EXISTS(SELECT login_token FROM user_session WHERE login_token=?)", [token])
                    token_valid = cursor.fetchone()[0]

                    if token_valid == 1:
                        #checks tweetId exists
                        cursor.execute("SELECT EXISTS(SELECT id FROM tweet WHERE id=?)", [tweet_id])
                        check_tweet_id = cursor.fetchone()[0]

                        if check_tweet_id == 1:
                            #get userId matchinng loginToken
                            cursor.execute("SELECT user_id FROM user_session WHERE login_token=?", [token])
                            user_id = cursor.fetchone()[0]

                            #check that user has not already liked current tweet
                            cursor.execute("SELECT EXISTS(SELECT t.id FROM tweet_like t INNER JOIN user_session u \
                                            ON t.user_id = u.user_id WHERE t.tweet_id=? AND t.user_id=?)", [tweet_id, user_id])
                            rel_exists = cursor.fetchone()[0]

                            #if user has not liked the tweet:
                            if rel_exists == 0:
                                cursor.execute("INSERT INTO tweet_like(tweet_id, user_id) VALUES(?,?)", [tweet_id, user_id])
                                conn.commit()
                                return Response(status=201)

                            #if user has already liked the tweet:
                            elif rel_exists == 1:
                                return Response("Cannot like tweet, current user has already liked", mimetype="text/plain", status=400)
                            else:
                                print("error in returning exists bool value in tweetLikes/post") 
                                return Response("Something went wrong", mimetype="text/plain", status=500)                       
                        else:
                            return Response("Invalid tweet id", mimetype="text/plain", status=400)
                    else:
                        return Response("Invalid login token", mimetype="text/plain", status=400)
                else:
                    return Response("Invalid login token", mimetype="text/plain", status=400)
            else:
                return Response("Invalid Json data", mimetype="text/plain", status=400)

        elif request.method == 'DELETE':
            data = request.json
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
    except:
        print("Something went wrong")
        return Response("Something went wrong", status=500)
    
    finally:
        if (cursor != None):
            cursor.close()
        if (conn != None):
            conn.rollback()
            conn.close()

#populates a tweet like dict FROM SQL QUERY
def pop_tweet_like(data):
    like = {
        "tweetId": data[0],
        "userId": data[1],
        "username": data[2],
    }
    return like