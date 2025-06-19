from sqlalchemy import Column, String, Integer
from .database import Base

class BillingInfoModel(Base):
    __tablename__ = "billing_info"

    id = Column(Integer, primary_key=True, index=True)
    #user_id = Column(Integer, nullable=False)
    credit_card_number = Column(String(16), nullable=False)
    expiration_date = Column(String(5), nullable=False)
    cvv = Column(String(3), nullable=False)
    card_holder_name = Column(String(100), nullable=False)
    email = Column(String, nullable=False)

    def __repr__(self):
        return f"<BillingInfo(id={self.id}, card_holder_name='{self.card_holder_name}')>"