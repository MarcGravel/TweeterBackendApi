from app_package import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import secrets
import json

@app.route('/api/login', methods=['POST', 'DELETE'])
def api_login():
    try:
        conn = mariadb.connect(
                        user=dbcreds.user,
                        password=dbcreds.password,
                        host=dbcreds.host,
                        port=dbcreds.port,
                        database=dbcreds.database
                        )
        cursor = conn.cursor()

        if request.method == 'POST':
            data = request.json
            # checks length of json dict, if values do not match correct amount, returns error message
            if len(data.keys()) == 2:
                # checks proper keys are submitted, if yes then query database for matching email and password
                if {"email", "password"} <= data.keys():
                    email = data.get("email")
                    password = data.get("password")

                    cursor.execute("SELECT password FROM user WHERE email=?", [email])
                    db_pass = cursor.fetchone()[0]
                    
                    # if matching, generate a login token, store it in user session and return success message with token and all user data
                    if db_pass == password:
                        cursor.execute("SELECT id, email, username, bio, birthdate, imageUrl, bannerUrl FROM user WHERE email=?", [email])
                        usr = cursor.fetchone()
                        login_token = secrets.token_urlsafe(16)
                        
                        #response data    
                        resp = {
                            "userId": usr[0],
                            "email": usr[1],
                            "username": usr[2],
                            "bio": usr[3],
                            "birthdate": usr[4],
                            "loginToken": login_token,
                            "imageUrl": usr[5],
                            "bannerUrl": usr[6] 
                        }

                        #add token to user session
                        cursor.execute("INSERT INTO user_session(user_id, login_token) VALUES(?,?)", [usr[0], login_token])
                        conn.commit()

                        return Response(json.dumps(resp), mimetype="application/json", status=201)
                    else:
                        return Response("Invalid credentials.", mimetype='text/plain', status=400)
                else:
                    print("Incorrect data submitted. Check key values")
                    return Response("Incorrect key values submitted.", mimetype='text/plain', status=400)

            elif len(data.keys()) > 2:
                print("Too much JSON data submitted")
                return Response("Too much data submitted", mimetype='text/plain', status=400)    
            elif len(data.keys()) < 2:
                print("Missing JSON data")
                return Response("Missing Json data", mimetype='text/plain', status=400)

        elif request.method == "DELETE":
            data = request.json
            
            # checks length of json dict, if values do not match correct amount, returns error message
            if len(data.keys()) == 1:
                
                # checks proper keys are submitted, if yes then query database for matching email and password
                if {"loginToken"} <= data.keys():
                    token = data.get("loginToken")
                    cursor.execute("SELECT * FROM user_session WHERE login_token=?", [token])
                    check_token = cursor.fetchone()
                    
                    if check_token != None:

                        cursor.execute("DELETE FROM user_session WHERE login_token=?", [token])
                        conn.commit()
                        return Response(status=204)
                    else:
                        return Response("Token is not valid", mimetype="text/plain", status=400)
                else:
                    print("Incorrect Json key value")
                    return Response("Incorrect Json key, login token required", mimetype='text/plain', status=400) 
            else:
                print("Incorrect Json data amount")
                return Response("Incorrect Json Data", mimetype='text/plain', status=400)

        else:
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
