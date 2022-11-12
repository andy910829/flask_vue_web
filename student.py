from bson import json_util
import json
from pymongo import MongoClient
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import uuid
import hashlib
from admin import *
import time


class student_class:
    def __init__(self,act="",pwd=""):
        self.cluster = MongoClient("mongodb://localhost:27017")
        self.db = self.cluster["user_storage"]
        self.collection = self.db["user"]
        self.account = act.replace(" ","")
        self.password = pwd
        self.student_id = act[1:10]
        self.acedemic_year = admin().get_current_acedemic_year()

    def email_check(self):  #傳送驗證碼(註冊)
        global cnt
        content = MIMEMultipart()  #建立MIMEMultipart物件
        user = self.collection.find_one({"account":self.account})
        if user:
            return ""
        else:
            code=''
            for i in range(6):
                add = random.choice([random.randrange(10)])
                code += str(add)
            content["subject"] = "專題系統帳號註冊驗證碼"  #郵件標題
            content["from"] = "andy625018171@gmail.com"  #寄件者
            content["to"] = self.account #收件者
            content.attach(MIMEText(code)) #郵件內容
            with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
                try:
                    smtp.ehlo()  # 驗證SMTP伺服器
                    smtp.starttls()  # 建立加密傳輸
                    smtp.login("andy625018171@gmail.com", "czmtbmhbecydmmah")  # 登入寄件者gmail
                    smtp.send_message(content)  # 寄送郵件
                    code=hashlib.sha256(code.encode('utf-8')).hexdigest() 
                    verification=verification_code(account=self.account,code=code)
                    verification.create()
                    return True
                except Exception as e:
                    return ""
                    
    def send_email(self): #傳送驗證碼(忘記密碼)
        global cnt
        user = self.collection.find_one({'account':self.account})
        if user == None:
            return ""
        try:
            content = MIMEMultipart() 
            code=''
            for i in range(6):
                add = random.choice([random.randrange(10)])
                code += str(add)
            print(code)
            content["subject"] = "專題系統驗證碼"  #郵件標題
            content["from"] = "andy625018171@gmail.com"  #寄件者
            content["to"] = self.account #收件者
            content.attach(MIMEText(code))
            with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
                try:
                    smtp.ehlo()  # 驗證SMTP伺服器
                    smtp.starttls()  # 建立加密傳輸
                    smtp.login("andy625018171@gmail.com", "czmtbmhbecydmmah")  # 登入寄件者gmail
                    smtp.send_message(content)  # 寄送郵件
                    code=hashlib.sha256(code.encode('utf-8')).hexdigest() 
                    verification=verification_code(account=self.account,code=code)
                    verification.create()                                     
                    return True
                except Exception as e:
                    return ""
        except:
            return ""


    def verification_code_check(self,user_code):
        verification=verification_code(account=self.account)
        code,dead_time = verification.get_code()
        if int(time.time()) <= dead_time:
            if code==user_code:
                verification.delete()
                return True
            else:
                return "false"
        else:
            return ""

    def reset_password(self):  #設定密碼
        try: 
            myquery = { "account": self.account }
            newvalues = { "$set": { "password": self.password} }
            self.collection.update_one(myquery, newvalues)
            return True
        except:
            return ""

    def create_user(self, name, phonenumber, advisor): #user註冊
        user={
            "account":self.account,
            "password":self.password,
            "student_id":self.student_id,
            "type":"student",
            "user_identity":"",
            "group_id":"",
            "name":name,
            "phonenumber":phonenumber,
            "advisor":advisor,
            "acedemic_year":self.acedemic_year,
        }
        self.collection.insert_one(user)
        return True

    def user_pwd_check(self): #確認使用者密碼(用於登入時)
        try:
            user = self.collection.find_one({"account":self.account})
            if user["password"] == self.password:
                return json.loads(json_util.dumps(user))
            else:
                return ""
        except:
            return ""

    def get_user_account(self): #取得user的帳號信息(用於登入時)
        try:
            user = self.collection.find_one({"account":self.account})
            return json.loads(json_util.dumps(user))
        except:
            return ""

    def create_group(self): #創建小組成功後修改user信息
        try:
            myquery = { "account": self.account }
            newvalues = { "$set": { "user_identity":"group_leader", "group_id": self.student_id} }
            self.collection.update_one(myquery, newvalues)
            return True
        except:
            return ""

    def join_group(self, group_id, studentid): #加入小組成功後修改user信息
        try:
            myquery = { "student_id": studentid }
            newvalues = { "$set": { "user_identity":"group_member", "group_id": group_id} }
            self.collection.update_one(myquery, newvalues)
            return True
        except:
            return ""
    
    def get_user(self, group_id):       #小組取得組員信息
        user={
            'leader':"",
            'member_id':[],
            'member':[]
        }
        res = self.collection.find({'group_id':group_id},{'_id':0,'name':1,'user_identity':1,'student_id':1})
        res = json.loads(json_util.dumps(res))
        for user_info in res:
            if user_info['user_identity'] == 'group_leader':
                user['leader']=user_info['name']
            else:
                user['member'].append(user_info['name'])
                user['member_id'].append(user_info['student_id'])
        return user

    def get_user_info(self,student_id):
        user = self.collection.find_one({"student_id":student_id})
        return user

   

class group_class:
    def __init__(self, act="", group_id="", student_id=""):
        self.cluster = MongoClient("mongodb://localhost:27017")
        self.db = self.cluster["user_storage"]
        self.collection = self.db["group"]
        self.account = act
        self.group_id = group_id
        self.student_id = student_id
        self.acedemic_year = admin().get_current_acedemic_year()
        self.student = student_class()

    def create_group(self): #創建小組
        try:
            advisor = self.student.get_user_info(student_id=self.student_id)["advisor"]
            group = {
            "group_id": self.group_id,
            "apply":[],
            "advisor":advisor,
            "leader":self.student_id,
            "member":[],
            "interm_report":{'file_path':''},
            "competition":{'file_path':''},
            "acedemic_year":self.acedemic_year
            }
            self.collection.insert_one(group)
            return True
        except:
            return ""
    
    def find_group(self): #申請加入小組
        try:
            group = self.collection.find_one({"group_id":self.group_id})
            if self.student_id in group["apply"]:
                return ""
            else:
                group["apply"].append(self.student_id)
                res = self.collection.update_one({"group_id":self.group_id},{"$set":group})
                if res:
                    return True
                else:
                    return ""
        except:
            return "null"
    
    def find_apply(self): #取得申請加入學生的資料
        try:
            apply = self.collection.find_one({"group_id":self.group_id})['apply']
            return json.loads(json_util.dumps(apply))
        except:
            return ""

    def ans_apply(self, ans): #管理申請加入組別的信息
        if ans == "accept":
            user_res = self.student.join_group(group_id=self.group_id,studentid=self.student_id)
            group = self.collection.find_one({"group_id":self.group_id})
            group["apply"].remove(self.student_id)
            group["member"].append(self.student_id)
            res = self.collection.update_one({"group_id":self.group_id},{"$set":group})
            if user_res and res:
                return True
        elif ans =="reject":
            group = self.collection.find_one({"group_id":self.group_id})
            group["apply"].remove(self.student_id)
            res = self.collection.update_one({"group_id":self.group_id},{"$set":group})
            return "false"
        else:
            return ""
    
    def upload_file(self,file):  #期中報告上傳
        # try:
            group = self.collection.find_one({"group_id":self.group_id})
            file_path = ""
            if group["interm_report"]["file_path"]=="":
                file_path = f"期中報告/{uuid.uuid4().hex}.pdf"  #uuid64 
            else:
                file_path=group["interm_report"]["file_path"]
            with open(file_path,"wb") as f:
                f.write(file)
            group = self.collection.find_one({"group_id":self.group_id})
            group["interm_report"] = {"file_path":file_path}
            self.collection.update_one({"group_id":self.group_id},{"$set":group})
            return True
        # except:
        #     return ""
    
    def competition_reg(self,file,option1,option2,YT_link):  #專題競賽報名
            group = self.collection.find_one({"group_id":self.group_id})
            file_path = ""
            if group["competition"]["file_path"]=="":
                file_path = f"專題競賽/{uuid.uuid4().hex}.pdf"  #uuid64
            else:
                file_path=group["competition"]["file_path"]
            with open(file_path,"wb") as f:
                f.write(file)
            info = {
                'file_path':file_path,
                'option1':option1,
                'option2':option2,
                'YT_link':YT_link,
                'status':'waiting'
            }
            group["competition"] = info
            print(group)
            self.collection.update_one({"group_id":self.group_id},{"$set":group})
            return True


    def get_competiton_status(self):  #取得報名專題競賽後老師是否同意
        try:
            group = self.collection.find_one({"group_id":self.group_id})
            res=json.loads(json_util.dumps(group))
            if group["competition"]["status"] == "pass":
                return res["competition"]
            elif group["competition"]["status"] == "waiting":
                return res["competition"]
            elif group["competition"]["status"] == "reject":
                return ""
        except:
            return ""
    
    def group_info(self):  #把組員信息打包回傳
        group_member = self.student.get_user(group_id = self.group_id)
        res={
            "group_id":self.group_id,
            "leader":group_member['leader'],
            "member":group_member['member'],
            "member_id":group_member['member_id']
        }
        return res

    def get_file(self,type):
        file_path = ""
        group = self.collection.find_one({"group_id":self.group_id})
        if type == "competition_report":
            file_path = group["competition"]["file_path"]
        elif type == "interm_report":
            file_path = group["interm_report"]["file_path"]
        return file_path

    def cancel_reg(self):
        group = self.collection.find_one({"group_id":self.group_id})
        group["competition"]={
                'file_path':group["competition"]["file_path"],
                'option1':'',
                'option2':'',
                'YT_link':'',
                'status':''
            }
        self.collection.update_one({"group_id":self.group_id},{"$set":group})
        return True


if __name__ == "__main__":
    # admin=group_class(group_id='109360253')
    # ans=admin.get_file(type = "competition_report" )
    # print(ans)
    cluster = MongoClient("mongodb://localhost:27017")
    db = cluster["user_storage"]
    collection = db["user"]
    user = json.loads(json_util.dumps(collection.find_one({"account":'t109360253@ntut.org.tw'})))
    user['check_code']=123456
    user=json.dumps(user)
    collection.update_one({"account":'t109360253@ntut.org.tw'},{'$set':user})
    print(user)