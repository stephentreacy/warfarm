from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from dotenv import load_dotenv
import warfarm as wf
import os

app = Flask(__name__)
api = Api(app)
load_dotenv()

class ItemPrices(Resource):
    def get(self):
        items = wf.get_item_list(os.getenv('LINK'))
        return {'items': items}

api.add_resource(ItemPrices, '/items')

if __name__ == '__main__':
    app.run(debug=True)
