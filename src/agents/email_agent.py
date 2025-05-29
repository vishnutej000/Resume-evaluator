from typing import Dict, Any, Optional, List
from src.utils.error_handler import ErrorHandler
import base64
import io

class EmailAgent:
    def __init__(self, gmail_service: Any, config: Dict[str, Any], error_handler: Optional[ErrorHandler] = None):
        self.gmail_service = gmail_service
        self.config = config
        self.error_handler = error_handler

    def fetch_attachments(self) -> List[Dict]:
        """Fetch resume attachments from received Gmail messages"""
        try:
            # Modify query to only fetch received emails
            base_query = self.config['gmail']['query']
            received_query = f"{base_query} in:inbox -from:me"
            max_results = self.config['gmail']['max_results']
            
            # Search for received emails with attachments
            results = self.gmail_service.users().messages().list(
                userId='me',
                q=received_query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            attachments = []
            
            for message in messages:
                message_attachments = self.process_message(message['id'])
                attachments.extend(message_attachments)
            
            return attachments
            
        except Exception as e:
            self.error_handler.handle_gmail_error(e, {'action': 'fetch_attachments'})
            return []

    def process_message(self, message_id: str) -> List[Dict]:
        """Process individual message for attachments"""
        try:
            message = self.gmail_service.users().messages().get(
                userId='me',
                id=message_id
            ).execute()
            
            # Skip if message is from the user
            headers = message['payload']['headers']
            from_header = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
            if 'me' in from_header.lower():
                return []
            
            attachments = []
            payload = message['payload']
            
            if 'parts' in payload:
                for part in payload['parts']:
                    if part.get('filename') and self.is_resume_file(part['filename']):
                        attachment_data = self.download_attachment(message_id, part)
                        if attachment_data:
                            attachments.append({
                                'filename': part['filename'],
                                'content': attachment_data,
                                'message_id': message_id
                            })
            
            return attachments
            
        except Exception as e:
            self.error_handler.handle_gmail_error(e, {'message_id': message_id})
            return []

    def is_resume_file(self, filename: str) -> bool:
        """Check if file is a resume"""
        valid_extensions = ['.pdf', '.docx']
        return any(filename.lower().endswith(ext) for ext in valid_extensions)

    def download_attachment(self, message_id: str, part: Dict) -> Any:
        """Download attachment content"""
        try:
            attachment_id = part['body']['attachmentId']
            attachment = self.gmail_service.users().messages().attachments().get(
                userId='me',
                messageId=message_id,
                id=attachment_id
            ).execute()
            
            data = attachment['data']
            content = base64.urlsafe_b64decode(data)
            
            # Check file size
            if len(content) > self.config['gmail']['attachment_size_limit']:
                return None
            
            return io.BytesIO(content)
            
        except Exception as e:
            self.error_handler.handle_gmail_error(e, {'attachment_id': attachment_id})
            return None