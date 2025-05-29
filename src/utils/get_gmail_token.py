from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import json
import os

def get_gmail_token():
    """Get Gmail OAuth2 token and save it to file"""
    # Define the scopes needed for Gmail API
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    # Paths for credentials and token files
    credentials_path = "src/utils/gmail_credentials.json"
    token_path = "src/utils/gmail_token.json"
    
    try:
        # Check if credentials file exists
        if not os.path.exists(credentials_path):
            print(f"❌ Error: Gmail credentials file not found at {credentials_path}")
            print("Please download your OAuth2 credentials from Google Cloud Console")
            print("and save them as 'src/utils/gmail_credentials.json'")
            return False
        
        # Create flow instance
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path,
            SCOPES
        )
        
        # Run the OAuth2 flow
        print("Starting Gmail authentication...")
        print("A browser window will open. Please login with your Google account")
        print("and grant the requested permissions.")
        creds = flow.run_local_server(port=0)
        
        # Save the credentials
        token_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        }
        
        with open(token_path, 'w') as token_file:
            json.dump(token_data, token_file)
        
        print(f"✓ Gmail token saved successfully to {token_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error during Gmail authentication: {e}")
        return False

if __name__ == "__main__":
    get_gmail_token() 