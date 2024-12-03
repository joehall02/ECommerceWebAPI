from flask import request
from marshmallow import ValidationError
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required
from services.payment_service import PaymentService
from decorators import handle_exceptions

# Define the namespace    
payment_ns = Namespace('payment', description='Payment operations')

# Define the models used for api documentation,
# actual validation is done using the schema
payment_model = payment_ns.model('Payment', {
    'stripe_payment_id': fields.String(required=True),
})

# Define the routes
@payment_ns.route('/', methods=['GET', 'POST'])
class PaymentResource(Resource):
    @jwt_required()
    @handle_exceptions
    def get(self): # Get all payment methods for a user        
        payments = PaymentService.get_all_payment_methods()        

        return marshal(payments, payment_model), 200
    
    @jwt_required()
    @handle_exceptions
    def post(self): # Create payment method for a user
        data = request.get_json()
                
        PaymentService.create_payment(data)        
        
        return {'message': 'Payment method created successfully'}, 201
    
@payment_ns.route('/<int:payment_id>', methods=['GET', 'DELETE'])
class PaymentResource(Resource):
    @jwt_required()
    @handle_exceptions
    def get(self, payment_id): # Get a payment method        
        payment = PaymentService.get_payment(payment_id)        

        return marshal(payment, payment_model), 200
    
    @jwt_required()
    @handle_exceptions
    def delete(self, payment_id): # Delete a payment method        
        PaymentService.delete_payment(payment_id)        

        return {'message': 'Payment method deleted successfully'}, 200