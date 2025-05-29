from typing import Dict, Any, Optional
from src.utils.error_handler import ErrorHandler

class VerifyTask:
    def __init__(self, agent, error_handler=None):
        self.agent = agent
        self.error_handler = error_handler

    def execute(self, candidates):
        """Execute skills verification task"""
        verified_candidates = []
        for candidate in candidates:
            try:
                verified_skills = self.agent.verify_skills(candidate['skills'])
                candidate['verified_skills'] = verified_skills
                verified_candidates.append(candidate)
            except Exception as e:
                self.error_handler.handle_verification_error(e, {'source': 'skills', 'candidate': candidate['email']})
                verified_candidates.append(candidate)
        return verified_candidates 