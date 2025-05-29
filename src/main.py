import os
import sys
import toml
from pathlib import Path
from dotenv import load_dotenv
from crewai import Crew

# Add src directory to Python path for proper imports
src_path = Path(__file__).parent
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

def load_config():
    """Load configuration files"""
    config_dir = Path(__file__).parent / 'config'
    criteria = toml.load(config_dir / 'criteria.toml')
    api_config = toml.load(config_dir / 'api_config.toml')
    
    # Merge configs
    config = {**criteria, **api_config}
    return config

def setup_agents(config):
    """Initialize all agents"""
    # Setup authentication
    gmail_auth = GmailAuth("src/utils/gmail_credentials.json")
    if not gmail_auth.authenticate():
        print("❌ Gmail authentication failed")
        return None, None, None, None, None
    github_auth = GitHubAuth()
    
    # Setup utility classes
    resume_parser = ResumeParser()
    error_handler = ErrorHandler()
    
    # Initialize agents
    email_agent = EmailAgent(gmail_auth.get_service(), config, error_handler)
    resume_agent = ResumeAgent(resume_parser, config, error_handler)
    github_agent = GitHubAgent(config, github_auth, error_handler)
    linkedin_agent = LinkedInAgent(config=config, error_handler=error_handler)
    skills_verifier = SkillsVerifier(config, error_handler)
    
    return email_agent, resume_agent, github_agent, linkedin_agent, skills_verifier

def setup_tasks(email_agent, resume_agent, github_agent, linkedin_agent, skills_verifier, error_handler):
    """Setup all tasks with proper CrewAI integration"""
    fetch_task = FetchTask(
        agent=email_agent,
        error_handler=error_handler
    )
    parse_task = ParseTask(
        agent=resume_agent,
        description="Parse and extract relevant information from resume documents"
    )
    analyze_task = AnalyzeTask(
        agent=github_agent,
        description="Analyze candidates' GitHub profiles and calculate technical scores"
    )
    linkedin_task = LinkedInTask(
        agent=linkedin_agent,
        error_handler=error_handler
    )
    verify_task = VerifyTask(
        agent=skills_verifier,
        error_handler=error_handler
    )
    
    return fetch_task, parse_task, analyze_task, linkedin_task, verify_task

def main():
    """Main execution function"""
    print("Starting Resume Evaluator...")
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Load configuration
        config = load_config()
        print("✓ Configuration loaded successfully")
        
        # Setup agents
        email_agent, resume_agent, github_agent, linkedin_agent, skills_verifier = setup_agents(config)
        print("✓ Agents initialized successfully")
        
        # Setup tasks
        error_handler = ErrorHandler()
        fetch_task, parse_task, analyze_task, linkedin_task, verify_task = setup_tasks(
            email_agent, resume_agent, github_agent, linkedin_agent, skills_verifier, error_handler
        )
        print("✓ Tasks configured successfully")
        
        print("Starting workflow execution...")
        
        # Execute workflow step by step
        print("Fetching email attachments...")
        attachments = fetch_task.execute()
        print(f"Found {len(attachments)} resume attachments")
        for att in attachments:
            print(f"  - {att['filename']}")
        
        if not attachments:
            print("No attachments found. Exiting.")
            return
        
        print("Parsing and evaluating resumes...")
        candidates = parse_task.execute(attachments)
        for result in candidates:
            print(f"Parsed: {result['filename']}")
            if result.get('error'):
                print(f"  Error: {result['error']}")
            else:
                print(f"  Email: {result.get('email', '')}")
                print(f"  Skills: {result.get('skills', [])}")
                print(f"  Experience: {result.get('experience_years', 0)} years")
                print(f"  Education: {result.get('education', '')}")
        print(f"Successfully parsed {len([c for c in candidates if not c.get('error')])} resumes")
        if not candidates or all(c.get('error') for c in candidates):
            print("No valid candidates found. Exiting.")
            return
        
        print("Analyzing GitHub profiles...")
        github_enriched = analyze_task.execute(candidates)
        print(f"Enriched {len(github_enriched)} candidates with GitHub data")
        
        print("Analyzing LinkedIn profiles...")
        linkedin_enriched = linkedin_task.execute(github_enriched)
        print(f"Enriched {len(linkedin_enriched)} candidates with LinkedIn data")
        
        print("Verifying skills...")
        final_candidates = verify_task.execute(linkedin_enriched)
        print(f"Verified skills for {len(final_candidates)} candidates")
        
        # Generate reports
        print("Generating reports...")
        report_generator = ReportGenerator(config)
        final_candidates = report_generator.generate_reports(final_candidates)
        
        print(f"✓ Report generation complete!")
        if final_candidates:
            top_candidate = final_candidates[0]
            print(f"Top candidate: {top_candidate['email']} with score {top_candidate['total_score']:.1f}")
        print("Reports saved to outputs/ directory")
        
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False
    
    return True

if __name__ == "__main__":
    main()