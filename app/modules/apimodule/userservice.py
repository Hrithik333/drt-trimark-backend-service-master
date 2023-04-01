import datetime
import random
import string

import jwt
import mysql
import mysql.connector
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

from app.model.User import User

connection = MongoClient("mongodb+srv://drttrimark:drttrimark31012023@drttrimark.ylmqj.mongodb.net/?retryWrites=true&w=majority")
#connection = MongoClient("mongodb+srv://root:root@cluster0.jinb4pq.mongodb.net/?retryWrites=true&w=majority")

class UserService:
    def __init__(self):
        pass

    @staticmethod
    def register(req):
        character_length = 16
        res = ''.join(random.choices(string.ascii_uppercase + string.digits, k=character_length))
        user_id = str(res)
        firstname = req["firstname"]
        lastname = req["lastname"]
        user_role = req["user_role"]
        password = req["password"]
        email = req["email"]
        hashed_password = generate_password_hash(password, method='sha256')
        to_be_inserted = {"_id": user_id, "firstname": firstname, "lastname": lastname, "user_role": user_role,
                          "email": email, "user_password": hashed_password}
        collections = connection.drt_trimark["user_details"]
        to_be_checked = {"email": email}
        response = collections.find_one(to_be_checked)
        if response is None:
            collections.insert_one(to_be_inserted)
            if req["user_role"] == "Reporting":
                collections = connection.drt_trimark["user_access"]
                use_cases = req["use_cases"]
                collections.insert_one({"_id": user_id, "use_cases": use_cases})
            return "User Successfully Created"
        else:
            return "Email already exists"

    @staticmethod
    def login(req):
        response = {}
        email = req["email"]
        user_pass = req["password"]
        mydb = mysql.connector.connect(
            host="ac1aa41ef8c434e959e8dde38ea6dca6-782152459.us-east-1.elb.amazonaws.com",
            user="root",
            password="trimarkdrt",
            database="user_details_database"
        )
        cursor = mydb.cursor(dictionary=True)
        cursor.execute('SELECT * FROM user_details WHERE email = %s', (email,))
        record = cursor.fetchone()
        # to_fetch = {"email": email}
        # collections = connection.drt_trimark["user_details"]
        # record = collections.find_one(to_fetch)
        if record is not None:
            if check_password_hash(record["password"], user_pass):
                user_id = record["id"]
                response["user_role"] = record["user_role"]
                response["display_name"] = record["firstname"] + " " + record["lastname"]
                response["status"] = "SUCCESS"
                response["message"] = "Login Successful"
                response["token"] = jwt.encode(
                    {'public_id': record["id"], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)},
                    "fmaihds76sa786d98siaohdn", "HS256")
                if response["user_role"] == "Admin":
                    collections = connection.drt_trimark["use_cases"]
                    docs = collections.find()
                    access = []
                    for record in docs:
                        access.append({"use_case_id": record["id"], "use_case_name": record["name"]})
                    response["use_cases"] = access
                elif response["user_role"] == "Reporting":
                    collections = connection.drt_trimark["user_access"]
                    doc = collections.find_one({"_id": user_id})
                    use_cases = doc["use_cases"]
                    collections = connection.drt_trimark["use_cases"]
                    access = []
                    for use_case in use_cases:
                        docs = collections.find_one({"id": str(use_case)})
                        access.append({"use_case_id": use_case, "use_case_name": docs["name"]})
                    response["use_cases"] = access
                collections = connection.drt_trimark["user_saved_config"]
                record = collections.find_one({"_id": user_id})
                saved_configs = []
                use_case_names_access = []
                for a in access:
                    use_case_names_access.append(a["use_case_name"])
                if record is not None:
                    configs = record["configs"]
                    for k, v in configs.items():
                        if k in use_case_names_access:
                            saved_configs.append({"use_case": k, "configs": list(v.keys())})
                response["saved_configs"] = saved_configs
            else:
                response["status"] = "FAILURE"
                response["message"] = "Invalid Password"
        else:
            response["status"] = "FAILURE"
            response["message"] = "User does not exist."
        return response

    def get_user_by_id(user_id):
        mydb = mysql.connector.connect(
            host="ac1aa41ef8c434e959e8dde38ea6dca6-782152459.us-east-1.elb.amazonaws.com",
            user="root",
            password="trimarkdrt",
            database="user_details_database"
        )
        cursor = mydb.cursor(dictionary=True)
        cursor.execute('SELECT * FROM user_details WHERE id = %s', (user_id,))
        record = cursor.fetchone()
        if record is None:
            return None
        else:
            fname = record["firstname"]
            lname = record["firstname"]
            username = record["email"]
            user = User(fname, lname, username)
            return user

    @staticmethod
    def get_saved_user_config(jwt_token):
        data = jwt.decode(jwt_token, "fmaihds76sa786d98siaohdn", algorithms=["HS256"])
        user_id = data["public_id"]
        #collections = connection.drt_trimark["user_details"]
        #to_fetch = {"_id": user_id}
        #record = collections.find_one(to_fetch)
        mydb = mysql.connector.connect(
            host="ac1aa41ef8c434e959e8dde38ea6dca6-782152459.us-east-1.elb.amazonaws.com",
            user="root",
            password="trimarkdrt",
            database="user_details_database"
        )
        cursor = mydb.cursor(dictionary=True)
        cursor.execute('SELECT * FROM user_details WHERE id ={}'.format(user_id))
        record = cursor.fetchone()
        role = record["user_role"]
        if role == "Admin":
            collections = connection.drt_trimark["use_cases"]
            docs = collections.find()
            access = []
            for record in docs:
                access.append({"use_case_id": record["id"], "use_case_name": record["name"]})
        elif role == "Reporting":
            collections = connection.drt_trimark["user_access"]
            doc = collections.find_one({"_id": user_id})
            use_cases = doc["use_cases"]
            collections = connection.drt_trimark["use_cases"]
            access = []
            for use_case in use_cases:
                docs = collections.find_one({"id": str(use_case)})
                access.append({"use_case_id": use_case, "use_case_name": docs["name"]})
        collections = connection.drt_trimark["user_saved_config"]
        user_id = str(user_id)
        record = collections.find_one({"user_id": user_id})
        saved_configs = []
        use_case_names_access = []
        for a in access:
            use_case_names_access.append(a["use_case_name"])
        if record is not None:
            configs = record["configs"]
            for k, v in configs.items():
                if k in use_case_names_access:
                    saved_configs.append({"use_case": k, "configs": list(v.keys())})
        return saved_configs
