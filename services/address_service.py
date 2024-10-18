from models import Address
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity
from schemas import AddressSchema

# Define the schema instance
address_schema = AddressSchema()

# Services
class AddressService:
    @staticmethod
    def create_address(data):
        # Check if data is provided
        if not data:
            raise ValidationError('No data provided')

        user = get_jwt_identity()

        # Validate the request data against the address schema
        valid_data = address_schema.load(data)

        # Check if the user exists
        if not user:
            raise ValidationError('User not found')
        
        new_address = Address(
            address_line_1 = valid_data['address_line_1'],
            address_line_2 = valid_data.get('address_line_2', None), # Safely get the address line 2 from the request data or default to None
            city = valid_data['city'],
            postcode = valid_data['postcode'],
            user_id = user
        )

        new_address.save()

        return new_address

    @staticmethod
    def get_all_addresses():
        user = get_jwt_identity() # Get the user id from the access token

        if not user:
            raise ValidationError('User not found')
        
        addresses = Address.query.filter_by(user_id=user).all()

        if not addresses:
            raise ValidationError('Addresses not found')
        
        addresses = address_schema.dump(addresses, many=True)

        
        return addresses

    @staticmethod
    def get_address(address_id):
        # Check if the id is provided
        if not address_id:
            raise ValidationError('No address id provided')

        address = Address.query.get(address_id)

        if not address:
            raise ValidationError('Address not found')
        
        # Serialize the address object to a json object
        address = address_schema.dump(address)
        
        return address

    @staticmethod
    def update_address(address_id, data):
        # Check if the id is provided
        if not address_id:
            raise ValidationError('No address id provided')
        
        # Check if data is provided
        if not data:
            raise ValidationError('No data provided')

        # Validate the request data against the address schema
        valid_data = address_schema.load(data, partial=True) # Allow partial data

        address = Address.query.get(address_id)

        if not address:
            raise ValidationError('Address not found')
        
        if not valid_data:
            raise ValidationError('No data provided')
        
        # Update the address fields
        # Loop through the data and update the address fields
        for key, value in data.items():
            setattr(address, key, value)

        address.save()

        return address

    @staticmethod
    def delete_address(address_id):
        # Check if the id is provided
        if not address_id:
            raise ValidationError('No address id provided')

        address = Address.query.get(address_id)

        if not address:
            raise ValidationError('Address not found')
        
        address.delete()

        return address