from app_package import app
import dbcreds
import mariadb
from flask import Flask, request, Response
import json
# re provides support for regular expressions
import re
import secrets

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
                cursor.execute("SELECT id, email, username, bio, birthdate, imageUrl, bannerUrl FROM user")
                all_users = cursor.fetchall()
                all_user_Dict = []

                #adds all users to a dictionary to return
                for u in all_users:
                    user = {
                        "userId": u[0],
                        "email": u[1],
                        "username": u[2],
                        "bio": u[3],
                        "birthdate": u[4],
                        "imageUrl": u[5],
                        "bannerUrl": u[6] 
                    }
                    all_user_Dict.append(user)

                return Response(json.dumps(all_user_Dict), mimetype="application/json", status=200)
            
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
                        cursor.execute("SELECT id, email, username, bio, birthdate, imageUrl, bannerUrl FROM user WHERE id=?", [paramId])
                        sel_usr = cursor.fetchone()

                        resp = {
                            "userId": sel_usr[0],
                            "email": sel_usr[1],
                            "username": sel_usr[2],
                            "bio": sel_usr[3],
                            "birthdate": sel_usr[4],
                            "imageUrl": sel_usr[5],
                            "bannerUrl": sel_usr[6] 
                        }

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
            new_user = {

            }
            
            if len(data.keys()) == 5 or len(data.keys()) == 6 or len(data.keys()) == 7: 
                if {"email", "username", "password", "bio", "birthdate"} <= data.keys() or \
                        {"email", "username", "password", "bio", "birthdate", "imageUrl"} <= data.keys() or \
                            {"email", "username", "password", "bio", "birthdate", "bannerUrl"} <= data.keys() or \
                                {"email", "username", "password", "bio", "birthdate", "imageUrl", "bannerUrl"} <= data.keys():

                        #.strip() will remove all leading and trailing whitespace    
                        new_user = {
                            "email": str(data.get("email")).strip(),
                            "username": str(data.get("username")).strip(),
                            "password": str(data.get("password")).strip(),
                            "bio": str(data.get("bio")).strip(),
                            "birthdate": data.get("birthdate"),
                            "imageUrl": str(data.get("imageUrl")).strip(),
                            "bannerUrl": str(data.get("bannerUrl")).strip()
                        }
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
                return Response("Password must be between 1 and 70 characters", mimetype="text/plain", status=400)

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
            print(user_id)

            #checks if client sent info for image or banner url and updates if required
            if new_user["imageUrl"] != "None":
                cursor.execute("UPDATE user SET image_url=? WHERE id=?", [new_user["imageUrl"], user_id])
                conn.commit()
                
            if new_user["bannerUrl"] != "None":
                cursor.execute("UPDATE user SET banner_url=? WHERE id=?", [new_user["bannerUrl"], user_id])
                conn.commit()

            #create session token and add token/user to session table
            login_token = secrets.token_urlsafe(16)
            cursor.execute("INSERT INTO user_session(user_id, login_token) VALUES(?,?)", [user_id, login_token])
            conn.commit()
            
            #get all data from tables and return a response
            cursor.execute("SELECT id, email, username, bio, birthdate, image_url, banner_url FROM user WHERE id=?", [user_id])
            usr = cursor.fetchone()
    
            resp = {
                "userId": usr[0],
                "email": usr[1],
                "username": usr[2],
                "bio": usr[3],
                "birthdate": usr[4],
                "imageUrl": usr[5],
                "bannerUrl": usr[6],
                "loginToken": login_token 
            }

            return Response(json.dumps(resp), mimetype="application/json", status=201)

        elif request.method == 'PATCH':
            pass

        elif request.method == 'DELETE':
            pass

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
        return Response("Something went wrong", mimetype='text/plain', status=500)
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
