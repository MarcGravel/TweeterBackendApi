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
        data = request.json
        token = data.get("loginToken")
        comment_id = data.get("commentId")

        #check correct keys sent
        if len(data.keys()) == 2 and {"loginToken", "commentId"} <= data.keys():
            
            #checks if token valid
            if token != None:
                #checks if token exists. 
                token_valid = db_index_fetchone("SELECT EXISTS(SELECT login_token FROM user_session WHERE login_token=?)", [token])

                if token_valid == 1:
                    #check commentId exists
                    check_comment_id = db_index_fetchone("SELECT EXISTS(SELECT id FROM comment WHERE id=?)", [comment_id])

                    if check_comment_id == 1:
                        #get userId matching token
                        user_id = db_index_fetchone("SELECT user_id FROM user_session WHERE login_token=?", [token])

                        #check that user has not already like the comment
                        rel_exists = db_index_fetchone("SELECT EXISTS(SELECT id FROM comment_like WHERE comment_id=? \
                                                        AND user_id=?)", [comment_id, user_id])

                        if rel_exists == 0:
                            db_commit("INSERT INTO comment_like(comment_id, user_id) VALUES(?,?)", [comment_id, user_id])
                            return Response(status=201)

                        else:
                            return Response("Cannot like comment, current user has already liked it", mimetype="text/plain", status=400)
                    else:
                        return Response("Invalid comment id", mimetype="text/plain", status=400)
                else:
                    return Response("Invalid login token", mimetype="text/plain", status=400)
            else:
                return Response("Invalid login token", mimetype="text/plain", status=400)
        else:
            return Response("Invalid Json data", mimetype="text/plain", status=400)

    elif request.method == 'DELETE':
        data = request.json
        token = data.get("loginToken")
        comment_id = data.get("commentId")

        #check correct keys sent
        if len(data.keys()) == 2 and {"loginToken", "commentId"} <= data.keys():
            
            #check tweetId is positive integer
            if str(comment_id).isdigit() == False:
                return Response("Not a valid tweet id number", mimetype="text/plain", status=400)
            
            #check token valid
            if token != None:
                #checks if token exists. 
                token_valid = db_index_fetchone("SELECT EXISTS(SELECT login_token FROM user_session WHERE login_token=?)", [token])

                if token_valid == 1:
                     #checks commentId exists
                    check_comment_id = db_index_fetchone("SELECT EXISTS(SELECT id FROM comment WHERE id=?)", [comment_id])

                    if check_comment_id == 1:
                        #get userId matchng loginToken
                        user_id = db_index_fetchone("SELECT user_id FROM user_session WHERE login_token=?", [token])

                        #check that user has already like current comment
                        rel_exists = db_index_fetchone("SELECT EXISTS(SELECT id FROM comment_like WHERE comment_id=? \
                                                        AND user_id=?)", [comment_id, user_id])
                        
                        #if user has liked comment
                        if rel_exists == 1:
                            db_commit("DELETE FROM comment_like WHERE comment_id=? AND user_id=?", [comment_id, user_id])
                            return Response(status=204)
                        else:
                            return Response("Cannot delete like, current user has not yet liked", mimetype="text/plain", status=400)
                    else:
                        return Response("Invalid comment id", mimetype="text/plain", status=400)
                else:
                    return Response("Invalid login token", mimetype="text/plain", status=400)
            else:
                return Response("Invalid login token", mimetype="text/plain", status=400)
        else:
            return Response("Invalid json data sent", mimetype="text/plain", status=400)
    else:
        print("Something went wrong, bad request method")
        return Response("Method Not Allowed", mimetype='text/plain', status=405)