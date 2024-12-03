from flask import request
from marshmallow import ValidationError
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required
from services.address_service import AddressService
from decorators import handle_exceptions

# Create a namespace
address_ns = Namespace('address', description='Address related operations')

# Define the models used for api documentation,
# actual validation is done using the schema
address_model = address_ns.model('Address', {
    'full_name': fields.String(required=True),
    'address_line_1': fields.String(required=True),
    'address_line_2': fields.String(),
    'city': fields.String(required=True),
    'postcode': fields.String(required=True),
    'is_default': fields.Boolean(required=True),
})

# Define the routes
@address_ns.route('/', methods=['POST', 'GET'])
class AddressResource(Resource):
    @jwt_required()
    @handle_exceptions
    def get(self): # Get all addresses for a user        
        addresses = AddressService.get_all_addresses()     
        
        return marshal(addresses, address_model), 200

    @jwt_required()
    @handle_exceptions
    def post(self): # Create a new address
        data = request.get_json()

        AddressService.create_address(data)        
        
        return {'message': 'Address created successfully'}, 201

@address_ns.route('/<int:address_id>', methods=['GET', 'PUT', 'DELETE'])
class AddressDetailResource(Resource):
    @jwt_required()
    @handle_exceptions
    def get(self, address_id): # Get a single address        
        address = AddressService.get_address(address_id)        
        
        return marshal(address, address_model), 200

    @jwt_required()
    @handle_exceptions
    def put(self, address_id): # Update a single address
        data = request.get_json()
                
        AddressService.update_address(address_id, data)        
        
        return {'message': 'Address updated successfully'}, 200


    @jwt_required() 
    @handle_exceptions
    def delete(self, address_id): # Delete a single address        
        AddressService.delete_address(address_id)        
        
        return {'message': 'Address deleted successfully'}, 200
