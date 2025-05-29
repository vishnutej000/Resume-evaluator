import logging
import json
import os
from datetime import datetime

class ErrorHandler:
    def __init__(self, log_file="logs/errors.log"):
        self.log_file = log_file
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            filename=self.log_file,
            level=logging.ERROR,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def log_error(self, error_type, message, context=None):
        """Log error with context"""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': str(message),
            'context': context
        }
        logging.error(json.dumps(error_data))
    
    def handle_gmail_error(self, error, context):
        """Handle Gmail API errors"""
        self.log_error('gmail_error', error, context)
        return False
    
    def handle_github_error(self, error, context):
        """Handle GitHub API errors"""
        self.log_error('github_error', error, context)
        return None
    
    def handle_parsing_error(self, error, filename):
        """Handle resume parsing errors"""
        self.log_error('parsing_error', error, {'filename': filename})
        return None
    
    def handle_verification_error(self, error, context=None):
        """Handle verification-related errors (skills, LinkedIn, etc.)"""
        self.log_error('verification_error', error, context)
        return None
    
    def handle_linkedin_error(self, error, email):
        """Handle LinkedIn-specific errors"""
        print(f"LinkedIn error for {email}: {error}")