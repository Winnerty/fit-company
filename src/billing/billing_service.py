from .models_db import BillingInfoModel
from .database import db_session
from .rabbitmq_service import rabbitmq_service


def pay(billing_info):
    if billing_info["credit_card_number"] and billing_info["expiration_date"] and billing_info["cvv"] and billing_info["card_holder_name"]:
        return True
    return False

def make_payment_billing(email):
    try:
        billing_info = {}
        db = db_session()
        billing_info_db = db.query(BillingInfoModel).filter(BillingInfoModel.email == email).first()
        billing_info["credit_card_number"] = billing_info_db.credit_card_number
        billing_info["expiration_date"] = billing_info_db.expiration_date
        billing_info["cvv"] = billing_info_db.cvv
        billing_info["card_holder_name"] = billing_info_db.card_holder_name

        return pay(billing_info)
    except Exception as e:
        return "Error processing payment: " + str(e)
    finally:
        db.close()
        send_users_who_paid(email)

def make_payment_no_billing(billing_info, save_billing_info=False):
    try:
        db = db_session()
        if(save_billing_info):
            billing_info_db = BillingInfoModel(
                credit_card_number=billing_info["credit_card_number"],
                expiration_date=billing_info["expiration_date"],
                cvv=billing_info["cvv"],
                card_holder_name=billing_info["card_holder_name"],
                email=billing_info["email"]
            )
            db.add(billing_info_db)
            db.commit()
            db.refresh(billing_info_db)
        
        return pay(billing_info)
    except Exception as e:
        db.rollback()
        return "Error processing payment: " + str(e)
    finally:
        db.close()
        send_users_who_paid(billing_info["email"])

def send_users_who_paid(email):
    rabbitmq_service.publish_message({"email": email, "message": "User has paid"})

def cancel_subscription(email):
    rabbitmq_service.publish_message_cancel({"id": email, "message": "User has canceled subscription"})