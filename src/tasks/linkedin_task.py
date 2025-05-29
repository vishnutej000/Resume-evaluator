from typing import Dict, Any, Optional
from src.utils.error_handler import ErrorHandler

class LinkedInTask:
    def __init__(self, agent, error_handler=None):
        self.agent = agent
        self.error_handler = error_handler

    def execute(self, candidates):
        """Execute LinkedIn enrichment task"""
        enriched_candidates = []
        for candidate in candidates:
            try:
                linkedin_data = self.agent.get_linkedin_profile(candidate['email'])
                if linkedin_data:
                    candidate['linkedin_data'] = linkedin_data
                enriched_candidates.append(candidate)
            except Exception as e:
                self.error_handler.handle_linkedin_error(e, candidate['email'])
                enriched_candidates.append(candidate)
        return enriched_candidates 