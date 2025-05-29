from typing import Dict, Any, Optional, List
from src.utils.error_handler import ErrorHandler

class FetchTask:
    def __init__(self, agent, error_handler=None):
        self.agent = agent
        self.error_handler = error_handler

    def execute(self):
        """Execute email fetching task"""
        try:
            return self.agent.fetch_attachments()
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_verification_error(e, {'source': 'email'})
            return []