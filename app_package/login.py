from app_package import app
from app_package.users import pop_dict_query
from app_package.users import check_email
from app_package.queryFunctions import db_commit, db_fetchone, db_index_fetchone
from flask import request, Response
import secrets #package to create session token strings
import json

@app.route('/api/login', methods=['POST', 'DELETE'])
def api_login():

    #response object for return
    response = None

    if request.method == 'POST':
        data = request.json
        # checks length of json dict, if values do not match correct amount, returns error message
        if len(data.keys()) == 2:
            # checks proper keys are submitted, if yes then query database for matching email and password
            if {"email", "password"} <= data.keys():
                email = data.get("email")
                password = data.get("password")

                #checks if valid email string before querying db
                if not check_email(email):
                    response = Response("Not a valid email", mimetype="text/plain", status=400)

                email_valid = db_index_fetchone("SELECT EXISTS(SELECT email FROM user WHERE email=?)", [email])

                #email_valid returns a 1 if email exists in db, and a 0 if not
                if email_valid == 1:
                    db_pass = db_index_fetchone("SELECT password FROM user WHERE email=?", [email])
                    
                    # if matching, generate a login token, store it in user session and return success message with token and all user data
                    if db_pass == password:
                        usr = db_fetchone("SELECT id, email, username, bio, birthdate, image_url, banner_url FROM user WHERE email=?", [email])
                        login_token = secrets.token_urlsafe(16)
                        
                        #response data populate dict and add token   
                        resp = pop_dict_query(usr)
                        resp["loginToken"] = login_token

                        #add token to user session
                        db_commit("INSERT INTO user_session(user_id, login_token) VALUES(?,?)", [usr[0], login_token])

                        response = Response(json.dumps(resp), mimetype="application/json", status=201)

                    else:
                        response = Response("Invalid credentials.", mimetype='text/plain', status=400)
                else:
                    response = Response("Email does not exist in database", mimetype="text/plain", status=400)

            elif {"username", "password"} <= data.keys():
                username = data.get("username")
                password = data.get("password")
                
                #checks if username exists
                username_valid = db_index_fetchone("SELECT EXISTS(SELECT email FROM user WHERE username=?)", [username])

                #username_valid returns a 1 if username exists in db, and a 0 if not
                if username_valid == 1:
                    db_pass = db_index_fetchone("SELECT password FROM user WHERE username=?", [username])

                    # if matching, generate a login token, store it in user session and return success message with token and all user data
                    if db_pass == password:
                        usr = db_fetchone("SELECT id, email, username, bio, birthdate, image_url, banner_url FROM user WHERE username=?", [username])
                        login_token = secrets.token_urlsafe(16)
                        
                        #response data populate dict and add token   
                        resp = pop_dict_query(usr)
                        resp["loginToken"] = login_token

                        #add token to user session
                        db_commit("INSERT INTO user_session(user_id, login_token) VALUES(?,?)", [usr[0], login_token])

                        response = Response(json.dumps(resp), mimetype="application/json", status=201)

                    else:
                        response = Response("Invalid credentials.", mimetype='text/plain', status=400)
                else:
                    response = Response("Username does not exist in database", mimetype="text/plain", status=400)
            else:
                response = Response("Incorrect keys submitted.", mimetype='text/plain', status=400)
        else:
            response = Response("Error, Expected 2 arguments", mimetype='text/plain', status=400)    

    elif request.method == 'DELETE':
        data = request.json
        
        # checks length of json dict, if values do not match correct amount, returns error message
        if len(data.keys()) == 1:
            
            # checks proper keys are submitted, if yes then query database for matching email and password
            if {"loginToken"} <= data.keys():
                token = data.get("loginToken")
                check_token = db_index_fetchone("SELECT EXISTS(SELECT * FROM user_session WHERE login_token=?)", [token])
                
                #if the token value exists, cursor has return a 1, so we check if value is 1 or 0
                if check_token == 1:
                    db_commit("DELETE FROM user_session WHERE login_token=?", [token])
                    response = Response(status=204)
                else:
                    response = Response("Token is not valid", mimetype="text/plain", status=400)
            else:
                response = Response("Incorrect Json key, login token required", mimetype='text/plain', status=400) 
        else:
            response = Response("Incorrect Json Data", mimetype='text/plain', status=400)

    else:
        print("Something went wrong, bad request method")
        response = Response("Method Not Allowed", mimetype='text/plain', status=405)

    return response
        