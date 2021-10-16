from app_package import app
from app_package.dataManFunctions import pop_dict_query
from app_package.queryFunctions import db_index_fetchone, db_commit, db_fetchall_args
from flask import request, Response
import json

@app.route('/api/follows', methods=['GET', 'POST', 'DELETE'])
def api_follows():
    if request.method == 'GET':
        params = request.args
        
        #checks that only one param is sent
        if len(params) == 1:
            if {"userId"} <= params.keys():
                param_id = params.get("userId")

                #checks if valid positive integer
                if param_id.isdigit() == False:
                    return Response("Not a valid id number", mimetype="text/plain", status=400)

                #checks if id exits as a user id. Returns a bool 1 or 0
                check_id_valid = db_index_fetchone("SELECT EXISTS(SELECT * FROM user WHERE id=?)", [param_id])

                #handles bool response
                if check_id_valid == 1:
                    all_follows = db_fetchall_args("SELECT id, email, username, bio, birthdate, image_url, banner_url \
                                    FROM user u INNER JOIN follows f ON u.id = f.followed WHERE f.follower=?", [param_id])
                    all_follows_list = []

                    #adds all valid users to a key formatted dict to return
                    for a in all_follows:
                        user = pop_dict_query(a)
                        all_follows_list.append(user)

                    return Response(json.dumps(all_follows_list), mimetype="application/json", status=200)

                else: 
                    return Response("User id does not exist", mimetype="text/plain", status=400)
            else:
                return Response("Incorrect key submitted.", mimetype='text/plain', status=400)                  
        else:
            return Response("Incorrect amount of data sent", mimetype="text/plain", status=400)

    elif request.method == 'POST':
        data = request.json
        if len(data.keys()) == 2:
            if {"loginToken", "followId"} <= data.keys():
                token = data.get("loginToken")
                follow_id = data.get("followId")
                
                #checks followId is positive integer
                if str(follow_id).isdigit() == False:
                    return Response("Not a valid follow id number", mimetype="text/plain", status=400)

                #checks if token valid
                if token != None:
                    #checks if token exists. 
                    token_valid = db_index_fetchone("SELECT EXISTS(SELECT login_token FROM user_session WHERE login_token=?)", [token])

                    if token_valid == 1:
                        #checks followId exists
                        check_follow_id = db_index_fetchone("SELECT EXISTS(SELECT id from user WHERE id=?)", [follow_id])

                        if check_follow_id == 1:
                            #grabs user_id that matches token 
                            user_id = db_index_fetchone("SELECT user_id FROM user_session WHERE login_token=?", [token])

                            #checks that user is not trying to follow themselves
                            if user_id == int(follow_id):
                                return Response("User cannot follow themselves", mimetype="text/plain", status=400)
                            
                            #checks follow relationship doesnt already exist
                            check_rel_exists = db_index_fetchone("SELECT EXISTS(SELECT followed FROM follows WHERE followed=? AND follower=?)", [follow_id, user_id])
                            
                            if check_rel_exists == 0:
                                db_commit("INSERT INTO follows(follower, followed) VALUES(?,?)", [user_id, follow_id])
                                return Response(status=204)

                            else:
                                return Response("This user is already being followed", mimetype="text/plain", status=400)
                        else:
                            return Response("No user with that id", mimetype="text/plain", status=400)
                    else:
                        return Response("Invalid login token", mimetype="text/plain", status=400)
                else:
                    return Response("Invalid login token", mimetype="text/plain", status=400)
            else:
                return Response("Incorrect keys submitted.", mimetype='text/plain', status=400)
        else:
            return Response("Not a valid amount of data sent", mimetype="text/plain", status=400)

    elif request.method == 'DELETE':
        data = request.json
        if len(data.keys()) == 2:
            if {"loginToken", "followId"} <= data.keys():
                token = data.get("loginToken")
                follow_id = data.get("followId")

                #checks followId is positive integer
                if str(follow_id).isdigit() == False:
                    return Response("Not a valid follow id number", mimetype="text/plain", status=400)
                
                #checks if token valid
                if token != None:
                    #checks if token exists. 
                    token_valid = db_index_fetchone("SELECT EXISTS(SELECT login_token FROM user_session WHERE login_token=?)", [token])

                    if token_valid == 1:
                        #checks followId exists
                        check_follow_id = db_index_fetchone("SELECT EXISTS(SELECT id from user WHERE id=?)", [follow_id])

                        if check_follow_id == 1:
                            #grabs user_id that matches token 
                            user_id = db_index_fetchone("SELECT user_id FROM user_session WHERE login_token=?", [token])

                            #check follow relationship exists
                            rel_exists = db_index_fetchone("SELECT EXISTS(SELECT follower, followed from follows WHERE \
                                            follower=? AND followed=?)", [user_id, follow_id])

                            if rel_exists == 1:
                                db_commit("DELETE FROM follows WHERE follower=? AND followed=?", [user_id, follow_id])
                                return Response(status=204)

                            else:
                                return Response("User not being followed, cannot unfollow", mimetype="text/plain", status=400)
                        else:
                            return Response("No user with that id", mimetype="text/plain", status=400)
                    else:
                        return Response("Invalid login token", mimetype="text/plain", status=400)
                else:
                    return Response("Invalid login token", mimetype="text/plain", status=400)
            else:
                return Response("Incorrect keys submitted.", mimetype='text/plain', status=400)
        else:
            return Response("Not a valid amount of data sent", mimetype="text/plain", status=400)
    else:
        print("Something went wrong at follows request.method")
        return Response("Something went wrong at request.method", mimetype='text/plain', status=500)
