from typing import Dict, Any, Optional, List
from src.utils.error_handler import ErrorHandler
import requests
import re
import logging
from bs4 import BeautifulSoup

class SkillsVerifier:
    def __init__(self, config: Dict[str, Any], error_handler: Optional[ErrorHandler] = None):
        self.config = config
        self.error_handler = error_handler
        self.logger = logging.getLogger(__name__)
        self.skill_sources = {
            'github': self.verify_github_skills,
            'linkedin': self.verify_linkedin_skills,
            'portfolio': self.verify_portfolio_skills
        }
    
    def verify_skills(self, candidate_data: Dict) -> Dict:
        """Verify skills from multiple sources"""
        try:
            verified_skills = {}
            total_score = 0
            source_count = 0
            
            for source, verify_func in self.skill_sources.items():
                source_skills = verify_func(candidate_data)
                if source_skills:
                    verified_skills[source] = source_skills
                    total_score += source_skills.get('score', 0)
                    source_count += 1
            
            # Calculate average score
            if source_count > 0:
                total_score /= source_count
            
            return {
                'verified_skills': verified_skills,
                'verification_score': round(total_score, 2),
                'confidence_level': self.calculate_confidence(verified_skills)
            }
            
        except Exception as e:
            self.error_handler.handle_verification_error(e, {'candidate': candidate_data.get('email')})
            return {
                'verified_skills': {},
                'verification_score': 0,
                'confidence_level': 'LOW'
            }
            
    def verify_github_skills(self, candidate_data: Dict) -> Dict:
        """Verify skills through GitHub profile"""
        try:
            github_username = candidate_data.get('github_username')
            if not github_username:
                return None
                
            # Get GitHub data
            github_data = self.get_github_data(github_username)
            if not github_data:
                return None
                
            # Extract skills from repositories
            skills = self.extract_github_skills(github_data)
            
            return {
                'skills': skills,
                'score': self.calculate_github_skill_score(skills)
            }
            
        except Exception as e:
            self.error_handler.handle_verification_error(e, {'source': 'github'})
            return None
            
    def verify_linkedin_skills(self, candidate_data: Dict) -> Dict:
        """Verify skills through LinkedIn profile"""
        try:
            linkedin_url = candidate_data.get('linkedin_url')
            if not linkedin_url:
                return None
                
            # Get LinkedIn data
            linkedin_data = self.get_linkedin_data(linkedin_url)
            if not linkedin_data:
                return None
                
            # Extract skills from LinkedIn
            skills = self.extract_linkedin_skills(linkedin_data)
            
            return {
                'skills': skills,
                'score': self.calculate_linkedin_skill_score(skills)
            }
            
        except Exception as e:
            self.error_handler.handle_verification_error(e, {'source': 'linkedin'})
            return None
            
    def verify_portfolio_skills(self, candidate_data: Dict) -> Dict:
        """Verify skills through portfolio website"""
        try:
            portfolio_url = candidate_data.get('portfolio_url')
            if not portfolio_url:
                return None
                
            # Get portfolio data
            portfolio_data = self.get_portfolio_data(portfolio_url)
            if not portfolio_data:
                return None
                
            # Extract skills from portfolio
            skills = self.extract_portfolio_skills(portfolio_data)
            
            return {
                'skills': skills,
                'score': self.calculate_portfolio_skill_score(skills)
            }
            
        except Exception as e:
            self.error_handler.handle_verification_error(e, {'source': 'portfolio'})
            return None
            
    def calculate_confidence(self, verified_skills: Dict) -> str:
        """Calculate confidence level based on verification sources"""
        if not verified_skills:
            return 'LOW'
            
        source_count = len(verified_skills)
        if source_count >= 3:
            return 'HIGH'
        elif source_count >= 2:
            return 'MEDIUM'
        return 'LOW'
        
    def get_github_data(self, username: str) -> Dict:
        """Get GitHub profile data"""
        try:
            api_url = self.config['github']['api_url']
            headers = {
                'Authorization': f"token {self.config.get('github_token', '')}",
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Get user data
            user_url = f"{api_url}/users/{username}"
            user_response = requests.get(user_url, headers=headers)
            if user_response.status_code != 200:
                return None
            user_data = user_response.json()
            
            # Get repositories
            repos_url = f"{api_url}/users/{username}/repos"
            repos_response = requests.get(repos_url, headers=headers)
            repos_data = repos_response.json() if repos_response.status_code == 200 else []
            
            return {
                'user': user_data,
                'repos': repos_data
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching GitHub data for {username}: {str(e)}")
            return None
        
    def get_linkedin_data(self, url: str) -> Dict:
        """Get LinkedIn profile data"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            skills_section = soup.find('section', {'id': 'skills-section'})
            
            if not skills_section:
                return None
                
            return {
                'html': response.text,
                'skills_section': str(skills_section)
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching LinkedIn data for {url}: {str(e)}")
            return None
        
    def get_portfolio_data(self, url: str) -> Dict:
        """Get portfolio website data"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return None
                
            return {
                'html': response.text,
                'url': url
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching portfolio data for {url}: {str(e)}")
            return None
        
    def extract_github_skills(self, github_data: Dict) -> List[str]:
        """Extract skills from GitHub data"""
        skills = set()
        
        # Extract from repository languages
        for repo in github_data.get('repos', []):
            if repo.get('language'):
                skills.add(repo['language'])
                
        # Extract from repository topics
        for repo in github_data.get('repos', []):
            for topic in repo.get('topics', []):
                skills.add(topic)
                
        # Extract from repository descriptions
        for repo in github_data.get('repos', []):
            if repo.get('description'):
                description = repo['description'].lower()
                for skill in self.config['skills']['required'] + self.config['skills']['preferred'] + self.config['skills']['bonus']:
                    if skill.lower() in description:
                        skills.add(skill)
                        
        return list(skills)
        
    def extract_linkedin_skills(self, linkedin_data: Dict) -> List[str]:
        """Extract skills from LinkedIn data"""
        skills = set()
        
        if not linkedin_data or 'skills_section' not in linkedin_data:
            return list(skills)
            
        soup = BeautifulSoup(linkedin_data['skills_section'], 'html.parser')
        skill_elements = soup.find_all('span', {'class': 'mr1 t-bold'})
        
        for element in skill_elements:
            skill = element.text.strip()
            if skill:
                skills.add(skill)
                
        return list(skills)
        
    def extract_portfolio_skills(self, portfolio_data: Dict) -> List[str]:
        """Extract skills from portfolio data"""
        skills = set()
        
        if not portfolio_data or 'html' not in portfolio_data:
            return list(skills)
            
        soup = BeautifulSoup(portfolio_data['html'], 'html.parser')
        text = soup.get_text().lower()
        
        # Look for skills in the text
        for skill in self.config['skills']['required'] + self.config['skills']['preferred'] + self.config['skills']['bonus']:
            if skill.lower() in text:
                skills.add(skill)
                
        return list(skills)
        
    def calculate_github_skill_score(self, skills: List[str]) -> float:
        """Calculate skill verification score from GitHub"""
        if not skills:
            return 0.0
            
        score = 0
        required_skills = self.config['skills']['required']
        preferred_skills = self.config['skills']['preferred']
        bonus_skills = self.config['skills']['bonus']
        
        # Calculate score based on skill categories
        required_count = sum(1 for skill in required_skills if skill in skills)
        preferred_count = sum(1 for skill in preferred_skills if skill in skills)
        bonus_count = sum(1 for skill in bonus_skills if skill in skills)
        
        score = (required_count / len(required_skills)) * 60
        score += (preferred_count / len(preferred_skills)) * 30
        score += min(bonus_count * 5, 10)
        
        return min(score, 100)
        
    def calculate_linkedin_skill_score(self, skills: List[str]) -> float:
        """Calculate skill verification score from LinkedIn"""
        if not skills:
            return 0.0
            
        score = 0
        required_skills = self.config['skills']['required']
        preferred_skills = self.config['skills']['preferred']
        bonus_skills = self.config['skills']['bonus']
        
        # Calculate score based on skill categories
        required_count = sum(1 for skill in required_skills if skill in skills)
        preferred_count = sum(1 for skill in preferred_skills if skill in skills)
        bonus_count = sum(1 for skill in bonus_skills if skill in skills)
        
        score = (required_count / len(required_skills)) * 60
        score += (preferred_count / len(preferred_skills)) * 30
        score += min(bonus_count * 5, 10)
        
        return min(score, 100)
        
    def calculate_portfolio_skill_score(self, skills: List[str]) -> float:
        """Calculate skill verification score from portfolio"""
        if not skills:
            return 0.0
            
        score = 0
        required_skills = self.config['skills']['required']
        preferred_skills = self.config['skills']['preferred']
        bonus_skills = self.config['skills']['bonus']
        
        # Calculate score based on skill categories
        required_count = sum(1 for skill in required_skills if skill in skills)
        preferred_count = sum(1 for skill in preferred_skills if skill in skills)
        bonus_count = sum(1 for skill in bonus_skills if skill in skills)
        
        score = (required_count / len(required_skills)) * 60
        score += (preferred_count / len(preferred_skills)) * 30
        score += min(bonus_count * 5, 10)
        
        return min(score, 100) 