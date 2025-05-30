# Resume Evaluator

An intelligent resume evaluation system that automatically processes, analyzes, and ranks candidate resumes using multiple data sources including Gmail, LinkedIn, and GitHub.

## Features

- **Automated Resume Processing**
  - Fetches resumes from Gmail attachments
  - Supports PDF and DOCX formats
  - Extracts key information (skills, experience, education)
  - Customizable email search queries

- **Multi-Source Candidate Analysis**
  - LinkedIn profile enrichment
  - GitHub activity analysis
  - Portfolio website verification
  - Skills verification across platforms

- **Intelligent Scoring System**
  - Skills-based scoring
  - Experience evaluation
  - Education assessment
  - GitHub contribution analysis
  - LinkedIn profile completeness

- **Comprehensive Reporting**
  - Detailed candidate reports
  - Skill verification results
  - Confidence scoring
  - Top candidate identification

## Prerequisites

- Python 3.10 or higher
- Gmail account with API access
- LinkedIn account (for profile verification)
- GitHub account (for repository analysis)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/vishnutej000/Resume-evaluator.git
cd resume-evaluator
```

2. Create and activate a virtual environment:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```
or use 

uv add -r requirements.txt   

## Setup and Configuration

### 1. Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as application type
   - Verify yourself as a test user 
   - Download the credentials JSON file
5. Save the credentials:
   - Rename the downloaded file to `gmail_credentials.json`
   - Place it in `src/utils/` directory

### 2. Generate Gmail Token

1. Run the token generation script:
```bash
python src/utils/get_gmail_token.py
```

2. A browser window will open automatically
3. Sign in with your Google account
4. You'll see a warning that the app isn't verified (normal for development)
5. Click "Continue" or "Advanced" and then "Go to [Your App Name]"
6. Grant the requested permissions
7. The token will be saved to `src/utils/gmail_token.json`

### 3. GitHub Token Setup

1. Go to [GitHub Settings > Developer Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Click "Generate new token"
3. Select scopes:
   - `repo` (Full control of private repositories)
   - `read:user` (Read user profile data)
   - `user:email` (Read user email addresses)
4. Copy the generated token
5. Create a `.env` file in the project root:
```bash
cp .env.example .env
```
6. Add your GitHub token to `.env`:
```
GITHUB_TOKEN=your_github_token_here
```
7. Add your recruiting Parameters to `src/config/recruiter_config.toml`:
```
Change paramaters 
```


## Customizing Email Search

The system uses Gmail's search operators to find relevant emails. You can customize the search in `src/config/api_config.toml`:

```toml
[gmail]
# Basic query for resumes
query = "subject:\"Resume\" has:attachment (filename:pdf OR filename:docx)"
max_results = 10
attachment_size_limit = 10485760  # 10MB
```

### Common Search Patterns

1. **Subject-based Search**:
```toml
# Search for specific subject lines
query = "subject:\"Resume\""
query = "subject:\"Job Application\""
query = "subject:\"CV\""
query = "subject:\"Application for Position\""
```

2. **Combined Search**:
```toml
# Search for multiple subjects
query = "subject:(\"Resume\" OR \"CV\" OR \"Job Application\")"
```

3. **Time-based Search**:
```toml
# Search within specific time periods
query = "subject:\"Resume\" newer_than:7d"  # Last 7 days
query = "subject:\"Resume\" after:2024/01/01"  # After specific date
```

4. **Label-based Search**:
```toml
# Search in specific labels
query = "label:applications subject:\"Resume\""
```

5. **Complex Queries**:
```toml
# Combine multiple conditions
query = "subject:\"Resume\" has:attachment (filename:pdf OR filename:docx) newer_than:30d"
query = "subject:(\"Resume\" OR \"CV\") has:attachment (filename:pdf OR filename:docx) in:inbox"
```

### Gmail Search Operators

Here are useful Gmail search operators:

- `subject:` - Search in subject line
- `from:` - Search by sender
- `to:` - Search by recipient
- `has:attachment` - Emails with attachments
- `filename:` - Search by attachment type
- `newer_than:` - Emails newer than specified time
- `older_than:` - Emails older than specified time
- `after:` - Emails after specific date
- `before:` - Emails before specific date
- `in:inbox` - Search in inbox
- `label:` - Search in specific label
- `is:starred` - Search starred emails
- `is:unread` - Search unread emails

## Running the System

1. Start the evaluation process:
```bash
python src/main.py
```

2. The system will:
   - Authenticate with Gmail
   - Search for resume attachments
   - Parse and analyze resumes
   - Check GitHub profiles
   - Verify LinkedIn profiles
   - Generate reports

3. View results in the `outputs/` directory:
   - `candidate_reports/`: Individual candidate evaluations
   - `summary_report.txt`: Overall evaluation summary

## Project Structure

```
resume-evaluator/
├── src/
│   ├── agents/
│   │   ├── email_agent.py      # Gmail interaction
│   │   ├── github_agent.py     # GitHub profile analysis
│   │   ├── linkedin_agent.py   # LinkedIn profile analysis
│   │   ├── resume_agent.py     # Resume parsing
│   │   └── skills_verifier.py  # Skills verification
│   ├── tasks/
│   │   ├── fetch_task.py       # Email fetching
│   │   ├── linkedin_task.py    # LinkedIn analysis
│   │   ├── verify_task.py      # Skills verification
│   │   └── report_task.py      # Report generation
│   ├── utils/
│   │   ├── error_handler.py    # Error handling
│   │   ├── logger.py          # Logging
│   │   ├── auth.py            # Authentication
│   │   └── get_gmail_token.py # Gmail token generation
│   ├── config/
│   │   └── api_config.toml    # Configuration
│   └── main.py                # Main script
├── outputs/                   # Generated reports
├── tests/                    # Test files
├── requirements.txt          # Dependencies
└── README.md                # Documentation
```

## Troubleshooting

### Common Issues

1. **Gmail Authentication Failed**
   - Check if `gmail_credentials.json` exists in `src/utils/`
   - Verify the credentials file is valid
   - Run `get_gmail_token.py` to generate a new token

2. **No Attachments Found**
   - Verify your Gmail search query in `api_config.toml`
   - Check if emails match the search criteria
   - Ensure attachments are PDF or DOCX format

3. **GitHub API Errors**
   - Verify GitHub token in `.env`
   - Check token permissions
   - Ensure token hasn't expired

4. **LinkedIn Verification Issues**
   - Check internet connection
   - Verify LinkedIn profile URLs
   - Ensure profiles are public

### Debug Mode

Enable debug logging by setting environment variable:
```bash
# Windows
set DEBUG=true

# macOS/Linux
export DEBUG=true
```

## Development

1. Run tests:
```bash
pytest tests/
```

2. Code formatting:
```bash
black src/
flake8 src/
mypy src/
```


