from flask import request
from models import Payment
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity
from schemas import PaymentSchema

# Define the schema instance
payment_schema = PaymentSchema()

# Services
class PaymentService:
    @staticmethod
    def create_payment(data):
        # Check if data is provided
        if not data:
            raise ValidationError('No data provided')
        
        # Validate the request data using the schema
        valid_data = payment_schema.load(data)
        
        user = get_jwt_identity() # Get the user id from the access token

        # Check if the user exists
        if not user:
            raise ValidationError('User not found')

        new_payment = Payment(
            card_number = valid_data['card_number'],
            name_on_card = valid_data['name_on_card'],
            expiry_date = valid_data['expiry_date'],
            security_code = valid_data['security_code'],
            user_id = user
        )
        new_payment.save()

        return new_payment

    @staticmethod
    def get_all_payment_methods():
        user = get_jwt_identity() # Get the user id from the access token

        # Check if the user exists
        if not user:
            raise ValidationError('User not found')

        payments = Payment.query.filter_by(user_id=user).all()

        if not payments:
            raise ValidationError('Payments not found')

        # Serialize the data
        payments = payment_schema.dump(payments, many=True)

        return payments
    
    @staticmethod
    def get_payment(payment_id):
        # Check if the payment id is provided
        if not payment_id:
            raise ValidationError('No payment id provided')

        payment = Payment.query.get(payment_id)

        if not payment:
            raise ValidationError('Payment not found')

        # Serialize the data
        payment = payment_schema.dump(payment)

        return payment

    @staticmethod
    def delete_payment(payment_id):
        # Check if the payment id is provided
        if not payment_id:
            raise ValidationError('No payment id provided')

        payment = Payment.query.get(payment_id)

        if not payment:
            raise ValidationError('Payment not found')

        payment.delete()

        return payment