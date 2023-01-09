from pprint import pprint
from flask import Blueprint, jsonify, request, current_app
from firebase_admin import  firestore
import requests
users = Blueprint('users', __name__)
# U9L4
@users.route('/plan/activate', methods=['POST'])
def activate_plan():
    # Get Access Token
    try:
        # Sandbox
        # url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
        # Live
        url = "https://api-m.paypal.com/v1/oauth2/token"
        headers = {
            "Accept" : "application/json",
            "Accept-Language" : "en_US",
        }
        payload = {
            "grant_type": "client_credentials"
        }

        response = requests.post(url, headers=headers, data=payload, 
            # Sandbox
            # auth=('AaF9TPfc06U-zKfM7Aw-m4cuBPelBCdEAS5l17vBc2ecUtO2ceA2vNV20yhaz16iegVqLXEXU-WQGpA2', 'EO3aAisrhXFusHtHeWHuHTXc8obsuSJn1yFOKPejcJasud4qdU5JoifOCOajUNZZlUlGMIGMmXIVFjoV'),
            # Live
            auth = ('AcBRMh8Sld5_EZwHykKvUVANAx8YCnC9JYJ0h4KbCJjLTo5w8u4gdK6c-UQ0mQSdqyjyCP5N4D0dL-R0','EIWyzn54Mfmgi8YIVhXydNC0S8Dx5sheQf-v0DXHWz9eBfk-ROmlrwjaRkOm0k43XCDCjd5EbVR1y1wg')
        )
        access_token = ""
        if response.status_code == 200:
            resp = response.json()
            access_token = resp["access_token"]

        else:
            return jsonify({"success": False}), 200

        headers = {
            "Content-Type": "application/json",
            "Authorization" : "Bearer "+access_token
        }
        data = request.get_json()
        # Sandbox
        # url = "https://api-m.sandbox.paypal.com/v2/checkout/orders/" + data["orderId"]
        # Live
        url = "https://api-m.paypal.com/v2/checkout/orders/" + data["orderId"]
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            resp = response.json()
            if resp["status"] == "COMPLETED":
                # Get order value
                order_value = resp["purchase_units"][0]["amount"]["value"]
                credit = 0
                if order_value == "14.99":
                    credit = 100
                elif order_value == "29.99":
                    credit = 250
                elif order_value == "49.99":
                    credit = 500
                db = firestore.client()
                request.doc["credits"] += credit
                db.collection("tools").document(request.user).set(request.doc)
                return jsonify({"success": True}), 200
        return jsonify({"success": False}), 200
    except Exception as e:
        print(e)
        return jsonify({"success": False}), 200