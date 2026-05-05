import random
from bs4 import BeautifulSoup
from firebase_admin import firestore
from flask import Flask, render_template, request
from datetime import datetime
import os
import json
import firebase_admin
from firebase_admin import credentials
import requests
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
    link += "<a href=/read3>教師查詢</a><hr>"
    link += "<a href='/movie'>查詢即將上映電影</a><hr>"
    link += "<a href='/movie2'>爬取電影進資料庫</a><hr>"
    link += "<a href='/movie3'>查詢電影資料庫</a><hr>"
    link += "<a href='/road'>查詢易肇事路口</a><hr>"
    link += "<a href='/weather'>天氣查詢</a><hr>"
    return link

@app.route("/weather", methods=["GET", "POST"])
def weather():
    result = None
    city = ""

    if request.method == "POST":
        city = request.form.get("city", "")
        city = city.replace("台", "臺")

        token = "rdec-key-123-45678-011121314"
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=" + token + "&format=JSON&locationName=" + city

        Data = requests.get(url, verify=False)

        # 👉 防止 API 爆掉
        if Data.status_code == 200:
            try:
                Weather = json.loads(Data.text)["records"]["location"][0]["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
                Rain = json.loads(Data.text)["records"]["location"][0]["weatherElement"][1]["time"][0]["parameter"]["parameterName"]

                result = Weather + "，降雨機率：" + Rain + "%"

            except:
                result = "資料解析失敗"
        else:
            result = "API錯誤：" + str(Data.status_code)

    return render_template("weather.html", result=result, city=city)

@app.route("/road", methods=["GET", "POST"])
def traffic():
    results = []
    keyword = ""

    if request.method == "POST":
        keyword = request.form.get("road", "")

        url = "https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=a1b899c0-511f-4e3d-b22b-814982a97e41"
        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(url, headers=headers, verify=False)

        if response.status_code == 200:
            data = response.json()

            for item in data:
                road = item.get("路口名稱", "")
                
                # 模糊搜尋
                if keyword in road:
                    results.append({
                        "road": road,
                        "count": item.get("總件數", ""),
                        "death": item.get("死亡人數", ""),
                        "injury": item.get("受傷人數", "")
                    })

    return render_template("road.html", results=results, keyword=keyword)

@app.route("/movie3", methods=["GET", "POST"])
def movie3():
    db = firestore.client()
    results = []
    keyword = ""
    
    if request.method == "POST":
        keyword = request.form.get("keyword")
        collection_ref = db.collection("電影")
        docs = collection_ref.get()

        for doc in docs:
            movie = doc.to_dict()
            if keyword in movie["title"]:
                results.append({
                    "title":  movie["title"],
                    "picture": movie["picture"],
                    "hyperlink": movie["hyperlink"],
                    "showDate": movie["showDate"],
                    "showLength": movie["showLength"],
                    "lastUpdate": movie["lastUpdate"]
                })

    return render_template("movie3.html", results=results, keyword=keyword)

@app.route("/movie2")
def movie2():
    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".filmListAllX li")
    lastUpdate = sp.find("div", class_="smaller09").text[5:]

    for item in result:
        picture = item.find("img").get("src").replace(" ", "")
        title = item.find("div", class_="filmtitle").text
        movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")
        show = item.find("div", class_="runtime").text.replace("上映日期：", "")
        show = show.replace("片長：", "")
        show = show.replace("分", "")
        showDate = show[0:10]
        showLength = show[13:]

        doc = {
            "title": title,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": showLength,
            "lastUpdate": lastUpdate
        }

        db = firestore.client()
        doc_ref = db.collection("電影").document(movie_id)
        doc_ref.set(doc)    
    return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate 

@app.route("/movie", methods=["GET", "POST"])
def movie():
    db = firestore.client()

    # :point_right: 第一次進來（GET）→ 自動爬蟲
    if request.method == "GET":
        url = "http://www.atmovies.com.tw/movie/next/"
        Data = requests.get(url)
        Data.encoding = "utf-8"

        sp = BeautifulSoup(Data.text, "html.parser")
        result = sp.select(".filmListAllX li")

        for item in result:
            try:
                picture = item.find("img").get("src").strip()

                # :star: 關鍵修正：補完整網址
                if picture.startswith("/"):
                    picture = "http://www.atmovies.com.tw" + picture

                title = item.find("div", class_="filmtitle").text.strip()

                link = item.find("a").get("href")
                movie_id = link.replace("/", "").replace("movie", "")

                hyperlink = "http://www.atmovies.com.tw" + link

                show = item.find("div", class_="runtime").text
                show = show.replace("上映日期：", "").replace("片長：", "").replace("分", "")

                showDate = show[0:10]
                showLength = show[13:]

                doc = {
                    "title": title,
                    "picture": picture,
                    "hyperlink": hyperlink,
                    "showDate": showDate,
                    "showLength": showLength
                }

                db.collection("電影").document(movie_id).set(doc)

            except Exception as e:
                print("錯誤:", e)

        return render_template("movie.html", movies=None)

    # :point_right: 查詢（POST）
    else:
        keyword = request.form["MovieTitle"]

        docs = db.collection("電影").get()

        movies = []
        for doc in docs:
            data = doc.to_dict()

            if keyword in data.get("title", ""):
                movies.append(data)

        return render_template("movie.html", movies=movies)

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