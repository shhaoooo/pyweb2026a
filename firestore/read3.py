import firebase_admin
from firebase_admin import credentials, firestore
import os

# ===== Firebase 初始化（一定要有）=====
if not firebase_admin._apps:
    cred = credentials.Certificate(
        os.path.join(os.path.dirname(__file__), "..", "serviceAccountKey.json")
    )
    firebase_admin.initialize_app(cred)

db = firestore.client()


# ===== 查詢 =====
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


# ===== Web 用 =====
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