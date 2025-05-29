# filepath: c:\Users\USER\resume-evaluator\src\agents\github_agent.py
import requests
import json

class GitHubLogic:
    """GitHub API logic separate from CrewAI Agent"""
    def __init__(self, auth, config, error_handler):
        self.auth = auth
        self.config = config
        self.error_handler = error_handler
        self.cache = {}

    def get_user_data(self, username):
        """Get GitHub user data"""
        if username in self.cache:
            return self.cache[username]
        try:
            user_url = f"{self.config['github']['api_url']}/users/{username}"
            user_response = requests.get(user_url, headers=self.auth.get_headers())
            if user_response.status_code != 200:
                return None
            user_data = user_response.json()
            repos_url = f"{self.config['github']['api_url']}/users/{username}/repos"
            repos_response = requests.get(repos_url, headers=self.auth.get_headers())
            repos_data = repos_response.json() if repos_response.status_code == 200 else []
            events_url = f"{self.config['github']['api_url']}/users/{username}/events"
            events_response = requests.get(events_url, headers=self.auth.get_headers())
            events_data = events_response.json() if events_response.status_code == 200 else []
            github_profile = {
                'user': user_data,
                'repos': repos_data,
                'events': events_data,
                'public_repos': user_data.get('public_repos', 0),
                'followers': user_data.get('followers', 0),
                'following': user_data.get('following', 0)
            }
            self.cache[username] = github_profile
            return github_profile
        except Exception as e:
            self.error_handler.handle_github_error(e, {'username': username})
            return None

class GitHubAgent:
    def __init__(self, config, github_auth, error_handler):
        self.config = config
        self.github_auth = github_auth
        self.error_handler = error_handler
        self.logic = GitHubLogic(github_auth, config, error_handler)

    def enrich_candidates(self, candidates):
        """Enrich candidates with GitHub data"""
        for candidate in candidates:
            if candidate.get('github_username'):
                try:
                    github_data = self.logic.get_user_data(candidate['github_username'])
                    candidate['github_data'] = github_data
                    candidate['github_score'] = self.calculate_github_score(github_data)
                    candidate['skills_score'] = self.calculate_skills_score(candidate['skills'])
                    candidate['experience_score'] = self.calculate_experience_score(candidate['experience_years'])
                    candidate['education_score'] = self.calculate_education_score(candidate['education'])
                    candidate['total_score'] = self.calculate_total_score(candidate)
                except Exception as e:
                    self.error_handler.handle_github_error(e, candidate['github_username'])
            else:
                candidate['github_score'] = 0
                candidate['skills_score'] = self.calculate_skills_score(candidate['skills'])
                candidate['experience_score'] = self.calculate_experience_score(candidate['experience_years'])
                candidate['education_score'] = self.calculate_education_score(candidate['education'])
                candidate['total_score'] = self.calculate_total_score(candidate)
        return candidates

    def calculate_github_score(self, github_data):
        """Calculate GitHub contribution score"""
        if not github_data:
            return 0
        score = 0
        public_repos = github_data.get('public_repos', 0)
        min_repos = self.config.get('github', {}).get('min_repos', 3)
        if public_repos >= min_repos:
            score += 30
        elif public_repos > 0:
            score += (public_repos / min_repos) * 30
        events = github_data.get('events', [])
        recent_activity = len([e for e in events if e.get('type') in ['PushEvent', 'PullRequestEvent']])
        if recent_activity >= 10:
            score += 40
        elif recent_activity > 0:
            score += (recent_activity / 10) * 40
        followers = github_data.get('followers', 0)
        if followers >= 50:
            score += 20
        elif followers > 0:
            score += (followers / 50) * 20
        repos = github_data.get('repos', [])
        total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
        if total_stars >= 100:
            score += 10
        elif total_stars > 0:
            score += (total_stars / 100) * 10
        return min(score, 100)

    def calculate_skills_score(self, skills):
        """Calculate skills score based on criteria"""
        if not skills:
            return 0
        required_skills = self.config['skills']['required']
        preferred_skills = self.config['skills']['preferred']
        bonus_skills = self.config['skills']['bonus']
        score = 0
        required_count = sum(1 for skill in required_skills if skill in skills)
        preferred_count = sum(1 for skill in preferred_skills if skill in skills)
        bonus_count = sum(1 for skill in bonus_skills if skill in skills)
        # Scoring formula
        score = (required_count / len(required_skills)) * 60
        score += (preferred_count / len(preferred_skills)) * 30
        score += min(bonus_count * 5, 10)
        return min(score, 100)

    def calculate_experience_score(self, years):
        """Calculate experience score"""
        if years < self.config['experience']['minimum_years']:
            return 0
        senior_threshold = self.config['experience']['senior_threshold']
        if years >= senior_threshold:
            return 100
        return (years / senior_threshold) * 100

    def calculate_education_score(self, education):
        """Calculate education score"""
        if not education:
            return 0
        accepted_degrees = self.config['education']['accepted_degrees']
        for degree in accepted_degrees:
            if degree.lower() in education.lower():
                return 100
        return 50  # Partial credit for other education

    def calculate_total_score(self, candidate):
        """Calculate weighted total score"""
        github_config = self.config.get('github', {})
        experience_config = self.config.get('experience', {})
        education_config = self.config.get('education', {})
        skills_weight = 0.4  # Default for skills
        experience_weight = experience_config.get('weight', 0.3)
        education_weight = education_config.get('weight', 0.3)
        github_weight = github_config.get('weight', 0.4)
        total = (
            candidate.get('skills_score', 0) * skills_weight +
            candidate.get('experience_score', 0) * experience_weight +
            candidate.get('education_score', 0) * education_weight +
            candidate.get('github_score', 0) * github_weight
        )
        candidate['total_score'] = round(total, 2)
        return candidate['total_score']
