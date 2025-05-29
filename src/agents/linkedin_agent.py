from typing import Dict, Any, Optional
from src.utils.error_handler import ErrorHandler
import requests
from bs4 import BeautifulSoup
import re
import time
import logging

class LinkedInAgent:
    def __init__(self, config: Dict[str, Any], error_handler: Optional[ErrorHandler] = None):
        self.config = config
        self.error_handler = error_handler
        self.logger = logging.getLogger(__name__)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

    def analyze_profiles(self, candidate_data: Dict) -> Dict:
        """Analyze LinkedIn profiles"""
        try:
            linkedin_url = candidate_data.get('linkedin_url')
            if not linkedin_url:
                self.logger.warning(f"No LinkedIn URL found for candidate: {candidate_data.get('email')}")
                return candidate_data

            username = self.extract_username(linkedin_url)
            if not username:
                self.logger.warning(f"Could not extract username from LinkedIn URL: {linkedin_url}")
                return candidate_data

            profile_data = self.get_public_profile(username)
            if profile_data:
                candidate_data['linkedin_data'] = profile_data
                candidate_data['linkedin_score'] = self._calculate_profile_score(profile_data)
            else:
                candidate_data['linkedin_score'] = 0

            return candidate_data

        except Exception as e:
            self.error_handler.handle_linkedin_error(e, candidate_data.get('email'))
            return candidate_data
    
    def extract_username(self, url: str) -> Optional[str]:
        """Extract username from LinkedIn URL"""
        patterns = [
            r'linkedin\.com/in/([^/]+)',
            r'linkedin\.com/pub/([^/]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url.lower())
            if match:
                return match.group(1)
        return None
    
    def get_public_profile(self, username: str) -> Dict[str, Any]:
        """Get public profile data from LinkedIn"""
        try:
            # Construct public profile URL
            url = f"https://www.linkedin.com/in/{username}/"
            
            # Make request with retry logic
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    
                    if response.status_code == 200:
                        if self._is_private_profile(response.text):
                            return {
                                'username': username,
                                'profile_score': 0,
                                'validation': {
                                    'profile_exists': True,
                                    'is_private': True,
                                    'error': 'Profile is private or restricted'
                                }
                            }
                        
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Extract basic information
                        name = self._extract_name(soup)
                        headline = self._extract_headline(soup)
                        location = self._extract_location(soup)
                        skills = self._extract_skills(soup)
                        experience = self._extract_experience(soup)
                        education = self._extract_education(soup)
                        
                        # Calculate profile score
                        profile_score = self._calculate_profile_score({
                            'name': name,
                            'headline': headline,
                            'location': location,
                            'skills': skills,
                            'experience': experience,
                            'education': education
                        })
                        
                        return {
                            'username': username,
                            'name': name,
                            'headline': headline,
                            'location': location,
                            'skills': skills,
                            'experience': experience,
                            'education': education,
                            'profile_score': profile_score,
                            'validation': {
                                'profile_exists': True,
                                'is_private': False,
                                'profile_completeness': profile_score / 100,
                                'last_updated': time.strftime('%Y-%m-%d')
                            }
                        }
                    elif response.status_code == 404:
                        return {
                            'username': username,
                            'profile_score': 0,
                            'validation': {
                                'profile_exists': False,
                                'error': 'Profile not found'
                            }
                        }
                    elif response.status_code == 403:
                        return {
                            'username': username,
                            'profile_score': 0,
                            'validation': {
                                'profile_exists': True,
                                'is_private': True,
                                'error': 'Access to profile is restricted'
                            }
                        }
                    else:
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay * (attempt + 1))
                            continue
                        return {
                            'username': username,
                            'profile_score': 0,
                            'validation': {
                                'profile_exists': False,
                                'error': f"Profile not accessible (Status: {response.status_code})"
                            }
                        }
                        
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                    return {
                        'username': username,
                        'profile_score': 0,
                        'validation': {
                            'profile_exists': False,
                            'error': 'Request timed out'
                        }
                    }
                except requests.exceptions.ConnectionError:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                    return {
                        'username': username,
                        'profile_score': 0,
                        'validation': {
                            'profile_exists': False,
                            'error': 'Connection error'
                        }
                    }
                
        except Exception as e:
            self.logger.error(f"Error fetching LinkedIn profile for {username}: {str(e)}")
            return {
                'username': username,
                'profile_score': 0,
                'validation': {
                    'profile_exists': False,
                    'error': str(e)
                }
            }
    
    def _is_private_profile(self, html_content: str) -> bool:
        """Check if profile is private or restricted"""
        private_indicators = [
            'This profile is not available',
            'This profile is private',
            'You need to be logged in to view this profile',
            'This profile is restricted',
            'Sign in to view this profile'
        ]
        
        return any(indicator.lower() in html_content.lower() for indicator in private_indicators)
    
    def _extract_name(self, soup: BeautifulSoup) -> str:
        """Extract name from profile"""
        try:
            name_elem = soup.find('h1', {'class': 'text-heading-xlarge'})
            return name_elem.text.strip() if name_elem else "N/A"
        except:
            return "N/A"
    
    def _extract_headline(self, soup: BeautifulSoup) -> str:
        """Extract headline from profile"""
        try:
            headline_elem = soup.find('div', {'class': 'text-body-medium'})
            return headline_elem.text.strip() if headline_elem else "N/A"
        except:
            return "N/A"
    
    def _extract_location(self, soup: BeautifulSoup) -> str:
        """Extract location from profile"""
        try:
            location_elem = soup.find('span', {'class': 'text-body-small'})
            return location_elem.text.strip() if location_elem else "N/A"
        except:
            return "N/A"
    
    def _extract_skills(self, soup: BeautifulSoup) -> list:
        """Extract skills from profile"""
        try:
            skills_section = soup.find('section', {'id': 'skills-section'})
            if not skills_section:
                return []
            
            skill_elements = skills_section.find_all('span', {'class': 'mr1 t-bold'})
            return [skill.text.strip() for skill in skill_elements]
        except:
            return []
    
    def _extract_experience(self, soup: BeautifulSoup) -> list:
        """Extract experience from profile"""
        try:
            experience_section = soup.find('section', {'id': 'experience-section'})
            if not experience_section:
                return []
            
            experience_items = experience_section.find_all('li', {'class': 'pv-entity__position-group-pager'})
            experiences = []
            
            for item in experience_items:
                try:
                    title = item.find('h3', {'class': 'pv-entity__name'}).text.strip()
                    company = item.find('p', {'class': 'pv-entity__secondary-title'}).text.strip()
                    duration = item.find('span', {'class': 'pv-entity__date-range'}).text.strip()
                    experiences.append({
                        'title': title,
                        'company': company,
                        'duration': duration
                    })
                except:
                    continue
            
            return experiences
        except:
            return []
    
    def _extract_education(self, soup: BeautifulSoup) -> list:
        """Extract education from profile"""
        try:
            education_section = soup.find('section', {'id': 'education-section'})
            if not education_section:
                return []
            
            education_items = education_section.find_all('li', {'class': 'pv-education-entity'})
            education = []
            
            for item in education_items:
                try:
                    school = item.find('h3', {'class': 'pv-entity__school-name'}).text.strip()
                    degree = item.find('p', {'class': 'pv-entity__degree-name'}).text.strip()
                    field = item.find('p', {'class': 'pv-entity__fos'}).text.strip()
                    education.append({
                        'school': school,
                        'degree': degree,
                        'field': field
                    })
                except:
                    continue
            
            return education
        except:
            return []
    
    def _calculate_profile_score(self, profile_data: Dict) -> int:
        """Calculate profile completeness score"""
        score = 0
        
        # Basic information (30 points)
        if profile_data.get('name') != "N/A":
            score += 10
        if profile_data.get('headline') != "N/A":
            score += 10
        if profile_data.get('location') != "N/A":
            score += 10
            
        # Skills (20 points)
        skills = profile_data.get('skills', [])
        if len(skills) >= 5:
            score += 20
        elif len(skills) > 0:
            score += len(skills) * 4
            
        # Experience (30 points)
        experience = profile_data.get('experience', [])
        if len(experience) >= 3:
            score += 30
        elif len(experience) > 0:
            score += len(experience) * 10
            
        # Education (20 points)
        education = profile_data.get('education', [])
        if len(education) >= 2:
            score += 20
        elif len(education) > 0:
            score += len(education) * 10
            
        return min(score, 100)

    def get_linkedin_profile(self, email: str) -> Dict[str, Any]:
        """Get LinkedIn profile data for a given email"""
        try:
            # Extract username from email
            username = email.split('@')[0]
            
            # Get profile data
            profile_data = self.get_public_profile(username)
            
            if profile_data and profile_data.get('validation', {}).get('profile_exists'):
                return {
                    'email': email,
                    'profile_url': f'https://www.linkedin.com/in/{username}',
                    'profile_data': profile_data,
                    'score': profile_data.get('profile_score', 0)
                }
            else:
                return {
                    'email': email,
                    'profile_url': None,
                    'profile_data': None,
                    'score': 0
                }
                
        except Exception as e:
            self.error_handler.handle_linkedin_error(e, email)
            return {
                'email': email,
                'profile_url': None,
                'profile_data': None,
                'score': 0
            } 