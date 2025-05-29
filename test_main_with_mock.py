import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add src directory to Python path for proper imports
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from utils.auth import GmailAuth, GitHubAuth
from utils.parsers import ResumeParser
from utils.error_handler import ErrorHandler
from utils.report_generator import ReportGenerator
from agents.email_agent import EmailAgent
from agents.resume_agent import ResumeAgent
from agents.github_agent import GitHubAgent
from agents.linkedin_agent import LinkedInAgent
from agents.skills_verifier import SkillsVerifier
from tasks.fetch_task import FetchTask
from tasks.parse_task import ParseTask
from tasks.analyze_task import AnalyzeTask
from tasks.linkedin_task import LinkedInTask
from tasks.verify_task import VerifyTask

# Mock data for attachments
mock_attachments = [
    {
        'filename': 'test_resume_1.pdf',
        'content': MagicMock(),  # Simulate file-like object
        'message_id': 'mock1'
    },
    {
        'filename': 'test_resume_2.docx',
        'content': MagicMock(),
        'message_id': 'mock2'
    },
    {
        'filename': 'real_resume.pdf',
        'content': MagicMock(),  # Simulate a real email attachment
        'message_id': 'mock3'
    }
]

# Mock candidate data after parsing
mock_candidates = [
    {
        'filename': 'test_resume_1.pdf',
        'email': 'alice@example.com',
        'github_username': 'alicehub',
        'skills': ['Python', 'ML'],
        'experience_years': 3,
        'education': 'MSc',
        'text': 'Alice resume text',
        'skills_score': 8,
        'experience_score': 7,
        'education_score': 9
    },
    {
        'filename': 'test_resume_2.docx',
        'email': 'bob@example.com',
        'github_username': 'bobgit',
        'skills': ['Java', 'Cloud'],
        'experience_years': 5,
        'education': 'BSc',
        'text': 'Bob resume text',
        'skills_score': 7,
        'experience_score': 8,
        'education_score': 8
    }
]

def generate_mock_resume_data():
    """Generate a mock resume data dictionary for testing."""
    return {
        'filename': 'mock_resume.pdf',
        'email': 'mock@example.com',
        'github_username': 'mockuser',
        'skills': ['Python', 'Machine Learning', 'Data Analysis'],
        'experience_years': 5,
        'education': 'MSc in Computer Science',
        'text': 'Mock resume text for testing purposes.',
        'skills_score': 9,
        'experience_score': 8,
        'education_score': 9
    }

# Add the generated mock resume to the mock_candidates list
mock_candidates.append(generate_mock_resume_data())

def run_mock_workflow():
    print("\n--- Running Resume Evaluator with Mock Data ---\n")
    # Setup config and error handler
    config = {'gmail': {'query': '', 'max_results': 10, 'attachment_size_limit': 10*1024*1024}, 'github': {}, 'linkedin': {}}
    error_handler = ErrorHandler()

    # Setup agents (with mocks where needed)
    email_agent = EmailAgent(None, config, error_handler)
    resume_agent = ResumeAgent(config, ResumeParser(), error_handler)
    github_agent = GitHubAgent(config, GitHubAuth(), error_handler)
    linkedin_agent = LinkedInAgent(config, error_handler)
    skills_verifier = SkillsVerifier(config, error_handler)

    # Mock fetch_attachments to return mock_attachments
    email_agent.fetch_attachments = MagicMock(return_value=mock_attachments)
    # Mock resume_agent.evaluate_candidates to return mock_candidates
    resume_agent.evaluate_candidates = MagicMock(return_value=mock_candidates)
    # Mock github_agent.enrich_candidates to just pass through
    github_agent.enrich_candidates = MagicMock(side_effect=lambda cands: cands)
    # Mock linkedin_agent.analyze_profiles to just pass through
    linkedin_agent.analyze_profiles = MagicMock(side_effect=lambda cands: cands)
    # Mock skills_verifier.verify_skills to just pass through
    skills_verifier.verify_skills = MagicMock(side_effect=lambda cands: cands)

    # Setup tasks
    fetch_task = FetchTask(agent=email_agent, error_handler=error_handler)
    parse_task = ParseTask(agent=resume_agent, description="Parse resumes")
    analyze_task = AnalyzeTask(agent=github_agent, description="Analyze GitHub")
    linkedin_task = LinkedInTask(agent=linkedin_agent, error_handler=error_handler)
    verify_task = VerifyTask(agent=skills_verifier, error_handler=error_handler)

    # Run workflow
    attachments = fetch_task.execute()
    print(f"Fetched {len(attachments)} mock attachments")
    candidates = parse_task.execute(attachments)
    print(f"Parsed {len(candidates)} mock candidates")
    github_enriched = analyze_task.execute(candidates)
    print(f"GitHub enriched {len(github_enriched)} candidates")
    linkedin_enriched = linkedin_task.execute(github_enriched)
    print(f"LinkedIn enriched {len(linkedin_enriched)} candidates")
    final_candidates = verify_task.execute(linkedin_enriched)
    print(f"Skills verified for {len(final_candidates)} candidates")
    print("\nMock workflow completed successfully!\n")

if __name__ == "__main__":
    run_mock_workflow() 