from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from uuid import uuid4
from lib.clients.dfs import DFS
from os import environ
client = MongoClient(environ.get("ATLAS_URI"))
db = client['tools']

serps = Blueprint('serps', __name__)


@serps.route('/get', methods=['POST'])
def serp():
    body = request.get_json()
    if "keyword" not in body:
        return jsonify({"error": "Manditory field keyword missing"}), 400
    if not isinstance(body["keyword"], str):
        return jsonify({"error": "keyword must be a string"}), 400
    if len(body["keyword"]) == 0:
        return jsonify({"error": "keyword cannot be empty"}), 400
    if "location" not in body:
        return jsonify({"error": "Manditory field location missing"}), 400
    if not isinstance(body["location"], str):
        return jsonify({"error": "location must be a string"}), 400
    if len(body["location"]) == 0:
        return jsonify({"error": "location cannot be empty"}), 400
    if "identifier" not in body:
        return jsonify({"error": "Manditory field identifier missing"}), 400
    if not isinstance(body["identifier"], str):
        return jsonify({"error": "identifier must be a string"}), 400
    if len(body["identifier"]) == 0:
        return jsonify({"error": "identifier cannot be empty"}), 400
    if hasattr(request, 'user'):
        doc = request.doc
        if doc["credits"] < 1:
            return jsonify({"error": "You do not have enough credits"}), 402
    try:
        dfs = DFS()
        serps = dfs.get_serp(body["keyword"], body["location"])
        serps["keyword"] = body["keyword"]
        serps["location"] = body["location"]
        serps[body["identifier"]] = str(uuid4())
        if hasattr(request, 'user'):
            doc["credits"] -= 1
            # Assign uid to serps
            serps["uid"] = request.user["uid"]
        else:
            doc = None
        db.serps.insert_one(serps)
        del serps["_id"]
        del serps["faq"]
        return jsonify({**serps, "doc": doc}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
