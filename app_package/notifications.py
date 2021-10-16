from app_package import app
from app_package.functions.queryFunctions import db_fetchall_args, db_index_fetchone, db_fetchall, db_commit
from app_package.functions.dataManFunctions import pop_comment_like, pop_dict_note
from flask import request, Response
import json

@app.route('/api/notifications', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def api_notifications():
    if request.method == 'GET':
        #gets all notifications for current user. 
        #list returned as descending to show must recent notifications at the top
        #login token required to get specific users info, must be sent in headers for encryption
        params = request.args
        token = request.headers.get("loginToken")
        user_id = params.get("userId")

        #check that proper keys submitted
        if len(params.keys()) == 1 and {"userId"} <= params.keys():
            #check userId is positive integer
            if str(user_id).isdigit() == False:
                return Response("Not a valid id number", mimetype="text/plain", status=400)

            #check userId exists    
            check_user_id = db_index_fetchone("SELECT EXISTS(SELECT id FROM user WHERE id=?)", [user_id])

            if check_user_id == 1:
                #check login token in headers match current user id
                user_is_valid = db_index_fetchone("SELECT EXISTS(SELECT id FROM user_session WHERE login_token=? \
                                                    AND user_id=?)", [token, user_id])
                if user_is_valid == 1:
                    #list returned as descending to show must recent notifications at the top
                    all_notifications = db_fetchall_args("SELECT * FROM notification WHERE user_id=? ORDER BY id DESC", [user_id])

                    #return in formatted list
                    all_notes_list = []
                    for a in all_notifications:
                        note = pop_dict_note(a)
                        all_notes_list.append(note)
                    
                    return Response(json.dumps(all_notes_list), mimetype="application/json", status=200) 

                else:
                    return Response("unauthorized to return this users data", mimetype="text/plain", status=400)
            else:
                return Response("User id does not exist", mimetype="text/plain", status=400)
        else:
            return Response("Invalid json data sent", mimetype="text/plain", status=400)

    elif request.method == 'POST':
        pass
    elif request.method == 'PATCH':
        pass
    elif request.method == 'DELETE':
        pass
    else:
        print("Something went wrong at notifications request.method")
        return Response("Something went wrong at request.method", mimetype='text/plain', status=500)