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
        
        addresses = Address.query.filter_by(user_id=user).all()

        # If the user already has 5 addresses, raise an error
        if len(addresses) >= 5:
            raise ValidationError('You have reached the maximum number of addresses')

        # If is_default is True, set all other addresses to False
        if valid_data['is_default'] == True:
            for address in addresses:
                address.is_default = False
                address.save()

        # If this is the first address, set it as default
        if not Address.query.filter_by(user_id=user).first():
            valid_data['is_default'] = True

        new_address = Address(
            full_name = valid_data['full_name'],
            address_line_1 = valid_data['address_line_1'],
            address_line_2 = valid_data.get('address_line_2', None), # Safely get the address line 2 from the request data or default to None
            city = valid_data['city'],
            postcode = valid_data['postcode'],
            is_default = valid_data['is_default'],
            user_id = user
        )

        new_address.save()

        return new_address

    @staticmethod
    def get_all_addresses():
        user = get_jwt_identity() # Get the user id from the access token

        if not user:
            raise ValidationError('User not found')
        
        # Get all addresses for the user, order by is_default in descending order
        addresses = Address.query.filter_by(user_id=user).order_by(Address.is_default.desc()).all()

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
    def get_default_address():
        user = get_jwt_identity()

        if not user:
            raise ValidationError('User not found')
        
        address = Address.query.filter_by(user_id=user, is_default=True).first()

        if not address:
            raise ValidationError('Default address not found')
        
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
        
        user = get_jwt_identity()

        if not user:
            raise ValidationError('User not found')
        
        # if is_default is True, set all addresses except the current one to False
        if valid_data['is_default'] == True:
            addresses = Address.query.filter_by(user_id=user).all()
            for addr in addresses:
                if addr.id != address_id:    
                    addr.is_default = False
                    addr.save()
        
        # Update the address fields
        # Loop through the data and update the address fields
        for key, value in valid_data.items():            
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

        # Set the next address as default if it exists
        user = get_jwt_identity()

        if not user:
            raise ValidationError('User not found')
        
        addresses = Address.query.filter_by(user_id=user).all()

        if addresses:
            addresses[0].is_default = True
            addresses[0].save()

        return address