from seo import seo
from locations import locations
from serps import serps
from gptx import gptx
from users import users
from flask import Flask, request
# Import Flask cors
from flask_cors import CORS
from pprint import pprint
from dotenv import load_dotenv
from lib.firebase import Firebase
from firebase_admin import auth, firestore
from pymongo import MongoClient
client = MongoClient('localhost', 27018)
db = client['cadmus']
load_dotenv()

#  Importing blueprint modules
app = Flask(__name__)
# Enable CORS
CORS(app)
app.config["firebase_admin"] = Firebase()


@app.before_request
def api_auth():
    headers = request.headers
    _path = request.path
    if request.method == 'OPTIONS':
        return
    if "x-api-key" in headers:
        api_key = headers["x-api-key"]
        if api_key == "JTBHiSlHXS2Pal7gF4JxZDdVsLfkprXB":
            return
    elif "Authorization" in headers:
        try:
            token = request.headers.get('Authorization')[7:]
            decoded_token = auth.verify_id_token(token)
            request.user = decoded_token["uid"]
            db = firestore.client()
            request.doc = db.collection(
                "tools").document(request.user).get().to_dict()
            if request.doc["credits"] <= 0:
                return jsonify({"error": "No credits left"}), 402
            return
        except Exception as e:
            print(e)
            return "Unauthorized", 401
    return "Unauthorized", 401


@app.after_request
def deduct_api_calls(response):
    if hasattr(response, 'json') and response.json is not None:
        if "error" in response.json:
            return response
        if "doc" in response.json:
            if response.json["doc"] is not None:
                doc = response.json["doc"]
                db = firestore.client()
                db.collection("tools").document(request.user).set(doc)
            del response.json["doc"]
    return response


app.register_blueprint(seo, url_prefix='/api/v1/seo')
app.register_blueprint(locations, url_prefix='/api/v1/location')
app.register_blueprint(serps, url_prefix='/api/v1/serp')
app.register_blueprint(gptx, url_prefix='/api/v1/gptx')
app.register_blueprint(users, url_prefix='/api/v1/users')
if __name__ == '__main__':
    app.run(debug=True)
    app.run()
