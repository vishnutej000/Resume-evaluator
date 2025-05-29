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

- Python 3.8 or higher
- Gmail account with API access
- LinkedIn account (for profile verification)
- GitHub account (for repository analysis)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/resume-evaluator.git
cd resume-evaluator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```
Edit `.env` with your credentials:
```
GMAIL_CREDENTIALS_FILE=path/to/credentials.json
GITHUB_TOKEN=your_github_token
```

## Configuration

1. Gmail API Setup:
   - Go to Google Cloud Console
   - Create a new project
   - Enable Gmail API
   - Create credentials (OAuth 2.0)
   - Download credentials and save as `credentials.json`

2. Update `src/config/api_config.toml`:
```toml
[gmail]
# Basic query for resumes
query = "subject:\"Resume\" has:attachment (filename:pdf OR filename:docx)"
max_results = 10
attachment_size_limit = 10485760  # 10MB

# Alternative query examples:
# query = "subject:\"Job Application\" has:attachment (filename:pdf OR filename:docx)"
# query = "subject:\"CV\" has:attachment (filename:pdf OR filename:docx)"
# query = "subject:\"Application for Position\" has:attachment (filename:pdf OR filename:docx)"

[github]
api_url = "https://api.github.com"
min_repos = 3

[skills]
required = ["Python", "JavaScript", "SQL"]
preferred = ["React", "Node.js", "MongoDB"]
bonus = ["Docker", "Kubernetes", "AWS"]
```

## Customizing Gmail Search

The system uses Gmail's search operators to find relevant emails. Here are some common ways to customize the search:

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

Here are some useful Gmail search operators you can use:

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

## Usage

1. Run the main script:
```bash
python src/main.py
```

2. View results in the `outputs/` directory:
   - `candidate_reports/`: Individual candidate evaluations
   - `summary_report.txt`: Overall evaluation summary

## Project Structure

```
resume-evaluator/
├── src/
│   ├── agents/
│   │   ├── email_agent.py
│   │   ├── github_agent.py
│   │   ├── linkedin_agent.py
│   │   ├── resume_agent.py
│   │   └── skills_verifier.py
│   ├── tasks/
│   │   ├── fetch_task.py
│   │   ├── linkedin_task.py
│   │   ├── verify_task.py
│   │   └── report_task.py
│   ├── utils/
│   │   ├── error_handler.py
│   │   └── logger.py
│   ├── config/
│   │   └── api_config.toml
│   └── main.py
├── outputs/
├── tests/
├── requirements.txt
└── README.md
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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Google Gmail API
- GitHub API
- BeautifulSoup4
- PyPDF2
- python-docx

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Roadmap

- [ ] Add support for more resume formats
- [ ] Implement machine learning-based skill matching
- [ ] Add support for more professional networks
- [ ] Enhance scoring algorithms
- [ ] Add web interface
- [ ] Implement real-time notifications 
