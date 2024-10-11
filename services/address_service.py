from models import Address
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity

# Services
class AddressService:
    @staticmethod
    def create_address(data):
        user = get_jwt_identity()

        # Check if the user exists
        if not user:
            raise ValidationError('User not found')
        
        new_address = Address(
            address_line_1 = data['address_line_1'],
            address_line_2 = data.get('address_line_2', None), # Safely get the address line 2 from the request data or default to None
            city = data['city'],
            postcode = data['postcode'],
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
        
        return addresses

    @staticmethod
    def get_address(address_id):
        address = Address.query.get(address_id)

        if not address:
            raise ValidationError('Address not found')
        
        return address

    @staticmethod
    def update_address(address_id, data):
        address = Address.query.get(address_id)

        if not address:
            raise ValidationError('Address not found')
        
        if not data:
            raise ValidationError('No data provided')
        
        # Update the address fields
        # Loop through the data and update the address fields
        for key, value in data.items():
            setattr(address, key, value)

        address.save()

        return address

    @staticmethod
    def delete_address(address_id):
        address = Address.query.get(address_id)

        if not address:
            raise ValidationError('Address not found')
        
        address.delete()

        return address