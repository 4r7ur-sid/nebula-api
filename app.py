from outlines import outlines
from locations import locations
from serps import serps
from gptx import gptx
from flask import Flask
from pprint import pprint

from pymongo import MongoClient
client = MongoClient('localhost', 27018)
db = client['cadmus']

#  Importing blueprint modules
app = Flask(__name__)
app.register_blueprint(outlines, url_prefix='/api/v1/outline')
app.register_blueprint(locations, url_prefix='/api/v1/location')
app.register_blueprint(serps, url_prefix='/api/v1/serp')
app.register_blueprint(gptx, url_prefix='/api/v1/gptx')

if __name__ == '__main__':
    app.run(debug=True)
    app.run()
