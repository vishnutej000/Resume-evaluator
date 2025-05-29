import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class GmailAuth:
    def __init__(self, credentials_path):
        self.credentials_path = credentials_path
        self.token_path = "src/utils/gmail_token.json"
        self.service = None
    
    def authenticate(self):
        """Authenticate with Gmail API using existing token"""
        try:
            # Check if token file exists
            if not os.path.exists(self.token_path):
                print(f"Gmail token file not found at: {self.token_path}")
                return False
            
            # Load existing token
            with open(self.token_path, 'r') as token_file:
                creds_data = json.load(token_file)
            
            if not creds_data.get('token'):
                print("Invalid token data in Gmail token file")
                return False
            
            creds = Credentials.from_authorized_user_info(creds_data)
            
            # Test the credentials by building the service
            self.service = build('gmail', 'v1', credentials=creds)
            
            # Verify service is working with a simple API call
            self.service.users().getProfile(userId='me').execute()
            
            print("✓ Gmail authentication successful")
            return True
            
        except FileNotFoundError:
            print(f"Gmail credentials file not found at: {self.credentials_path}")
            return False
        except json.JSONDecodeError:
            print("Invalid JSON format in Gmail credentials file")
            return False
        except Exception as e:
            print(f"Gmail authentication failed: {e}")
            return False
    
    def get_service(self):
        """Return authenticated Gmail service"""
        return self.service

class GitHubAuth:
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        if not self.token:
            print("⚠️  Warning: GITHUB_TOKEN environment variable not set")
            print("GitHub API functionality will be limited")
        
        self.headers = {
            'Authorization': f'token {self.token}' if self.token else '',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def get_headers(self):
        """Return headers for GitHub API requests"""
        if not self.token:
            print("⚠️  GitHub token not available, API requests will fail")
        return self.headers
    
    def is_authenticated(self):
        """Check if GitHub token is available"""
        return bool(self.token)
