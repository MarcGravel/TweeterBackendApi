from app_package import app
from app_package.queryFunctions import db_fetchall_args, db_index_fetchone, db_fetchall, db_commit
from app_package.dataManFunctions import pop_comment_like
from flask import request, Response
import json

@app.route('/api/comment-likes', methods=['GET', 'POST', 'DELETE'])
def api_comment_likes():
    if request.method == 'GET':
        params = request.args

        #checks length of request. 2 lengths accepted.
        #no data returns all likes
        if len(params.keys()) == 0:
            all_comment_likes = db_fetchall("SELECT c.comment_id, c.user_id, u.username FROM comment_like c INNER JOIN \
                                            user u ON c.user_id = u.id")
                #skip next elif/else statements to continue
        
        #id returns all likes of that comment id
        elif len(params.keys()) == 1 and {"commentId"} <= params.keys():
            comment_id = params.get("commentId")

            #checks if valid positive integer 
            if comment_id.isdigit() == False:
                return Response("Not a valid id number", mimetype="text/plain", status=400)

            #checks if comment_id exists in db
            check_id_valid = db_index_fetchone("SELECT EXISTS(SELECT * FROM comment WHERE id=?)", [comment_id])

            if check_id_valid == 1:
                all_comment_likes = db_fetchall_args("SELECT c.comment_id, c.user_id, u.username FROM comment_like c INNER JOIN \
                                            user u ON c.user_id = u.id WHERE c.comment_id=?", [comment_id])
                    #skip else statments to continue
            else:
                return Response("Comment id does not exist", mimetype="text/plain", status=400)
        else:
            return Response("Incorrect Json data sent", mimetype='text/plain', status=400)

        all_likes_list = []
        for l in all_comment_likes:
            like = pop_comment_like(l)
            all_likes_list.append(like)
        return Response(json.dumps(all_likes_list), mimetype="application/json", status=200)

    elif request.method == 'POST':
        pass
    elif request.method == 'DELETE':
        pass
    else:
        print("Something went wrong, bad request method")
        return Response("Method Not Allowed", mimetype='text/plain', status=405)