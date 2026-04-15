import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# ===== Firebase 初始化（本地 + Vercel 都可）=====
def init_firebase():
    if not firebase_admin._apps:
        if os.path.exists("serviceAccountKey.json"):
            # 本地
            cred = credentials.Certificate("serviceAccountKey.json")
        else:
            # 雲端（Vercel）
            firebase_config = os.getenv("FIREBASE_CONFIG")
            if not firebase_config:
                raise ValueError("Firebase 環境變數未設定")

            cred_dict = json.loads(firebase_config)
            cred = credentials.Certificate(cred_dict)

        firebase_admin.initialize_app(cred)


# ===== 初始化 DB =====
init_firebase()
db = firestore.client()


# ===== 查詢功能 =====
def search_teachers(keyword):
    results = []

    docs = db.collection("靜宜資管").get()

    for doc in docs:
        data = doc.to_dict()

        name = data.get("name", "")
        lab = data.get("lab", "")

        if keyword and keyword in name:
            results.append({
                "name": name,
                "lab": lab
            })

    return results


# ===== Web 用（Flask）=====
def read3_view():
    from flask import request, render_template

    teachers = []
    keyword = ""

    if request.method == "POST":
        keyword = request.form.get("keyword", "")
        teachers = search_teachers(keyword)

    return render_template(
        "read3.html",
        teachers=teachers,
        keyword=keyword
    )


# ===== CLI 模式（終端機可用）=====
if __name__ == "__main__":
    keyword = input("請輸入老師名字關鍵字：")

    result = search_teachers(keyword)

    print("\n查詢結果：")

    if result:
        for t in result:
            print(f"老師：{t['name']}，研究室：{t['lab']}")
    else:
        print("查無資料")