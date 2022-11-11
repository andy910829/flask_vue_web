from pymongo import MongoClient
import schedule
from datetime import datetime
import time

class verification_code:
    def __init__(self,account="",code="",user_code=""):
        self.cluster = MongoClient("mongodb://localhost:27017")
        self.db = self.cluster["user_storage"]
        self.collection = self.db["verification_code"]
        self.account=account
        self.user_code=user_code
        self.code=code
    
    def delete_code_everyday(self):
        schedule.every().day.at("03:00").do(self.delete_all)

    def create(self):
        dead_time = int(time.time() + (15*60))
        user=self.collection.find_one({"account":self.account})
        info={
                "account":self.account,
                "code":self.code,
                "dead_time":dead_time
            }
        if user == None:
            self.collection.insert_one(info)
        else:
            self.collection.update_one({"account":self.account},{"$set":info})


    def get_code(self):
        user=self.collection.find_one({"account":self.account})
        code = user['code']
        dead_time =  user["dead_time"]
        return code, dead_time

    def delete(self):
        self.collection.delete_one({"account":self.account})
        return True

    def delete_all(self):
        self.collection.delete_many()
        return True

class admin:
    def __init__(self,acedemic_year="",time_line="",current_acedemic_year=""):
        self.cluster = MongoClient("mongodb://localhost:27017")
        self.db = self.cluster["user_storage"]
        self.collection = self.db["info"]
        self.acedemic_year=acedemic_year
        self.current_acedemic_year=current_acedemic_year
        self.timeline = time_line

    def create_acedemic_year_info(self):    #新增第一筆學年度資料，創建一次之後不會再用到
        info={
            "name":"acedemic_year_info",
            "current_acedemic_year":self.current_acedemic_year,
            "acedemic_year_info":{self.acedemic_year:{"time_line":self.timeline}}
        }
        self.collection.insert_one(info)
        return True

    def create_new_acedemic_year(self):   #新增新的學年度資料，包含學年度及時間線資料
        info = self.collection.find_one()
        info["acedemic_year_info"][self.acedemic_year] = {
            "time_line":self.timeline
        }
        self.collection.update_one({"name":"acedemic_year_info"},{"$set":info})
        return True
    
    def update_current_acedemic_year(self):  #提供管理員修改目前的學年度
        info = self.collection.find_one()
        info["current_acedemic_year"] = self.current_acedemic_year
        self.collection.update_one({"name":"acedemic_year_info"},{"$set":info})
        return True

    def get_current_acedemic_year(self):  #回傳目前的學年度
        return self.collection.find_one()["current_acedemic_year"]

if __name__=="__main__":
    verification=verification_code(account='t109360253@ntut.org.tw',code=897654)
    verification.create()
