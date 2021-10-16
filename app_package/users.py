from app_package import app
from app_package.dataManFunctions import pop_dict_query, pop_dict_req, check_email, check_length, allowed_data
from app_package.queryFunctions import db_index_fetchone, db_fetchone, db_fetchall, db_commit
from flask import request, Response
import json
import secrets #package to create session token strings
import validators #validates URLs

@app.route('/api/users', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def api_users():
    if request.method == 'GET':
        params = request.args

        # checks length of json dict (2 different requests are accepted), if values do not match correct amount, returns error message
        if len(params.keys()) == 0:
            all_users = db_fetchall("SELECT id, email, username, bio, birthdate, image_url, banner_url FROM user")
            all_user_list = []

            #adds all users to a key formatted dict to return
            for u in all_users:
                user = pop_dict_query(u)
                all_user_list.append(user)

            return Response(json.dumps(all_user_list), mimetype="application/json", status=200)
        
        #if client sends over a userid param. checks proper key amount and then key name
        elif len(params.keys()) == 1:
            if {"userId"} <= params.keys():
                param_id = params.get("userId")

                #checks if valid positive integer
                if param_id.isdigit() == False:
                    return Response("Not a valid id number", mimetype="text/plain", status=400)

                #checks if param id exists as a user id in DB
                #if not exists, returns 0. If exists, returns one. 
                check_id_valid = db_index_fetchone("SELECT EXISTS(SELECT * FROM user WHERE id=?)", [param_id])

                #handles response of EXISTS query
                if check_id_valid == 1:
                    sel_usr = db_fetchone("SELECT id, email, username, bio, birthdate, image_url, banner_url FROM user WHERE id=?", [param_id])
                    resp = pop_dict_query(sel_usr)

                    return Response(json.dumps(resp), mimetype="application/json", status=200)
                else:
                    return Response("User id does not exist", mimetype="text/plain", status=400)
            else:
                return Response("Incorrect keys submitted.", mimetype='text/plain', status=400)
        else:
            return Response("Too much data submitted", mimetype='text/plain', status=400)

    elif request.method == 'POST':
        data = request.json
        
        if len(data.keys()) >= 5 and len(data.keys()) <= 7: 
            if {"email", "username", "password", "bio", "birthdate"} <= data.keys() or \
                    {"email", "username", "password", "bio", "birthdate", "imageUrl"} <= data.keys() or \
                        {"email", "username", "password", "bio", "birthdate", "bannerUrl"} <= data.keys() or \
                            {"email", "username", "password", "bio", "birthdate", "imageUrl", "bannerUrl"} <= data.keys():

                    #populates a clean dict that handles whitespaces
                    new_user = pop_dict_req(data)   
                    
            else: 
                return Response("Incorrect keys submitted.", mimetype='text/plain', status=400)
        else: 
            return Response("Not a valid amount of data sent", mimetype="text/plain", status=400)

        #check email valid and proper character count
        if not check_email(new_user["email"]):
            return Response("Not a valid email address", mimetype="text/plain", status=400)

        #check email length
        if not check_length(new_user["email"], 1, 40):
            return Response("Email is too long", mimetype="text/plain", status=400)

        #check email exists in db
        check_email_exists = db_index_fetchone("SELECT EXISTS(SELECT email FROM user WHERE email=?)", [new_user["email"]])

        if check_email_exists == 1:
            return Response("Email already exists", mimetype="text/plain", status=400)

        #check username valid
        if not check_length(new_user["username"], 1, 50):
            return Response("Username must be between 1 and 50 characters", mimetype="text/plain", status=400)

        #check username exists in db
        check_username_exists = db_index_fetchone("SELECT EXISTS(SELECT username FROM user WHERE username=?)", [new_user["username"]])

        if check_username_exists == 1:
            return Response("Username already exists", mimetype="text/plain", status=400)

        #check password valid
        if not check_length(new_user["password"], 6, 50):
            return Response("Password must be between 6 and 50 characters", mimetype="text/plain", status=400)

        #check bio valid
        if not check_length(new_user["bio"], 1, 70):
            return Response("Bio must be between 1 and 70 characters", mimetype="text/plain", status=400)

        #check birthdate valid
        if not check_length(new_user["birthdate"], 1, 30):
            return Response("Birthdate value must be between 1 and 30 characters", mimetype="text/plain", status=400)
        
        #adds data to new row in db
        db_commit("INSERT INTO user(email, username, password, bio, birthdate) \
                        VALUES(?,?,?,?,?)", [new_user["email"], new_user["username"], 
                            new_user["password"], new_user["bio"], new_user["birthdate"]])

        user_id = db_index_fetchone("SELECT id FROM user WHERE email=?", [new_user["email"]])

        #checks if client sent info for image or banner url, checks validity of url links then updates.
        if "imageUrl" in new_user:
            if validators.url(new_user["imageUrl"]) and len(new_user["imageUrl"]) <= 200:
                db_commit("UPDATE user SET image_url=? WHERE id=?", [new_user["imageUrl"], user_id])
            
        if "bannerUrl" in new_user:
            if validators.url(new_user["bannerUrl"]) and len(new_user["bannerUrl"]) <= 200:
                db_commit("UPDATE user SET banner_url=? WHERE id=?", [new_user["bannerUrl"], user_id])

        #create session token and add token/user to session table
        login_token = secrets.token_urlsafe(16)
        db_commit("INSERT INTO user_session(user_id, login_token) VALUES(?,?)", [user_id, login_token])
        
        #get all data from tables and return a response
        usr = db_fetchone("SELECT id, email, username, bio, birthdate, image_url, banner_url FROM user WHERE id=?", [user_id])

        #populates dict and then adds the login token
        resp = pop_dict_query(usr)   
        resp["loginToken"] = login_token 

        return Response(json.dumps(resp), mimetype="application/json", status=201)

    elif request.method == 'PATCH':
        data = request.json
        token = data.get("loginToken")

        if token != None:
            token_valid = db_index_fetchone("SELECT EXISTS(SELECT login_token FROM user_session WHERE login_token=?)", [token])
            
            if token_valid == 1:
                #removes any keys that should not exist in request
                allowed_keys = {"loginToken", "email", "username", "bio", "birthdate", "imageUrl", "bannerUrl"}
                allowed_data(data, allowed_keys)

                #populates a new dict to handle all whitespaces
                upd_user = pop_dict_req(data)

                #check email valid and proper character count
                if "email" in upd_user:
                    if not check_email(upd_user["email"]):
                        return Response("Not a valid email address", mimetype="text/plain", status=400)

                    #check email length
                    if not check_length(upd_user["email"], 1, 40):
                        return Response("Email is too long", mimetype="text/plain", status=400)

                    #check email exists in db
                    check_email_exists = db_index_fetchone("SELECT EXISTS(SELECT email FROM user WHERE email=?)", [upd_user["email"]])

                    if check_email_exists == 1:
                        return Response("Email already exists", mimetype="text/plain", status=400)

                    #runs update query if all email checks pass
                    db_commit("UPDATE user u INNER JOIN user_session s ON u.id = s.user_id SET email=? WHERE login_token=?", [upd_user["email"], token])

                #check username valid
                if "username" in upd_user:
                    if not check_length(upd_user["username"], 1, 50):
                        return Response("Username must be between 1 and 50 characters", mimetype="text/plain", status=400)

                    #check username exists in db
                    check_username_exists = db_index_fetchone("SELECT EXISTS(SELECT username FROM user WHERE username=?)", [upd_user["username"]])

                    if check_username_exists == 1:
                        return Response("Username already exists", mimetype="text/plain", status=400)

                    #runs update query if all username checks pass
                    db_commit("UPDATE user u INNER JOIN user_session s ON u.id = s.user_id SET username=? WHERE login_token=?", [upd_user["username"], token])

                #check bio valid
                if "bio" in upd_user:
                    if not check_length(upd_user["bio"], 1, 70):
                        return Response("Bio must be between 1 and 70 characters", mimetype="text/plain", status=400)
                    
                    #runs update query if bio check passes
                    db_commit("UPDATE user u INNER JOIN user_session s ON u.id = s.user_id SET bio=? WHERE login_token=?", [upd_user["bio"], token])

                #check birthdate valid
                if "birthdate" in upd_user:
                    if not check_length(upd_user["birthdate"], 1, 30):
                        return Response("Birthdate value must be between 1 and 30 characters", mimetype="text/plain", status=400)

                    #runs update query if birthdate check passes
                    db_commit("UPDATE user u INNER JOIN user_session s ON u.id = s.user_id SET birthdate=? WHERE login_token=?", [upd_user["birthdate"], token])

                #checks if urls are valid format
                if "imageUrl" in upd_user:
                    if validators.url(upd_user["imageUrl"]) and len(upd_user["imageUrl"]) <= 200:
                        #runs update query if imageUrl check passes
                        db_commit("UPDATE user u INNER JOIN user_session s ON u.id = s.user_id SET image_url=? WHERE login_token=?", [upd_user["imageUrl"], token])

                if "bannerUrl" in upd_user:
                    if validators.url(upd_user["bannerUrl"]) and len(upd_user["bannerUrl"]) <= 200:
                        #runs update query if bannerUrl check passes
                        db_commit("UPDATE user u INNER JOIN user_session s ON u.id = s.user_id SET banner_url=? WHERE login_token=?", [upd_user["bannerUrl"], token])
                
                #get updated user info
                updated = db_fetchone("SELECT u.id, email, username, bio, birthdate, image_url, banner_url FROM user u INNER JOIN user_session s ON u.id = s.user_id WHERE login_token=?", [token])
                resp = pop_dict_query(updated)
                
                return Response(json.dumps(resp), mimetype="application/json", status=200)
            
            else:
                return Response("Invalid Login Token", mimetype="text/plain", status=400)
        else:
            return Response("A login token is required", mimetype="text/plain", status=400)

    elif request.method == 'DELETE':
        data =  request.json

        if len(data.keys()) == 2:
            #check if proper keys are sent
            if {"loginToken", "password"} <= data.keys():
                token = data.get("loginToken")
                password = data.get("password")

                if token != None:
                    token_valid = db_index_fetchone("SELECT EXISTS(SELECT login_token from user_session WHERE login_token=?)", [token])

                    if token_valid == 1:
                        #checks if user assigned to token has matching password (also grabs id for easy delete if future checks pass)
                        compare_tbl = db_fetchone("SELECT login_token, password, u.id FROM user u INNER JOIN user_session s ON u.id = s.user_id WHERE login_token=?", [token])
                        
                        #checks password in returned tuple with password sent by client
                        if password == compare_tbl[1]:
                            db_commit("DELETE FROM user WHERE id=?", [compare_tbl[2]])
                            return Response(status=204)
                        else:
                            return Response("Credentials do not match, can't delete", mimetype="text/plain", status=400)                    
                    else:
                        return Response("Invalid Login Token", mimetype="text/plain", status=400)
                else: 
                    return Response("Invalid Login Token", mimetype="text/plain", status=400)
            else:
                return Response("Invalid Json Data. Check keys", mimetype="text/plain", status=400)
        else:
            return Response("Invalid amount of data", mimetype="text/plain", status=400)
    else:
        print("Something went wrong, bad request method")
        return Response("Method Not Allowed", mimetype='text/plain', status=405)

