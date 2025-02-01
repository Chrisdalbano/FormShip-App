import jwt
from datetime import datetime, timedelta
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken
import uuid

def generate_participant_token(participant):
    """Generate JWT token for participant using DRF Simple JWT"""
    token = AccessToken()
    
    # Add required claims
    token['token_type'] = 'access'
    token['participant_id'] = str(participant.id)
    token['email'] = participant.email
    token['type'] = 'participant'
    token['name'] = participant.name
    
    # Convert to string
    token_str = str(token)
    print(f"[Token] Generated token: {token_str[:20]}...")
    print(f"[Token] Token payload: {token.payload}")
    return token_str

def verify_participant_token(token):
    """Verify participant JWT token"""
    try:
        print(f"[Token] Starting verification for token: {token[:20]}...")
        print(f"[Token] Full token being verified: {token}")
        
        # Use DRF Simple JWT settings for verification
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256'],
            options={
                'verify_signature': True,
                'verify_exp': True,
                'verify_iat': True,
            }
        )
        print(f"[Token] Successfully decoded payload: {payload}")
        
        # Verify this is a participant token
        if not payload.get('type') == 'participant':
            print(f"[Token] Invalid token type: {payload.get('type')}")
            raise jwt.InvalidTokenError('Invalid token type')
            
        if not payload.get('participant_id'):
            print("[Token] Missing participant_id in payload")
            raise jwt.InvalidTokenError('Invalid token: missing participant_id')
            
        print(f"[Token] Token verified successfully for participant: {payload.get('participant_id')}")
        return payload
            
    except jwt.ExpiredSignatureError:
        print("[Token] Token has expired")
        raise AuthenticationFailed('Token has expired')
    except jwt.InvalidTokenError as e:
        print(f"[Token] Invalid token error: {str(e)}")
        raise AuthenticationFailed(f'Invalid token: {str(e)}')
    except Exception as e:
        print(f"[Token] Unexpected error during verification: {str(e)}")
        raise AuthenticationFailed(f'Token verification failed: {str(e)}') 