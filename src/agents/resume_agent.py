import toml

class ResumeAgentLogic:
    """Resume parsing and evaluation logic separate from CrewAI Agent"""
    def __init__(self, parser, config, error_handler):
        self.parser = parser
        self.config = config
        self.error_handler = error_handler
        self.criteria = config

class ResumeAgent:
    def __init__(self, parser, config, error_handler):
        self.parser = parser
        self.config = config
        self.error_handler = error_handler

    def evaluate_candidates(self, attachments):
        """Evaluate candidates based on resume content"""
        candidates = []
        for attachment in attachments:
            try:
                result = self.parser.parse_resume(attachment['filename'], attachment['content'])
                if result.get('error'):
                    print(f"[DEBUG] Parsing error for {attachment['filename']}: {result['error']}")
                candidates.append(result)
            except Exception as e:
                print(f"[DEBUG] Exception during parsing {attachment['filename']}: {e}")
                candidates.append({'filename': attachment['filename'], 'error': str(e)})
        return candidates

    def process_resume(self, attachment):
        """Process individual resume"""
        try:
            parsed_data = self.parser.parse_resume(
                attachment['filename'],
                attachment['content']
            )
            if not parsed_data:
                return None
            candidate = {
                'filename': attachment['filename'],
                'email': parsed_data['email'],
                'github_username': parsed_data['github_username'],
                'skills': parsed_data['skills'],
                'experience_years': parsed_data['experience_years'],
                'education': parsed_data['education'],
                'text': parsed_data['text']
            }
            # Calculate scores
            candidate['skills_score'] = self.calculate_skills_score(parsed_data['skills'])
            candidate['experience_score'] = self.calculate_experience_score(parsed_data['experience_years'])
            candidate['education_score'] = self.calculate_education_score(parsed_data['education'])
            return candidate
        except Exception as e:
            self.error_handler.handle_parsing_error(e, attachment['filename'])
            return None

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