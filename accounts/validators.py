import re
from django.core.exceptions import ValidationError

class CustomValidator:
    def validate(self, password, user=None):
        errors = []

        if user:
            cleaned = password.strip().lower()

            if cleaned == user.name.lower():
                errors.append('*Password cannot be the name')
            
            if cleaned == user.username.lower():
                errors.append('*Password cannot be the username')
            
            if cleaned == user.email.lower():
                errors.append('*Password cannot be the email')
        
        if not re.search(r'[A-Za-z]', password):
            errors.append('*Password must contain at least one letter')
        
        if not re.search(r'[0-9]', password):
            errors.append('*Password must contain at least one number')

        if errors:
            raise ValidationError(errors)
