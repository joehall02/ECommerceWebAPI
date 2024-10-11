from flask import request
from models import Payment
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity

# Services
class PaymentService:
    @staticmethod
    def create_payment(data):
        user = get_jwt_identity() # Get the user id from the access token

        # Check if the user exists
        if not user:
            raise ValidationError('User not found')

        new_payment = Payment(
            card_number = data['card_number'],
            name_on_card = data['name_on_card'],
            expiry_date = data['expiry_date'],
            security_code = data['security_code'],
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

        return payments
    
    @staticmethod
    def get_payment(payment_id):
        payment = Payment.query.get(payment_id)

        if not payment:
            raise ValidationError('Payment not found')

        return payment

    @staticmethod
    def delete_payment(payment_id):
        payment = Payment.query.get(payment_id)

        if not payment:
            raise ValidationError('Payment not found')

        payment.delete()

        return payment