from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    link = "<h1>歡迎進入洪唯皓的網站首頁</h1>"
    link += "<a href='/mis'>課程</a><hr>"
    link += "<a href='/today'>今天日期</a><hr>"
    link += "<a href='/about'>關於唯皓</a><hr>"
    link += "<a href='/welcome?u=洪唯皓&dep=靜宜資管'>GET傳值</a><hr>"
    link += "<a href='/account'>POST傳值</a><hr>"
    return link

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

if __name__ == "__main__":
    app.run(debug=True)