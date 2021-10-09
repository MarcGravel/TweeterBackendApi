from app_package import app
from app_package.users import pop_dict_query
import dbcreds
import mariadb
from flask import Flask, request, Response
import json

@app.route('/api/follows', methods=['GET', 'POST', 'DELETE'])
def api_follows():
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
            
            #checks that only one param is sent
            if len(params) == 1:
                if {"userId"} <= params.keys():
                    param_id = params.get("userId")

                    #checks if valid positive integer
                    if param_id.isdigit() == False:
                        return Response("Not a valid id number", mimetype="text/plain", status=400)

                    #checks if id exits as a user id. Returns a bool 1 or 0
                    cursor.execute("SELECT EXISTS(SELECT * FROM user WHERE id=?)", [param_id])
                    check_id_valid = cursor.fetchone()[0]

                    #handles bool response
                    if check_id_valid == 1:
                        cursor.execute("SELECT id, email, username, bio, birthdate, image_url, banner_url \
                                        FROM user u INNER JOIN follows f ON u.id = f.followed WHERE f.follower=?", [param_id])
                        all_follows = cursor.fetchall()
                        all_follows_list = []

                        #adds all valid users to a key formatted dict to return
                        for a in all_follows:
                            user = pop_dict_query(a)
                            all_follows_list.append(user)

                        return Response(json.dumps(all_follows_list), mimetype="application/json", status=200)

                    else: 
                        return Response("User id does not exist", mimetype="text/plain", status=400)

                else:
                    print("Incorrect data submitted. Check key")
                    return Response("Incorrect key submitted.", mimetype='text/plain', status=400)
                    
            else:
                print("Did not send correct amount of data")
                return Response("Incorrect amount of data sent", mimetype="text/plain", status=400)

        elif request.method == 'POST':
            data = request.json
            if len(data.keys()) == 2:
                if {"loginToken", "followId"} <= data.keys():
                    token = data.get("loginToken")
                    follow_id = data.get("followId")
                    
                    #checks followId is positive integer
                    if str(follow_id).isdigit() == False:
                        return Response("Not a valid follow id number", mimetype="text/plain", status=400)

                    #checks if token valid
                    if token != None:
                        #checks if token exists. 
                        cursor.execute("SELECT EXISTS(SELECT login_token FROM user_session WHERE login_token=?)", [token])
                        token_valid = cursor.fetchone()[0]

                        if token_valid == 1:
                            #checks followId exists
                            cursor.execute("SELECT EXISTS(SELECT id from user WHERE id=?)", [follow_id])
                            check_follow_id = cursor.fetchone()[0]

                            if check_follow_id == 1:
                                #grabs user_id that matches token 
                                cursor.execute("SELECT user_id FROM user_session WHERE login_token=?", [token])
                                user_id = cursor.fetchone()[0]

                                #checks that user is not trying to follow themselves
                                if user_id == int(follow_id):
                                    return Response("User cannot follow themselves", mimetype="text/plain", status=400)
                                
                                #checks follow relationship doesnt already exist
                                cursor.execute("SELECT EXISTS(SELECT followed FROM follows WHERE followed=? AND follower=?)", [follow_id, user_id])
                                check_rel_exists = cursor.fetchone()[0]
                                
                                if check_rel_exists == 0:
                                    cursor.execute("INSERT INTO follows(follower, followed) VALUES(?,?)", [user_id, follow_id])
                                    conn.commit()
                                    return Response(status=204)

                                else:
                                    return Response("This user is already being followed", mimetype="text/plain", status=400)
                            else:
                                return Response("No user with that id", mimetype="text/plain", status=400)
                        else:
                            return Response("Invalid login token", mimetype="text/plain", status=400)
                    else:
                        return Response("Invalid login token", mimetype="text/plain", status=400)
                else:
                    return Response("Incorrect keys submitted.", mimetype='text/plain', status=400)
            else:
                return Response("Not a valid amount of data sent", mimetype="text/plain", status=400)

        elif request.method == 'DELETE':
            data = request.json
            if len(data.keys()) == 2:
                if {"loginToken", "followId"} <= data.keys():
                    token = data.get("loginToken")
                    follow_id = data.get("followId")

                    #checks followId is positive integer
                    if str(follow_id).isdigit() == False:
                        return Response("Not a valid follow id number", mimetype="text/plain", status=400)
                    
                    #checks if token valid
                    if token != None:
                        #checks if token exists. 
                        cursor.execute("SELECT EXISTS(SELECT login_token FROM user_session WHERE login_token=?)", [token])
                        token_valid = cursor.fetchone()[0]

                        if token_valid == 1:
                            #checks followId exists
                            cursor.execute("SELECT EXISTS(SELECT id from user WHERE id=?)", [follow_id])
                            check_follow_id = cursor.fetchone()[0]

                            if check_follow_id == 1:
                                #grabs user_id that matches token 
                                cursor.execute("SELECT user_id FROM user_session WHERE login_token=?", [token])
                                user_id = cursor.fetchone()[0]

                                #check follow relationship exists
                                cursor.execute("SELECT EXISTS(SELECT follower, followed from follows WHERE \
                                                follower=? AND followed=?)", [user_id, follow_id])
                                rel_exists = cursor.fetchone()[0]

                                if rel_exists == 1:
                                    cursor.execute("DELETE FROM follows WHERE follower=? AND followed=?", [user_id, follow_id])
                                    conn.commit()
                                    return Response(status=204)

                                else:
                                    return Response("User not being followed, cannot unfollow", mimetype="text/plain", status=400)
                            else:
                                return Response("No user with that id", mimetype="text/plain", status=400)
                        else:
                            return Response("Invalid login token", mimetype="text/plain", status=400)
                    else:
                        return Response("Invalid login token", mimetype="text/plain", status=400)
                else:
                    return Response("Incorrect keys submitted.", mimetype='text/plain', status=400)
            else:
                return Response("Not a valid amount of data sent", mimetype="text/plain", status=400)

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