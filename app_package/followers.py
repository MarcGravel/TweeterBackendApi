from app_package import app
from app_package.dataManFunctions import pop_dict_query
from app_package.queryFunctions import db_fetchall_args, db_index_fetchone, db_fetchone, db_fetchall, db_commit
import dbcreds
import mariadb
from flask import request, Response
import json

@app.route('/api/followers', methods=['GET'])
def api_followers():
    if request.method == 'GET':
        params = request.args

        #checks that only one param is sent
        if len(params) == 1:
            if {"userId"} <= params.keys():
                param_id = params.get("userId")

                #checks if valid positive integer
                if param_id.isdigit() == False:
                    return Response("Not a valid id number", mimetype="text/plain", status=400)

                #checks if id exists as a user id. Returns bool 1 or 0
                check_id_valid = db_index_fetchone("SELECT EXISTS(SELECT * FROM user WHERE id=?)", [param_id])

                #handle response
                if check_id_valid == 1:
                    all_followers = db_fetchall_args("SELECT id, email, username, bio, birthdate, image_url, banner_url \
                                    FROM user u INNER JOIN follows f ON u.id = f.follower WHERE f.followed=?", [param_id])
                    all_followers_list = []

                    #adds all valid users to a key formatted dict to return
                    for a in all_followers:
                        user = pop_dict_query(a)
                        all_followers_list.append(user)

                    return Response(json.dumps(all_followers_list), mimetype="application/json", status=200)

                else:
                    return Response("User id does not exist", mimetype="text/plain", status=400)
            else:
                return Response("Incorrect key submitted.", mimetype='text/plain', status=400)
        else:
            return Response("Incorrect amount of data sent", mimetype="text/plain", status=400)
    else:
        print("Something went wrong, bad request method")
        return Response("Method Not Allowed", mimetype='text/plain', status=405)