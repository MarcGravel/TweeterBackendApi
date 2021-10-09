from app_package import app
import dbcreds
import mariadb
from flask import Flask, request, Response
import json
import re #re provides support for regular expressions
import secrets #package to create session token strings
import validators #validates URLs

@app.route('/api/users', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def api_users():
    try:
        conn = mariadb.connect(
                        user=dbcreds.user,
                        password=dbcreds.password,
                        host=dbcreds.host,
                        port=dbcreds.port,
                        database=dbcreds.database
                        )
        cursor = conn.cursor()

        if request.method == 'GET':
            params = request.args

            # checks length of json dict (2 different requests are accepted), if values do not match correct amount, returns error message
            if len(params.keys()) == 0:
                cursor.execute("SELECT id, email, username, bio, birthdate, image_url, banner_url FROM user")
                all_users = cursor.fetchall()
                all_user_list = []

                #adds all users to a dictionary to return
                for u in all_users:
                    user = pop_dict_query(u)
                    all_user_list.append(user)

                return Response(json.dumps(all_user_list), mimetype="application/json", status=200)
            
            #if client sends over a userid param. checks proper key amount and then key name
            elif len(params.keys()) == 1:
                if {"userId"} <= params.keys():
                    paramId = params.get("userId")

                    #checks if is valid number
                    if paramId.isdigit() == False:
                        return Response("Not a valid id number", mimetype="text/plain", status=400)

                    #checks if param id exists as a user id in DB
                    #if not exists, returns 0. If exists, returns one. 
                    cursor.execute("SELECT EXISTS(SELECT * FROM user WHERE id=?)", [paramId])
                    check_id_valid = cursor.fetchone()[0]

                    #handles response of EXISTS query
                    if check_id_valid == 1:
                        cursor.execute("SELECT id, email, username, bio, birthdate, image_url, banner_url FROM user WHERE id=?", [paramId])
                        sel_usr = cursor.fetchone()

                        resp = pop_dict_query(sel_usr)

                        return Response(json.dumps(resp), mimetype="application/json", status=200)
                    else:
                        return Response("user id does not exist", mimetype="text/plain", status=400)
                else:
                    print("Incorrect data submitted. Check key")
                    return Response("Incorrect keys submitted.", mimetype='text/plain', status=400)
            else:
                print("Too much JSON data submitted")
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
                    print("Incorrect data submitted. Check keys")
                    return Response("Incorrect keys submitted.", mimetype='text/plain', status=400)
            else: 
                return Response("Not a valid number of arguments sent", mimetype="text/plain", status=400)

            #check email valid and proper character count
            if not check_email(new_user["email"]):
                return Response("Not a valid email address", mimetype="text/plain", status=400)

            #check email length
            if not check_length(new_user["email"], 1, 40):
                return Response("Email is too long", mimetype="text/plain", status=400)

            #check email exists in db
            cursor.execute("SELECT EXISTS(SELECT email FROM user WHERE email=?)", [new_user["email"]])
            check_email_exists = cursor.fetchone()[0]

            if check_email_exists == 1:
                return Response("Email already exists", mimetype="text/plain", status=400)

            #check username valid
            if not check_length(new_user["username"], 1, 50):
                return Response("Username must be between 1 and 50 characters", mimetype="text/plain", status=400)

            #check username exists in db
            cursor.execute("SELECT EXISTS(SELECT username FROM user WHERE username=?)", [new_user["username"]])
            check_username_exists = cursor.fetchone()[0]

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
            cursor.execute("INSERT INTO user(email, username, password, bio, birthdate) \
                            VALUES(?,?,?,?,?)", [new_user["email"], new_user["username"], 
                                new_user["password"], new_user["bio"], new_user["birthdate"]])
            conn.commit()

            cursor.execute("SELECT id FROM user WHERE email=?", [new_user["email"]])
            user_id = cursor.fetchone()[0]

            #checks if client sent info for image or banner url, checks validity of url links then updates.
            if new_user["imageUrl"] != "None":
                if not validators.url(new_user["imageUrl"]): 
                    cursor.execute("UPDATE user SET image_url=? WHERE id=?", [new_user["imageUrl"], user_id])
                    conn.commit()
                
            if new_user["bannerUrl"] != "None":
                if not validators.url(new_user["bannerUrl"]):
                    cursor.execute("UPDATE user SET banner_url=? WHERE id=?", [new_user["bannerUrl"], user_id])
                    conn.commit()

            #create session token and add token/user to session table
            login_token = secrets.token_urlsafe(16)
            cursor.execute("INSERT INTO user_session(user_id, login_token) VALUES(?,?)", [user_id, login_token])
            conn.commit()
            
            #get all data from tables and return a response
            cursor.execute("SELECT id, email, username, bio, birthdate, image_url, banner_url FROM user WHERE id=?", [user_id])
            usr = cursor.fetchone()

            #populates dict and then adds the login token
            resp = pop_dict_query(usr)   
            resp["loginToken"] = login_token 

            return Response(json.dumps(resp), mimetype="application/json", status=201)

        elif request.method == 'PATCH':
            data = request.json
            token = data.get("loginToken")

            if token != None:
                cursor.execute("SELECT EXISTS(SELECT login_token from user_session WHERE login_token=?)", [token])
                token_valid = cursor.fetchone()[0]
                
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
                        cursor.execute("SELECT EXISTS(SELECT email FROM user WHERE email=?)", [upd_user["email"]])
                        check_email_exists = cursor.fetchone()[0]

                        if check_email_exists == 1:
                            return Response("Email already exists", mimetype="text/plain", status=400)

                        #runs update query if all email checks pass
                        cursor.execute("UPDATE user u INNER JOIN user_session s ON u.id = s.user_id SET email=? WHERE login_token=?", [upd_user["email"], token])
                        conn.commit()

                    #check username valid
                    if "username" in upd_user:
                        if not check_length(upd_user["username"], 1, 50):
                            return Response("Username must be between 1 and 50 characters", mimetype="text/plain", status=400)

                        #check username exists in db
                        cursor.execute("SELECT EXISTS(SELECT username FROM user WHERE username=?)", [upd_user["username"]])
                        check_username_exists = cursor.fetchone()[0]

                        if check_username_exists == 1:
                            return Response("Username already exists", mimetype="text/plain", status=400)

                        #runs update query if all username checks pass
                        cursor.execute("UPDATE user u INNER JOIN user_session s ON u.id = s.user_id SET username=? WHERE login_token=?", [upd_user["username"], token])
                        conn.commit()

                    #check bio valid
                    if "bio" in upd_user:
                        if not check_length(upd_user["bio"], 1, 70):
                            return Response("Bio must be between 1 and 70 characters", mimetype="text/plain", status=400)
                        
                        #runs update query if bio check passes
                        cursor.execute("UPDATE user u INNER JOIN user_session s ON u.id = s.user_id SET bio=? WHERE login_token=?", [upd_user["bio"], token])
                        conn.commit()

                    #check birthdate valid
                    if "birthdate" in upd_user:
                        if not check_length(upd_user["birthdate"], 1, 30):
                            return Response("Birthdate value must be between 1 and 30 characters", mimetype="text/plain", status=400)

                        #runs update query if birthdate check passes
                        cursor.execute("UPDATE user u INNER JOIN user_session s ON u.id = s.user_id SET birthdate=? WHERE login_token=?", [upd_user["birthdate"], token])
                        conn.commit()

                    #checks if urls are valid format
                    if "imageUrl" in upd_user:
                        if not validators.url(upd_user["imageUrl"]):
                            return Response("Not a valid Url for image", mimetype="text/plain", status=400)
                        
                        #runs update query if imageUrl check passes
                        cursor.execute("UPDATE user u INNER JOIN user_session s ON u.id = s.user_id SET image_url=? WHERE login_token=?", [upd_user["imageUrl"], token])
                        conn.commit()

                    if "bannerUrl" in upd_user:
                        if not validators.url(upd_user["bannerUrl"]):
                            return Response("Not a valid Url for banner", mimetype="text/plain", status=400)

                        #runs update query if bannerUrl check passes
                        cursor.execute("UPDATE user u INNER JOIN user_session s ON u.id = s.user_id SET banner_url=? WHERE login_token=?", [upd_user["bannerUrl"], token])
                        conn.commit()
                    
                    #get updated user info
                    cursor.execute("SELECT u.id, email, username, bio, birthdate, image_url, banner_url FROM user u INNER JOIN user_session s ON u.id = s.user_id WHERE login_token=?", [token])
                    updated = cursor.fetchone()
                    resp = pop_dict_query(updated)
                    
                    return Response(json.dumps(resp), mimetype="application/json", status=200)
                
                else:
                    print("Token does not exist in db")
                    return Response("Invalid Login Token", mimetype="text/plain", status=400)

            else:
                print("No login token") 
                return Response("A login token is required", mimetype="text/plain", status=400)

        elif request.method == 'DELETE':
            data =  request.json

            if len(data.keys()) == 2:
                #check if proper keys are sent
                if {"loginToken", "password"} <= data.keys():
                    token = data.get("loginToken")
                    password = data.get("password")

                    if token != None:
                        cursor.execute("SELECT EXISTS(SELECT login_token from user_session WHERE login_token=?)", [token])
                        token_valid = cursor.fetchone()[0]

                        if token_valid == 1:
                            #checks if user assigned to token has matching password (also grabs id for easy dlete if future checks pass)
                            cursor.execute("SELECT login_token, password, u.id FROM user u INNER JOIN user_session s ON u.id = s.user_id WHERE login_token=?", [token])
                            compare_tbl = cursor.fetchone()
                            
                            #checks password in returned tuple with password sent by client
                            if password == compare_tbl[1]:
                                cursor.execute("DELETE FROM user WHERE id=?", [compare_tbl[2]])
                                conn.commit()
                                return Response(status=204)
                            else:
                                return Response("Credentials do not match, can't delete", mimetype="text/plain", status=400)
                        
                        else:
                            print("Token does not exist in db")
                            return Response("Invalid Login Token", mimetype="text/plain", status=400)
                    
                else:
                    return Response("Invalid Json Data. Check keys", mimetype="text/plain", status=400)
            
            else:
                return Response("Invalid amount of data", mimetype="text/plain", status=400)

        else:
            print("Something went wrong, bad request method")
            return Response("Method Not Allowed", mimetype='text/plain', status=405)

    except mariadb.DataError:
        print("Something is wrong with your data")
        return Response("Something is wrong with the data", mimetype='text/plain', status=404)
    except mariadb.OperationalError:
        print("Something is wrong with your connection")
        return Response("Something is wrong with the connection", mimetype='text/plain', status=500)
    except:
        print("Something went wrong")
        return Response("Something went wrong", status=500)
    
    finally:
        if (cursor != None):
            cursor.close()
        if (conn != None):
            conn.rollback()
            conn.close()


# Regular expression for email string
def check_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False

#checks length is valid on input
def check_length(input, min_len, max_len):
    if len(input) >= min_len and len(input) <= max_len:
        return True
    else:
        return False

#populates dict FROM SQL QUERY tuples or lists
def pop_dict_query(data):
    user = {
        "userId": data[0],
        "email": data[1],
        "username": data[2],
        "bio": data[3],
        "birthdate": data[4],
        "imageUrl": data[5],
        "bannerUrl": data[6] 
    }
    return user

#populates dict FROM JSON DATA REQ and removes leading and trailing whitespaces
def pop_dict_req(data):
    new_dict = {
    }
    for k, v in data.items():
        new_dict[k] = str(v).strip()

    return new_dict

#checks json request for allowed keys only
def allowed_data(data, allowed_keys):
    for key in list(data.keys()):
                if key not in allowed_keys:
                    del data[key]
    return data
