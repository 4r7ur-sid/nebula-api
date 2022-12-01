from outlines import outlines
from locations import locations
from serps import serps
from gptx import gptx
from flask import Flask, request
from pprint import pprint
from dotenv import load_dotenv

from pymongo import MongoClient
client = MongoClient('localhost', 27018)
db = client['cadmus']
load_dotenv()

#  Importing blueprint modules
app = Flask(__name__)


@app.before_request
def api_auth():
    headers = request.headers
    _path = request.path
    if "x-api-key" in headers:
        api_key = headers["x-api-key"]
        if api_key == "JTBHiSlHXS2Pal7gF4JxZDdVsLfkprXB":
            return
    return "Unauthorized", 401


@app.after_request
def deduct_api_calls(response):
    return response


app.register_blueprint(outlines, url_prefix='/api/v1/outline')
app.register_blueprint(locations, url_prefix='/api/v1/location')
app.register_blueprint(serps, url_prefix='/api/v1/serp')
app.register_blueprint(gptx, url_prefix='/api/v1/gptx')

if __name__ == '__main__':
    app.run(debug=True)
    app.run()
