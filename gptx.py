from flask import Blueprint, jsonify, request
from pymongo import MongoClient

from lib.tools.status_generator import StatusGenerator
gptx = Blueprint('gptx', __name__)


@gptx.route('/status-generator', methods=['POST'])
def status_generator():
    body = request.get_json()
    if "url" not in body:
        return jsonify({"error": "Manditory field missing"}), 400
    if not isinstance(body["url"], str):
        return jsonify({"error": "url must be a string"}), 400
    if len(body["url"]) == 0:
        return jsonify({"error": "url cannot be empty"}), 400
    if "social_media" not in body:
        return jsonify({"error": "Manditory field missing"}), 400
    if not isinstance(body["social_media"], str):
        return jsonify({"error": "social_media must be a string"}), 400
    if body["social_media"] not in ["linkedin", "twitter"]:
        return jsonify({"error": "social_media must be linkedin or twitter"}), 400
    if "variations" not in body:
        return jsonify({"error": "Manditory field missing"}), 400
    # StatusGenerator
    try:
        status_generator = StatusGenerator(
            body["url"], body["social_media"], body["variations"])
        return jsonify(status_generator.generate()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
