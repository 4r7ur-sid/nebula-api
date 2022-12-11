from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from uuid import uuid4
from lib.clients.dfs import DFS
client = MongoClient('localhost', 27018)
db = client['cadmus']

serps = Blueprint('serps', __name__)


@serps.route('/get', methods=['POST'])
def serp():
    body = request.get_json()
    if "keyword" not in body:
        return jsonify({"error": "Manditory field missing"}), 400
    if not isinstance(body["keyword"], str):
        return jsonify({"error": "keyword must be a string"}), 400
    if len(body["keyword"]) == 0:
        return jsonify({"error": "keyword cannot be empty"}), 400
    if "location" not in body:
        return jsonify({"error": "Manditory field missing"}), 400
    if not isinstance(body["location"], str):
        return jsonify({"error": "location must be a string"}), 400
    if len(body["location"]) == 0:
        return jsonify({"error": "location cannot be empty"}), 400
    dfs = DFS()
    serps = dfs.get_serp(body["keyword"], body["location"])
    serps["keyword"] = body["keyword"]
    serps["location"] = body["location"]
    serps[body["identifier"]] = str(uuid4())
    db.serps.insert_one(serps)
    del serps["_id"]
    del serps["faq"]
    return jsonify(serps), 200
