from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["merlin_taskifier"]


def save_login_to_mongo(login_data: dict):
    for collection_name in db.list_collection_names():
        db[collection_name].delete_many({})

    collection = db["logins"]
    collection.replace_one(
        {"userid": login_data["userid"]},
        login_data,
        upsert=True
    )


def get_login_by_userid(userid: str):
    return db["logins"].find_one({"userid": str(userid)})


def save_notifications_to_mongo(userid: str, notifications: list):
    db["notifications"].delete_many({"userid": userid})
    for n in notifications:
        n["userid"] = userid
    db["notifications"].insert_many(notifications)


def get_notifications_by_userid(userid: str):
    return list(db["notifications"].find({"userid": str(userid)}))


def save_student_tasks(tasks: list, userid: str = None):
    if userid:
        db["tasks"].delete_many({"userid": userid})
        for task in tasks:
            task["userid"] = userid
    else:
        db["tasks"].delete_many({})
    db["tasks"].insert_many(tasks)


def get_all_student_tasks():
    tasks = list(db["student_tasks"].find())
    for task in tasks:
        task["_id"] = str(task["_id"])  # Fix za ObjectId
    return tasks



def get_tasks_by_userid(userid: str):
    tasks = list(db["tasks"].find({"userid": str(userid)}))
    for task in tasks:
        task["_id"] = str(task["_id"])
    return tasks

def get_student_tasks_by_userid(userid: str):
    tasks = list(db["student_tasks"].find({"userid": str(userid)}))
    for task in tasks:
        task["_id"] = str(task["_id"])
    return tasks


def save_student_tasks_to_mongo(student_tasks: list, userid: str = None):
    if not userid:
        print("❌ Nedostaje userid za spremanje student_tasks.")
        return

    # Obriši stare zadatke za korisnika
    db["student_tasks"].delete_many({"userid": userid})

    # Dodaj userid svakom zadatku i spremi
    for task in student_tasks:
        task["userid"] = userid

    db["student_tasks"].insert_many(student_tasks)

def save_tasks_to_mongo(tasks, userid: str):
    if tasks:
        for task in tasks:
            task["userid"] = userid
        db["tasks"].delete_many({"userid": userid})
        db["tasks"].insert_many(tasks)


def save_dinp_links_to_mongo(links: list):
    db["dinp_pdfs"].delete_many({})  # očisti staro
    if links:
        db["dinp_pdfs"].insert_many(links)

def get_dinp_pdf_links():
    return list(db["dinp_pdfs"].find())

def save_dinp_tasks(tasks: list):
    db["dinp_tasks"].delete_many({})
    db["dinp_tasks"].insert_many(tasks)

def get_dinp_tasks_by_userid(userid: str):
    tasks = list(db["dinp_tasks"].find({"user_id": str(userid)}))
    for task in tasks:
        task["_id"] = str(task["_id"])
    return tasks