from app_package import app
import dbcreds
import mariadb
from flask import Flask, request, Response
import json
# re provides support for regular expressions
import re

@app.route('/api/users')
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
                
            elif len(params.keys()) == 1:
                if {"userId"} <= params.keys():
                    paramId = params.get("userId")

                    cursor.execute("SELECT EXISTS(SELECT * FROM user WHERE id=?)", [paramId])
                    check_id_valid = cursor.fetchone()[0]

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
                    return Response("Incorrect key values submitted.", mimetype='text/plain', status=400)
            else:
                print("Too much JSON data submitted")
                return Response("Too much data submitted", mimetype='text/plain', status=400)
                
        elif request.method == 'POST':
            pass
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
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
def check_email(email):
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False