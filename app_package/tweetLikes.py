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
            
            #checks length of request. 2 lengths accepted. 
            #no data returns all likes
            if len(params.keys()) == 0:
                cursor.execute("SELECT t.tweet_id, u.id, u.username FROM tweet_like t INNER JOIN user u ON t.user_id = u.id")
                all_tweet_likes = cursor.fetchall()
                all_likes_list = []

                #adds all likes to a key formatted dict to return
                for l in all_tweet_likes:
                    like = pop_tweet_like(l)
                    all_likes_list.append(like)
                
                return Response(json.dumps(all_likes_list), mimetype="application/json", status=200)

            #id returns all likes of that tweet id
            if len(params.keys()) and {"tweetId"} <= params.keys():
                pass
            else:
                return Response("Incorrect Json data sent", mimetype='text/plain', status=400)


        elif request.method == 'POST':
            data = request.json
            pass

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