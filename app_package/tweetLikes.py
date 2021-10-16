from app_package import app
from app_package.functions.dataManFunctions import pop_tweet_like
from app_package.functions.queryFunctions import db_fetchall_args, db_index_fetchone, db_fetchall, db_commit
from flask import request, Response
import json

@app.route('/api/tweet-likes', methods=['GET', 'POST', 'DELETE'])
def api_tweet_likes():
    if request.method == 'GET':
        params = request.args
        
        #checks length of request. 2 lengths accepted. 
        #no data returns all likes
        if len(params.keys()) == 0:
            all_tweet_likes = db_fetchall("SELECT t.tweet_id, u.id, u.username FROM tweet_like t INNER JOIN user u ON t.user_id = u.id")
                #skip next elif/else statments to continue

        #id returns all likes of that tweet id
        elif len(params.keys()) == 1 and {"tweetId"} <= params.keys():
            tweet_id = params.get("tweetId")

            #checks if valid positive integer 
            if tweet_id.isdigit() == False:
                return Response("Not a valid id number", mimetype="text/plain", status=400)

            #checks if tweet_id exists in db
            check_id_valid = db_index_fetchone("SELECT EXISTS(SELECT * FROM tweet WHERE id=?)", [tweet_id])

            if check_id_valid == 1:
                all_tweet_likes = db_fetchall_args("SELECT t.tweet_id, u.id, u.username FROM tweet_like t INNER JOIN user u ON t.user_id = u.id \
                                WHERE t.tweet_id=?", [tweet_id])
                    #skip else statments to continue
            else:
                return Response("Tweet id does not exist", mimetype="text/plain", status=400)
        else:
            return Response("Incorrect Json data sent", mimetype='text/plain', status=400)
        
        # for either request above return all likes in a key formatted dict
        all_likes_list = []
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
                token_valid = db_index_fetchone("SELECT EXISTS(SELECT login_token FROM user_session WHERE login_token=?)", [token])

                if token_valid == 1:
                    #checks tweetId exists
                    check_tweet_id = db_index_fetchone("SELECT EXISTS(SELECT id FROM tweet WHERE id=?)", [tweet_id])

                    if check_tweet_id == 1:
                        #get userId matchinng loginToken
                        user_id = db_index_fetchone("SELECT user_id FROM user_session WHERE login_token=?", [token])

                        #check that user has not already liked current tweet
                        rel_exists = db_index_fetchone("SELECT EXISTS(SELECT t.id FROM tweet_like t INNER JOIN user_session u \
                                        ON t.user_id = u.user_id WHERE t.tweet_id=? AND t.user_id=?)", [tweet_id, user_id])

                        #if user has not liked the tweet:
                        if rel_exists == 0:
                            db_commit("INSERT INTO tweet_like(tweet_id, user_id) VALUES(?,?)", [tweet_id, user_id])
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
                token_valid = db_index_fetchone("SELECT EXISTS(SELECT login_token FROM user_session WHERE login_token=?)", [token])

                if token_valid == 1:
                    #checks tweetId exists
                    check_tweet_id = db_index_fetchone("SELECT EXISTS(SELECT id FROM tweet WHERE id=?)", [tweet_id])

                    if check_tweet_id == 1:
                        #get userId matching loginToken
                        user_id = db_index_fetchone("SELECT user_id FROM user_session WHERE login_token=?", [token])

                        #check that user has already liked current tweet
                        rel_exists = db_index_fetchone("SELECT EXISTS(SELECT t.id FROM tweet_like t INNER JOIN user_session u \
                                        ON t.user_id = u.user_id WHERE t.tweet_id=? AND t.user_id=?)", [tweet_id, user_id])

                        #if user has liked the tweet:
                        if rel_exists == 1:
                            db_commit("DELETE FROM tweet_like WHERE tweet_id=? AND user_id=?", [tweet_id, user_id])
                            return Response(status=204)

                        #if user has not liked the tweet:
                        elif rel_exists == 0:
                            return Response("Cannot delete like, current user has not yet liked", mimetype="text/plain", status=400)
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

    else:
        print("Something went wrong at tweet_likes request.method")
        return Response("Something went wrong at request.method", mimetype='text/plain', status=500) 
