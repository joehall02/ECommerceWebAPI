from flask import request
from models import Payment, User
from schemas import PaymentSchema
from marshmallow import ValidationError
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import get_jwt_identity, jwt_required

# Define the schema instance
payment_schema = PaymentSchema()

# Services
class PaymentService:
    @staticmethod
    def create_payment(data):
        user = get_jwt_identity()

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
    def get_all_payment_methods(user_id):
        payments = Payment.query.filter_by(user_id=user_id).all()

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

# Define the namespace    
payment_ns = Namespace('payment', description='Payment operations')

# Define the models used for api documentation,
# actual validation is done using the schema
payment_model = payment_ns.model('Payment', {
    'card_number': fields.Integer(required=True),
    'name_on_card': fields.String(required=True),
    'expiry_date': fields.Date(required=True),
    'security_code': fields.String(required=True),
})

# Define the routes
@payment_ns.route('/', methods=['GET', 'POST'])
class PaymentResource(Resource):
    @jwt_required()
    def get(self): # Get all payment methods for a user
        # Get all payment methods for a user
        try:
            user_id = get_jwt_identity() # Get the user ID from the access token
            payments = PaymentService.get_all_payment_methods(user_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500

        try:
            payments = payment_schema.dump(payments, many=True)
        except ValidationError as e:
            return {'error': str(e)}, 500
        except Exception as e:
            return {'error': str(e)}, 500

        return marshal(payments, payment_model), 200
    
    @jwt_required()
    def post(self): # Create payment method for a user
        data = request.get_json()

        # Validate the request data using the schema
        try:
            valid_data = payment_schema.load(data)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        
        # Create a new payment method
        try:
            PaymentService.create_payment(valid_data)
        except ValidationError as e:
            return {'error': str(e)}, 400  
        except Exception as e:
            return {'error': str(e)}, 500
        
        return {'message': 'Payment method created successfully'}, 201
    
@payment_ns.route('/<int:payment_id>', methods=['GET', 'DELETE'])
class PaymentResource(Resource):
    @jwt_required()
    def get(self, payment_id): # Get a payment method
        try:
            payment = PaymentService.get_payment(payment_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500

        try:
            payment = payment_schema.dump(payment)
        except ValidationError as e:
            return {'error': str(e)}, 500
        except Exception as e:
            return {'error': str(e)}, 500

        return marshal(payment, payment_model), 200
    
    @jwt_required()
    def delete(self, payment_id):
        try:
            PaymentService.delete_payment(payment_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500

        return {'message': 'Payment method deleted successfully'}, 200