from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
from student import *
import hashlib
from flask_socketio import SocketIO,emit
import time
import threading
from admin import *


app =Flask(__name__,template_folder='frontend')
cors = CORS(app,resources={r"/api/*":{"origins":'*'}})
socketio = SocketIO()
socketio.init_app(app, cors_allowed_origins='*',async_mode='threading')

# @socketio.on('get_server_time', namespace='/api')
# def get_server_time():
#     localtime = time.time()*1000
#     print(localtime)
#     socketio.emit('time_recive',localtime,namespace='/api')

@app.route('/api/get_server_time',methods=['GET'])
def get_server_time():
    localtime = time.time()*1000
    return jsonify({'res':localtime})

@app.route('/api/login', methods = ['POST'])
def login():
    act = request.get_json()["act"]    #若是要獲取post請求:request.get_json()['name'],GET請求用request.args.get('name')
    type = request.get_json()["type"]
    if type == "account":
        user = student_class(act)
        user = user.get_user_account()
        if user != "":
            response = {
                    'user': user
                }
            return jsonify(response)
        else:
            response = {
                    'user': ''
                }
            return jsonify(response)
    elif type == "password":
        pwd = hashlib.sha256(request.get_json()["pwd"].encode('utf-8')).hexdigest() 
        user = student_class(act,pwd)
        user = user.user_pwd_check()
        if user != "":
            response = {
                    'user': user
                }
            return jsonify(response)
        else:
            response = {
                    'user': ''
                }
            return jsonify(response)

@app.route('/api/register', methods = ['POST'])
def register():
    act = request.get_json()["act"]
    pwd = hashlib.sha256(request.get_json()["pwd"].encode('utf-8')).hexdigest() 
    user = student_class(act,pwd)
    code = user.email_check()
    if code:
        response = {
            'code': code
        }
        return jsonify(response)
    else:
        response = {
            'code': ""
        }
        return jsonify(response)

@app.route('/api/verify', methods = ['POST'])
def verify():
    act = request.get_json()["act"]
    user = student_class(act)
    status = user.verification_code_check(user_code=hashlib.sha256(request.get_json()['user_code'].encode('utf-8')).hexdigest())
    response = {
        'res': status
    }
    return jsonify(response)

@app.route('/api/forgetpd_verify', methods = ['POST'])
def forget():
    act = request.get_json()["act"]
    user = student_class(act)
    code = user.send_email()
    response = {
            'code': code
    }
    return jsonify(response)


@app.route('/api/reset_password', methods = ['POST'])
def reset_pd():
    act = request.get_json()["act"]
    pwd = hashlib.sha256(request.get_json()["pwd"].encode('utf-8')).hexdigest() 
    user = student_class(act,pwd)
    res = user.reset_password()
    if res:
        response = {
            "reset":res
        }
        return jsonify(response)
    else:
        response = {
            "reset": ""
        }
        return jsonify(response)

@app.route('/api/create_account', methods = ['POST'])
def create():
    act = request.get_json()["act"] 
    pwd = hashlib.sha256(request.get_json()["pwd"].encode('utf-8')).hexdigest() 
    name = request.get_json()["name"]
    phonenumber = request.get_json()["phonenumber"]
    advisor = request.get_json()["advisor"]
    user = student_class(act,pwd)
    create=user.create_user(name,phonenumber,advisor)
    response = {
        'status': create
    }
    return jsonify(response)

@app.route('/api/create_group', methods = ['POST'])
def creategroup():
    act = request.get_json()["act"]
    user = student_class(act)
    user.create_group()
    group = group_class(act=act,group_id=act[1:10],student_id=act[1:10])
    ans = group.create_group()
    if ans:
        response = {
            'res': ans
        }
        return jsonify(response)
    else:
        response = {
            'res': ""
        }
        return jsonify(response)

@app.route('/api/find_group', methods = ['POST']) #申請加入小組
def findgroup():
    student_id = request.get_json()["student_id"]
    group_id = request.get_json()["group_id"]
    group = group_class(student_id=student_id, group_id = group_id)
    ans = group.find_group()
    if ans:
        response = {
            'res': ans
        }
        return jsonify(response)
    else:
        response = {
            'res': ""
        }
        return jsonify(response)

@app.route('/api/find_apply', methods = ['POST']) #找小組申請加入名單
def findapply():
    group_id = request.get_json()["group_id"]
    type = request.get_json()["type"]
    if type == "get_apply":
        group = group_class(group_id=group_id)
        ans = group.find_apply()
        if ans:
            response = {
                'res': ans
            }
            return jsonify(response)
        else:
            response = {
                'res': ""
            }
            return jsonify(response)
    elif type == "accept" or type == "reject":
        student_id = request.get_json()["student_id"]
        group = group_class(group_id=group_id, student_id=student_id)
        res = group.ans_apply(ans = type)
        if res:
            response = {
                'res': res
            }
            return jsonify(response)
        else:
            response = {
                'res': ""
            }
            return jsonify(response)

@app.route('/api/upload_file', methods = ['POST'])
def upload_file():
    file = request.files['file']  #抓到前端post過來的檔案  教學:https://blog.csdn.net/xin_yun_Jian/article/details/103620476
    file_data = file.stream.read() #讀成二進制
    group_id = request.form["group_id"]
    group = group_class(group_id = group_id)
    ans = group.upload_file(file=file_data)
    if ans:
        response = {
            'res':True
        }
        return jsonify(response)
    else:
        response = {
            'res': ""
        }
        return jsonify(response)

@app.route('/api/competition_reg', methods = ['POST'])
def competition_reg():
    file = request.files['file']  #抓到前端post過來的檔案  教學:https://blog.csdn.net/xin_yun_Jian/article/details/103620476
    file_data = file.stream.read() #讀成二進制
    group_id = request.form["group_id"]
    option1 = request.form["option1"]
    option2 = request.form["option2"]
    YT_link = request.form["YT_link"]
    group = group_class(group_id = group_id)
    ans = group.competition_reg(file=file_data,option1=option1,option2=option2,YT_link=YT_link)
    if ans:
        response = {
            'res':True
        }
        return jsonify(response)
    else:
        response = {
            'res': ""
        }
        return jsonify(response)

@app.route('/api/get_competition_status', methods = ['GET'])
def get_competiton_status():
    group_id = request.args.get('group_id')
    group = group_class(group_id = group_id)
    ans = group.get_competiton_status()
    response = {
        'res': ans
    }
    return jsonify(response)

@app.route('/api/group_info', methods = ['GET'])
def get_group_info():
    group_id = request.args.get('group_id')
    group = group_class(group_id = group_id)
    group_info = group.group_info()
    response = {
        'group_info':group_info,
    }
    return jsonify(response)

@app.route('/api/get_file', methods = ['POST'])  #https://blog.csdn.net/zhaojikun521521/article/details/110436871
def get_file():
    try:
        group_id = request.get_json()["group_id"]
        type= request.get_json()["type"]
        group = group_class(group_id = group_id)
        res = group.get_file(type=type)
        return send_file(str(res))
    except:
        return ""

@app.route('/api/cancel_reg', methods = ['POST']) 
def cancel_reg():
    group_id = request.get_json()["group_id"]
    group = group_class(group_id = group_id)
    res = group.cancel_reg()
    response = {
        'res':res,
    }
    return jsonify(response)

@app.route('/', defaults={'path': 'index.html'}) #路徑自動導到index.html中,接下來由vue-router接手
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")


if __name__ == "__main__":
    verification = verification_code()
    t1 = threading.Thread(target=verification.delete_code_everyday)
    t1.daemon=True
    t1.start()
    socketio.run(app,host='172.104.101.224',port=8000,debug = True)



# def server_time():
#     while True:
#         localtime = time.localtime()
#         result = time.strftime("%Y-%m-%d %I:%M:%S %p", localtime)
#         socketio.emit('time_recive',result,namespace='/api')
#         print(result)
#         time.sleep(1)
