from flask import Flask, request, jsonify

from .billing_service import make_payment_no_billing, make_payment_billing
from .database import init_db, db_session
from .models_db import BillingInfoModel
app = Flask(__name__)

@app.route("/billing/health", methods=["GET"])
def health():
    return jsonify({"status": "UP"}), 200

@app.route("/billing/make_payment", methods=["POST"])
def make_payment():
    try:
        data = request.get_json()
        billing_info = {}
        billing_info["credit_card_number"] = data.get("credit_card_number")
        billing_info["expiration_date"] = data.get("expiration_date")
        billing_info["cvv"] = data.get("cvv")
        billing_info["card_holder_name"] = data.get("card_holder_name")
        billing_info["email"] = data.get("email")
        if(not billing_info["credit_card_number"] or
           not billing_info["expiration_date"] or
           not billing_info["cvv"] or
           not billing_info["card_holder_name"]):
            if(make_payment_billing( billing_info["email"])):
                return jsonify({"message": "Payment processed without billing info"}), 200
            else:
                return jsonify({"error": "Payment failed"}), 400
        else:
            if(make_payment_no_billing(billing_info, data.get("save_billing_info", False))):
                return jsonify({"message": "Payment processed with billing info"}), 200
            else:
                return jsonify({"error": "Payment failed"}), 400
    except Exception as e:
        return jsonify({"error": "Error processing payment", "details": str(e)}), 500

@app.route("/billing/cancel_subscription", methods=["POST"])
def cancel_subscription():
    try:
        data = request.get_json()
        email = data.get("email")
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        if make_payment_billing(email):
            return jsonify({"message": "Subscription canceled"}), 200
        else:
            return jsonify({"error": "Error canceling subscription"}), 400
    except Exception as e:
        return jsonify({"error": "Error canceling subscription", "details": str(e)}), 500

def run_app():
    """Entry point for the application script"""
    # Initialize the database before starting the app
    init_db()
    
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    run_app()

