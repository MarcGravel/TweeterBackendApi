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
                    all_notifications = db_fetchall_args("SELECT * FROM notification WHERE owner_id=? ORDER BY id DESC", [user_id])

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
        #see below for function to post notification. function needs to be outside request.method 
        #scope so other modules can access. On post of other requests, a notification post will be
        #created after successfull db commit.
        pass
    elif request.method == 'PATCH':
        pass
    elif request.method == 'DELETE':
        pass
    else:
        print("Something went wrong at notifications request.method")
        return Response("Something went wrong at request.method", mimetype='text/plain', status=500)

#uowners_id is id of user being notified
#others_id is id of user causing notification
#notified_id is id of object being notified(id# of tweet or comment)
#type_of_notify is what is causing notification (a tweet, a follow, a comment, a reply)
#seen is bool if user has viewed the notification yet, default to false on notify creation        
def post_notification(owners_id, cur_user_id, type_of_notify, notified_id):
    args_list = [owners_id, cur_user_id, type_of_notify]
    if any(arg is None for arg in args_list):
        print("Unable to create notification, null values exist")
    else:
        #default seen row always False
        isSeen = 0

        if type_of_notify == "like":
            db_commit("INSERT INTO notification(owner_id, cur_user_id, type_of_notify, seen, tweet_id) \
                        VALUES(?,?,?,?,?)", [owners_id, cur_user_id, type_of_notify, isSeen, notified_id])

        elif type_of_notify == "follow":
            db_commit("INSERT INTO notification(owner_id, cur_user_id, type_of_notify, seen) VALUES(?,?,?,?)", \
                        [owners_id, cur_user_id, type_of_notify, isSeen])
        elif type_of_notify == "comment":
            pass
        elif type_of_notify == "reply":
            pass
        else:
            print("Incorrect notification type tag")