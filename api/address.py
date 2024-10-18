from flask import request
from marshmallow import ValidationError
from flask_restx import Namespace, Resource, fields, marshal
from flask_jwt_extended import jwt_required
from services.address_service import AddressService

# Create a namespace
address_ns = Namespace('address', description='Address related operations')

# Define the models used for api documentation,
# actual validation is done using the schema
address_model = address_ns.model('Address', {
    'address_line_1': fields.String(required=True),
    'address_line_2': fields.String(),
    'city': fields.String(required=True),
    'postcode': fields.String(required=True)
})

# Define the routes
@address_ns.route('/', methods=['POST', 'GET'])
class AddressResource(Resource):
    @jwt_required()
    def get(self): # Get all addresses for a user
        try:
            addresses = AddressService.get_all_addresses()
        except ValidationError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500                
        
        return marshal(addresses, address_model), 200

    @jwt_required()
    def post(self): # Create a new address
        data = request.get_json()
        
        # Create a new address
        try:
            AddressService.create_address(data)
        except ValidationError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500
        
        return {'message': 'Address created successfully'}, 201

@address_ns.route('/<int:address_id>', methods=['GET', 'PUT', 'DELETE'])
class AddressDetailResource(Resource):
    @jwt_required()
    def get(self, address_id): # Get a single address
        try:
            address = AddressService.get_address(address_id)
        except ValidationError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500
        
        return marshal(address, address_model), 200

    @jwt_required()
    def put(self, address_id): # Update a single address
        data = request.get_json()
        
        # Update the address
        try:
            AddressService.update_address(address_id, data)
        except ValidationError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500
        
        return {'message': 'Address updated successfully'}, 200


    @jwt_required() 
    def delete(self, address_id): # Delete a single address
        try:
            AddressService.delete_address(address_id)
        except ValidationError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': str(e)}, 500
        
        return {'message': 'Address deleted successfully'}, 200
