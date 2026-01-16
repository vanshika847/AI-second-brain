"""
Firebase Authentication for AI Second Brain
Handles user sign-in with Google accounts
"""

import firebase_admin
from firebase_admin import credentials, auth
import json

class FirebaseAuth:
    def __init__(self, credentials_path='firebase-credentials.json'):
        """
        Initialize Firebase Admin SDK
        
        Args:
            credentials_path: Path to Firebase service account JSON file
        """
        try:
            # Initialize Firebase
            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized successfully!")
        except Exception as e:
            print(f"❌ Error initializing Firebase: {str(e)}")
    
    def verify_token(self, id_token):
        """
        Verify a Firebase ID token
        
        Args:
            id_token: Firebase ID token from client
            
        Returns:
            User information if valid, None otherwise
        """
        try:
            # Verify the token
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            email = decoded_token.get('email', 'No email')
            
            print(f"✅ User authenticated: {email}")
            return {
                'uid': uid,
                'email': email,
                'name': decoded_token.get('name', 'Unknown')
            }
        except Exception as e:
            print(f"❌ Token verification failed: {str(e)}")
            return None
    
    def create_custom_token(self, uid):
        """
        Create a custom token for a user
        
        Args:
            uid: User ID
            
        Returns:
            Custom token string
        """
        try:
            custom_token = auth.create_custom_token(uid)
            return custom_token.decode('utf-8')
        except Exception as e:
            print(f"❌ Error creating custom token: {str(e)}")
            return None
    
    def get_user(self, uid):
        """
        Get user information by UID
        
        Args:
            uid: User ID
            
        Returns:
            User record
        """
        try:
            user = auth.get_user(uid)
            return {
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name,
                'photo_url': user.photo_url
            }
        except Exception as e:
            print(f"❌ Error getting user: {str(e)}")
            return None


# Example usage
if __name__ == "__main__":
    print("🔐 Testing Firebase Authentication...\n")
    
    # Initialize Firebase
    fb_auth = FirebaseAuth()
    
    print("\n✅ Firebase is ready to authenticate users!")
    print("Note: Token verification requires a client app to generate tokens.")