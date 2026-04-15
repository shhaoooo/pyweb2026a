import firebase_admin
from firebase_admin import credentials, firestore
import os

# ===== Firebase 初始化（安全版：避免重複）=====
if not firebase_admin._apps:
    cred = credentials.Certificate(
        os.path.join(os.path.dirname(__file__), "../serviceAccountKey.json")
    )
    firebase_admin.initialize_app(cred)

db = firestore.client()


# ===== 查詢核心邏輯（給 Web + CLI 共用）=====
def search_teachers(keyword):
    results = []

    docs = db.collection("靜宜資管").stream()

    for doc in docs:
        data = doc.to_dict()

        name = data.get("name", "")
        lab = data.get("lab", "")

        if keyword.lower() in name.lower():
            results.append({
                "name": name,
                "lab": lab
            })

    return results


# ===== Flask 用（web.py 會呼叫）=====
def read3_view(request):
    from flask import render_template

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


# ===== CLI 用（直接終端機執行）=====
if __name__ == "__main__":
    keyword = input("請輸入老師名字關鍵字：")

    teachers = search_teachers(keyword)

    print("\n查詢結果：")

    if teachers:
        for t in teachers:
            print(f"老師：{t['name']}，研究室：{t['lab']}")
    else:
        print("查無資料")