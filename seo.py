from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from lib.tools.outline import GenerateOutline

client = MongoClient('localhost', 27018)
db = client['cadmus']

seo = Blueprint('seo', __name__)


@seo.route('/generate', methods=['POST'])
def outline():
    body = request.get_json()
    if "urls" not in body:
        return jsonify({"error": "Manditory field missing"}), 400
    if not isinstance(body["urls"], list):
        return jsonify({"error": "urls must be a list"}), 400
    if len(body["urls"]) == 0:
        return jsonify({"error": "urls cannot be empty"}), 400
    if len(body["urls"]) > 10:
        return jsonify({"error": "urls cannot be more than 10"}), 400
    if "outline_id" not in body:
        return jsonify({"error": "Manditory field missing"}), 400
    if not isinstance(body["outline_id"], str):
        return jsonify({"error": "outline_id must be a string"}), 400
    if len(body["outline_id"]) == 0:
        return jsonify({"error": "outline_id cannot be empty"}), 400
    if not db.serps.find_one({"outline_id": body["outline_id"]}):
        return jsonify({"error": "outline_id does not exist"}), 400
    if db.outlines.find_one({"outline_id": body["outline_id"]}):
        return jsonify(
            db.outlines.find_one(
                {"outline_id": body["outline_id"]}, {"_id": 0})
        ), 200
    outline = GenerateOutline(body["urls"], body["outline_id"]).generate()
    outline["outline_id"] = body["outline_id"]
    db.outlines.insert_one(outline)
    del outline["_id"]
    return jsonify(outline), 200


@seo.route('/get', methods=['POST'])
def get_outline():
    body = request.get_json()
    if "outline_id" not in body:
        return jsonify({"error": "Manditory field missing"}), 400
    if not isinstance(body["outline_id"], str):
        return jsonify({"error": "outline_id must be a string"}), 400
    if len(body["outline_id"]) == 0:
        return jsonify({"error": "outline_id cannot be empty"}), 400
    outline = db.outlines.find_one({"outline_id": body["outline_id"]})
    if not outline:
        return jsonify({"error": "outline_id does not exist"}), 400
    del outline["_id"]
    return jsonify(outline), 200
