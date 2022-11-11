from pymongo import MongoClient
from gridfs import *
import os

cluster = MongoClient("mongodb://localhost:27017")
db = cluster["user_storage"]
collection = db["test"]
file_dict={
    "filename":"test",
    "filesize":100
}
filename="C:\\Users\\88696\\Dropbox\\我的電腦 (LAPTOP-SVUIPIGO)\\Desktop\\性格測試.pdf"
fsize = os.path.getsize(filename)
file_dict["filesize"] = fsize/1024
with open(filename,'rb') as f:
    file_data = f.read()
    file_dict["filedata"] = file_data
    file_dict["filename"] = filename
    file = collection.insert_one(file_dict)
print(file)
