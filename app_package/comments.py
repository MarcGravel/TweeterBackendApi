from datetime import datetime
import validators
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
        pass
    elif request.method == 'PATCH':
        pass
    elif request.method == 'DELETE':
        pass
    else:
        print("Something went wrong, bad request method")
        return Response("Method Not Allowed", mimetype='text/plain', status=405) 