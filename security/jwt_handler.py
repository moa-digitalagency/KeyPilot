import jwt
import datetime
from datetime import timedelta, timezone

def generate_token(payload, secret, algorithm='HS256', expiration_minutes=60):
    """
    Generates a JWT token signed with the provided secret.

    Args:
        payload (dict): The data to include in the token payload.
        secret (str): The secret key to sign the token.
        algorithm (str, optional): The algorithm to use for signing. Defaults to 'HS256'.
        expiration_minutes (int, optional): The number of minutes until the token expires. Defaults to 60.

    Returns:
        str: The generated JWT token.
    """
    try:
        # Create a copy of the payload to avoid modifying the original
        token_payload = payload.copy()

        # Add expiration time
        token_payload['exp'] = datetime.datetime.now(timezone.utc) + timedelta(minutes=expiration_minutes)

        # Add issued at time
        token_payload['iat'] = datetime.datetime.now(timezone.utc)

        encoded_token = jwt.encode(token_payload, secret, algorithm=algorithm)
        return encoded_token
    except Exception as e:
        print(f"Error generating token: {e}")
        return None

def validate_token(token, secret, algorithms=['HS256']):
    """
    Validates a JWT token.

    Args:
        token (str): The JWT token to validate.
        secret (str): The secret key to verify the token signature.
        algorithms (list, optional): A list of allowed algorithms. Defaults to ['HS256'].

    Returns:
        dict: The decoded payload if the token is valid.
        None: If the token is invalid or expired.
    """
    try:
        decoded_payload = jwt.decode(token, secret, algorithms=algorithms)
        return decoded_payload
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token.")
        return None
    except Exception as e:
        print(f"Error validating token: {e}")
        return None
