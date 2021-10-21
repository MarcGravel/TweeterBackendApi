from app_package import app
from app_package.functions.queryFunctions import db_fetchall_args, db_index_fetchone, db_fetchall, db_commit
from app_package.functions.dataManFunctions import pop_comment_like, pop_dict_note
from flask import request, Response
import json

@app.route('/api/notifications', methods=['GET', 'PATCH', 'DELETE'])
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

    elif request.method == 'PATCH':
        #sets true (1) to all values in seen column that match ownerId and userId
        data = request.json
        token = data.get("loginToken")

        if len(data.keys()) == 1 and {"loginToken"} <= data.keys():
            #check login token valid
            token_valid = db_index_fetchone("SELECT EXISTS(SELECT login_token FROM user_session WHERE login_token=?)", [token])

            if token_valid == 1:
                #get user id from token
                user_id = db_index_fetchone("SELECT user_id FROM user_session WHERE login_token=?", [token])

                db_commit("UPDATE notification SET seen=1 WHERE owner_id=?", [user_id])
                return Response(status=200)
                
            else:
                return Response("Invalid login token", mimetype="text/plain", status=400)
        else:
            return Response("Invalid json data", mimetype="text/plain", status=400)

    elif request.method == 'DELETE':
        data = request.json
        token = data.get("loginToken")
        user_id = data.get("userId")

        #check proper keys submitted
        if len(data.keys()) == 2 and {"loginToken", "userId"} <= data.keys():
            #check userId is positive integer
            if str(user_id).isdigit() == False:
                return Response("Not a valid id number", mimetype="text/plain", status=400)

            #check loginToken valid
            token_valid = db_index_fetchone("SELECT EXISTS(SELECT login_token FROM user_session WHERE login_token=?)", [token])

            if token_valid == 1:
                #check id matches token
                user_is_valid = db_index_fetchone("SELECT EXISTS(SELECT id FROM user_session WHERE login_token=? \
                                                    AND user_id=?)", [token, user_id])
                
                if user_is_valid == 1:
                    db_commit("DELETE FROM notification WHERE owner_id=?", [user_id])
                    return Response(status=204)
                else:
                    return Response("Token does not match id", mimetype="text/plain", status=400)
            else:
                return Response("Invalid login token", mimetype="text/plain", status=400)
        else:
            return Response("Invalid json data sent", mimetype="text/plain", status=400)

    else:
        print("Something went wrong at notifications request.method")
        return Response("Something went wrong at request.method", mimetype='text/plain', status=500)

#owners_id is id of user being notified
#others_id is id of user causing notification
#notified_id is id of object being notified(id# of tweet or comment)
#type_of_notify is what is causing notification (a tweet, a follow, a comment, a reply)
#seen is bool if user has viewed the notification yet, default to false on notify creation        
def post_notification(owners_id, cur_user_id, type_of_notify, tweet_id, comment_id):
    args_list = [owners_id, cur_user_id, type_of_notify]
    if any(arg is None for arg in args_list):
        print("Unable to create notification, null values exist in required columns")
    else:
        #default seen row always False
        isSeen = 0

        if type_of_notify == "like":
            db_commit("INSERT INTO notification(owner_id, cur_user_id, type_of_notify, seen, tweet_id) \
                        VALUES(?,?,?,?,?)", [owners_id, cur_user_id, type_of_notify, isSeen, tweet_id])

        elif type_of_notify == "follow":
            db_commit("INSERT INTO notification(owner_id, cur_user_id, type_of_notify, seen) VALUES(?,?,?,?)", \
                        [owners_id, cur_user_id, type_of_notify, isSeen])
        elif type_of_notify == "comment" or type_of_notify == "reply":
            db_commit("INSERT INTO notification(owner_id, cur_user_id, type_of_notify, seen, tweet_id, comment_id) \
                        VALUES(?,?,?,?,?,?)", [owners_id, cur_user_id, type_of_notify, isSeen, tweet_id, comment_id])
        else:
            print("Incorrect notification type tag")