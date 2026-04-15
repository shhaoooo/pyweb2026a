import random
from firebase_admin import firestore
from flask import Flask, render_template, request
from datetime import datetime
import os
import json
import firebase_admin
from firebase_admin import credentials
from firestore.read3 import read3_view

# ===== Firebase 初始化（唯一一次）=====
if not firebase_admin._apps:
    if os.path.exists('serviceAccountKey.json'):
        cred = credentials.Certificate('serviceAccountKey.json')
    else:
        firebase_config = os.getenv('FIREBASE_CONFIG')
        cred_dict = json.loads(firebase_config)
        cred = credentials.Certificate(cred_dict)

    firebase_admin.initialize_app(cred)

db = firestore.client()
app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    link = "<h1>歡迎進入洪唯皓的網站首頁</h1>"
    link += "<a href='/mis'>課程</a><hr>"
    link += "<a href='/today'>今天日期</a><hr>"
    link += "<a href='/about'>關於唯皓</a><hr>"
    link += "<a href='/welcome?u=洪唯皓&dep=靜宜資管'>GET傳值</a><hr>"
    link += "<a href='/account'>POST傳值</a><hr>"
    link += "<a href=/math>數學運算</a><hr>" 
    link += "<a href=/cup>擲茭</a><hr>"
    link += "<a href=/read3>教師查詢</a>"
    return link

@app.route("/read3", methods=["GET", "POST"])
def read3():
    teachers = []
    keyword = ""

    if request.method == "POST":
        keyword = request.form.get("keyword", "")

        docs = db.collection("靜宜資管").get()

        for doc in docs:
            data = doc.to_dict()
            name = data.get("name", "")
            lab = data.get("lab", "")

            if keyword in name:
                teachers.append({
                    "name": name,
                    "lab": lab
                })

    return render_template(
        "read3.html",
        teachers=teachers,
        keyword=keyword
    )

@app.route("/mis")
def course():
    return '<h1>資訊管理導論</h1><a href="/">返回首頁</a>'

@app.route("/today")
def today():
    now = datetime.now()
    now_str = f"{now.year}年{now.month}月{now.day}日"
    return render_template("today.html", datetime=now_str)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    x = request.values.get("u")
    y = request.values.get("dep")
    return render_template("welcome.html", name = x, dep = y)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = f"您輸入的帳號是：{user}；密碼為：{pwd}"
        return result
    else:
        return render_template("account.html")

@app.route("/math", methods=["GET", "POST"])
def math():
    if request.method == "POST":
        x = int(request.form["x"])
        opt = request.form["opt"]
        y = int(request.form["y"])      
        result = "您輸入的是：" + str(x) + opt + str(y)
        
        if (opt == "/" and y == 0):
            result += "，除數不能為0"
        else:
            match opt:
                case "+":
                    r = x + y
                case "-":
                    r = x - y
                case "*":
                    r = x * y
                case "/":
                    r = x / y  # 修正：之前誤寫為 x - y
                case _:
                    return "未知運算符號"
            result += "=" + str(r)  + "<br><a href=/>返回首頁</a>"          
        return result
    else:
        return render_template("math.html")

@app.route('/cup', methods=["GET"])
def cup():
    # 檢查網址是否有 ?action=toss
    #action = request.args.get('action')
    action = request.values.get("action")
    result = None
    
    if action == 'toss':
        # 0 代表陽面，1 代表陰面
        x1 = random.randint(0, 1)
        x2 = random.randint(0, 1)
        
        # 判斷結果文字
        if x1 != x2:
            msg = "聖筊：表示神明允許、同意，或行事會順利。"
        elif x1 == 0:
            msg = "笑筊：表示神明一笑、不解，或者考慮中，行事狀況不明。"
        else:
            msg = "陰筊：表示神明否定、憤怒，或者不宜行事。"
            
        result = {
            "cup1": "/static/" + str(x1) + ".jpg",
            "cup2": "/static/" + str(x2) + ".jpg",
            "message": msg
        }
        
    return render_template('cup.html', result=result)

if __name__ == "__main__":
    app.run(debug=True)