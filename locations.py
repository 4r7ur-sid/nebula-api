from flask import Blueprint, jsonify, request
from pymongo import MongoClient
client = MongoClient('localhost', 27018)
db = client['cadmus']

locations = Blueprint('locations', __name__)


@locations.route('/get', methods=['POST'])
def get_locations():
    body = request.get_json()
    if "query" not in body:
        return jsonify({"error": "Manditory field missing"}), 400
    if not isinstance(body["query"], str):
        return jsonify({"error": "query must be a string"}), 400
    if len(body["query"]) == 0:
        return jsonify({"error": "query cannot be empty"}), 400
    # Regex for typeahead search
    query = {
        "location_name": {
            "$regex": body["query"],
            "$options": "i"
        }
    }
    if "parent_id" not in body:
        query["location_type"] = "Country"
    else:
        query["location_code_parent"] = body["parent_id"]

    locations = db.locations.find(query, {"_id": 0}).limit(10)
    return jsonify(list(locations)), 200


@locations.route('/check-children', methods=['POST'])
def check_location_children():
    body = request.get_json()
    if "parent_id" not in body:
        return jsonify({"error": "Manditory field missing"}), 400
    if not isinstance(body["parent_id"], str):
        return jsonify({"error": "parent_id must be a string"}), 400
    if len(body["parent_id"]) == 0:
        return jsonify({"error": "parent_id cannot be empty"}), 400
    query = {
        "location_code_parent": body["parent_id"],
        "location_type": {"$in": ["State", "Union Territory"]}
    }
    # Check how many type of location_type are there with their count
    locations = db.locations.aggregate([
        {"$match": query},
        {"$group": {"_id": "$location_type", "count": {"$sum": 1}}}
    ])
    return jsonify({
        "children": list(locations)
    }), 200
