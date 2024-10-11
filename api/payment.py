from flask import request
from schemas import PaymentSchema
from marshmallow import ValidationError
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required
from services.payment_service import PaymentService

# Define the schema instance
payment_schema = PaymentSchema()

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
            payments = PaymentService.get_all_payment_methods()
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500

        try:
            payments = payment_schema.dump(payments, many=True)
        except ValidationError as e:
            return {'error': str(e)}, 400
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
    def delete(self, payment_id): # Delete a payment method
        try:
            PaymentService.delete_payment(payment_id)
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500

        return {'message': 'Payment method deleted successfully'}, 200