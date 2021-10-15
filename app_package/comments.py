from datetime import datetime
import validators
from werkzeug.wrappers import response
from app_package import app
from app_package.dataManFunctions import allowed_data, pop_dict_req, check_length, pop_dict_comment
from app_package.queryFunctions import db_fetchall_args, db_index_fetchone, db_fetchone, db_fetchall, db_commit
from flask import request, Response
import json

@app.route('/api/comments', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def api_comments():
    if request.method == 'GET':
        params = request.args

        # checks length of json dict, if values do not match correct amount, returns error message
        if len(params.keys()) == 1:
            if {"tweetId"} <= params.keys():
                param_id = params.get("tweetId")

                #checks if valid positive integer 
                if param_id.isdigit() == False:
                    return Response("Not a valid id number", mimetype="text/plain", status=400)

                #checks if param id exists as a user id
                check_id_valid = db_index_fetchone("SELECT EXISTS(SELECT * FROM tweet where id=?)", [param_id])

                if check_id_valid == 1:
                    tweet_comments = db_fetchall_args("SELECT c.id, t.id, u.id, username, c.content, c.created_at FROM comment c \
                            INNER JOIN tweet t ON c.tweet_id = t.id INNER JOIN user u ON c.user_id = u.id WHERE t.id=?", [param_id])
                    all_comments_list = []

                    #populates response dict
                    for t in tweet_comments:
                        comment = pop_dict_comment(t)
                        all_comments_list.append(comment)

                    return Response(json.dumps(all_comments_list, default=str), mimetype="application/json", status=200)
                else:
                    return Response("Tweet id does not exist", mimetype="text/plain", status=400)
            else:
                return Response("Incorrect json data sent", mimetype="text/plain", status=400)
        else:
            return Response("Incorrect amount of data submitted", mimetype='text/plain', status=400)

    elif request.method == 'POST':
        data = request.json
        token = data.get("loginToken")
        tweet_id = data.get("tweetId")

        #checks if correct amount of keys from request
        if len(data.keys()) == 3:
            if {"loginToken", "tweetId", "content"} <= data.keys():
                #populates a new dict with leading and trailing whitespaces removed
                new_comment = pop_dict_req(data)
            else:
                return Response("Incorrect keys submitted", mimetype="text/plain", status=400)

            #checks if valid positive integer 
            if str(tweet_id).isdigit() == False:
                return Response("Not a valid id number", mimetype="text/plain", status=400)
            
            #check token valid
            if token != None:
                #checks if token exists. 
                token_valid = db_index_fetchone("SELECT EXISTS(SELECT login_token FROM user_session WHERE login_token=?)", [token])

                if token_valid == 0:
                    return Response("Not a valid login token", mimetype="text/plain", status=400)
            else:
                return Response("Invalid login token", mimetype="text/plain", status=400)

            #check tweetId exists
            tweet_id_valid = db_index_fetchone("SELECT EXISTS(SELECT id FROM tweet WHERE id=?)", [tweet_id])

            if tweet_id_valid == 0:
                return Response("Tweet id does not exist", mimetype="text/plain", status=400)

            #check content length
            if not check_length(new_comment["content"], 1, 150):
                return Response("Content must be between 1 and 150 characters", mimetype="text/plain", status=400)
            
            #create a post timestamp for date
            created_date =  datetime.now()

            #get userId from token
            user_id = db_index_fetchone("SELECT user_id FROM user_session WHERE login_token=?", [new_comment["loginToken"]])
            print(user_id)

            #add data to new row
            db_commit("INSERT INTO comment(tweet_id, user_id, content, created_at) VALUES(?,?,?,?)", \
                        [tweet_id, user_id, new_comment["content"], created_date])
            
            #get all required data for return
            ret_data = db_fetchone("SELECT c.id, c.tweet_id, c.user_id, u.username, c.content, c.created_at FROM \
                                    comment c INNER JOIN user u ON c.user_id = u.id INNER JOIN tweet t ON \
                                    c.tweet_id = t.id WHERE c.tweet_id=? AND c.user_id=? ORDER BY c.id DESC LIMIT 1", [tweet_id, user_id])
            
            #create response obj
            resp = pop_dict_comment(ret_data)

            return Response(json.dumps(resp, default=str), mimetype="application/json", status=201) 

        else:
            return Response("Not a valid amount of data sent", mimetype="text/plain", status=400)

    elif request.method == 'PATCH':
        data = request.json
        token = data.get("loginToken")
        comment_id = data.get("commentId")
        content = data.get("content")

        if len(data.keys()) == 3 and {"loginToken", "commentId", "content"} <= data.keys():
            #checks commentId is positive integer
            if str(comment_id).isdigit() == False:
                return Response("Not a valid comment id number", mimetype="text/plain", status=400)

            if token != None:
                token_valid = db_index_fetchone("SELECT EXISTS(SELECT login_token FROM user_session WHERE login_token=?)", [token])

                if token_valid == 1:
                    #check comment id exists in db
                    comment_id_valid = db_index_fetchone("SELECT EXISTS(SELECT id FROM comment WHERE id=?)", [comment_id])

                    if comment_id_valid == 1:
                        #check the comment belongs to same user as login token
                        rel_exists = db_index_fetchone("SELECT EXISTS(SELECT c.id FROM comment c INNER JOIN \
                                                        user_session u ON u.user_id = c.user_id WHERE u.login_token=? \
                                                        AND c.id=?)", [token, comment_id])

                        if rel_exists == 1:
                            #clear leading and trailing whitespaces from content
                            clean_content = str(content).strip()
                            #check content length
                            if not check_length(clean_content, 1, 150):
                                return Response("Content must be between 1 and 150 characters", mimetype="text/plain", status=400)
                            #run update query if check passes
                            db_commit("UPDATE comment SET content=? WHERE id=?", [clean_content, comment_id])

                            #collect and format response for return
                            updated_c = db_fetchone("SELECT c.id, c.tweet_id, c.user_id, u.username, c.content, c.created_at FROM \
                                                    comment c INNER JOIN user u ON c.user_id = u.id WHERE c.id=?", [comment_id])
                            
                            resp = pop_dict_comment(updated_c)

                            return Response(json.dumps(resp, default=str), mimetype="application/json", status=200)
                        else: 
                            return Response("Unauthorized to update this comment", mimetype="text/plain", status=401)
                    else:
                        return Response("Comment id does not exist", mimetype="text/plain", status=400)
                else:
                    return Response("Invalid login token", mimetype="text/plain", status=400)
            else:
                return Response("A login token is required", mimetype="text/plain", status=400)
        else:
            return Response("Invalid json data sent", mimetype="text/plain", status=400)

    elif request.method == 'DELETE':
        pass
    else:
        print("Something went wrong, bad request method")
        return Response("Method Not Allowed", mimetype='text/plain', status=405) 