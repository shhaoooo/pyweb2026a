import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

doc = {
  "name": "洪唯皓",
  "mail": "asd0965104898@gmail.com",
  "lab": 579
}

doc_ref = db.collection("靜宜資管").document("Wei-Hao Hong")
doc_ref.set(doc)