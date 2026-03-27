import asyncio
import sys
import os

# Set up path to import app modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.oauth2 import create_access_token, verify_token, TokenRequest, TokenTypes, TokenData
from app.shared.enums import Role

def main():
    try:
        req = TokenRequest(id="test_user_id", role=Role.USER)
        print("TokenRequest created:", req.model_dump())
        
        token = create_access_token(req)
        print("Created access token:", token)
        
        try:
            expected_token_type = TokenTypes.ACCESS
            credentials_exception = Exception("AuthFailedException")
            decoded_token = verify_token(token, credentials_exception, expected_token_type)
            print("Successfully verified token:", decoded_token)
            
        except Exception as e:
            print("Verification failed with exception:", type(e))
            print("Exception message:", e)
            
            # Let's try manually doing what verify_token does to see the exact Pydantic ValidationError
            import jose.jwt
            from app.core.config import CONFIG
            payload = jose.jwt.decode(token, CONFIG.SECRET_KEY, algorithms=[CONFIG.ALGORITHM])
            print("Raw decoded payload:", payload)
            
            from pydantic import ValidationError
            try:
                # Try to instantiate TokenData
                token_data = TokenData(**payload)
                print("TokenData instantiated directly:", token_data)
            except ValidationError as ve:
                print("Pydantic Validation Error:", ve.errors())
                
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
