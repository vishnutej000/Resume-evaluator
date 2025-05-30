# Resume Evaluation System

An intelligent system for automated resume evaluation and candidate screening. This system processes resumes from emails, analyzes GitHub profiles, and generates comprehensive evaluation reports.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Integration](#api-integration)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Features

### Core Features
- Email-based resume collection and processing
- GitHub profile analysis
- Automated candidate scoring
- Detailed evaluation reports
- Customizable scoring criteria
- Multi-format report generation (JSON, Markdown, PDF, HTML)

### Advanced Features
- Integration with Gmail API
- GitHub profile analysis
- LinkedIn profile integration (optional)
- Calendar integration for interviews
- Automated notifications
- Backup and security features

## Prerequisites

### System Requirements
- Python 3.8 or higher
- 4GB RAM minimum
- 1GB free disk space
- Internet connection for API access

### Required Accounts
- Gmail account with API access
- GitHub account with API token
- LinkedIn account (optional)
- Google Calendar account (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/resume-evaluation.git
cd resume-evaluation
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up API credentials:
   - Create a `config` directory in the project root
   - Add your API credentials:
     - Gmail: `config/gmail_credentials.json`
     - GitHub: Add token to `recruiter_config.toml`
     - LinkedIn: Add credentials to `recruiter_config.toml`
     - Calendar: `config/calendar_credentials.json`

## Configuration

### Basic Configuration
1. Edit `src/config/recruiter_config.toml` to set your requirements:
   - Email search settings
   - Scoring weights
   - Required skills
   - Experience requirements
   - Education requirements
   - GitHub requirements
   - Output settings

2. Configure email settings:
   - Set your Gmail credentials
   - Configure email search parameters
   - Set notification preferences

3. Configure GitHub settings:
   - Add your GitHub token
   - Set minimum requirements
   - Configure preferred topics and languages

### Advanced Configuration

#### Scoring Configuration
```toml
[scoring.weights]
skills = 30
experience = 25
education = 15
github = 30
```

#### Skills Configuration
```toml
[skills]
required_skills = [
    "Python",
    "JavaScript",
    "React",
    "SQL"
]
```

#### Experience Configuration
```toml
[experience]
min_years = 2
preferred_years = 5
max_years = 15
```

## Usage

### Basic Usage

1. Start the system:
```bash
python src/main.py
```

2. Monitor the process:
- Check `outputs/logs/app.log` for detailed logs
- View reports in `outputs/reports/`
- Check candidate data in `outputs/candidates/`

### Advanced Usage

#### Automated Processing
1. Enable auto-processing in `recruiter_config.toml`:
```toml
[automation]
auto_process_new_emails = true
check_interval_minutes = 60
```

2. Set up notifications:
```toml
[notifications]
send_notifications = true
notification_email = "your@email.com"
```

#### Custom Report Generation
1. Configure report settings:
```toml
[report]
company_name = "Your Company"
position_title = "Software Engineer"
```

2. Generate custom reports:
```bash
python src/utils/report_generator.py --format pdf
```

## Project Structure

```
resume-evaluation/
├── src/
│   ├── config/
│   │   ├── recruiter_config.toml
│   │   └── criteria.toml
│   ├── utils/
│   │   ├── email_processor.py
│   │   ├── github_analyzer.py
│   │   ├── resume_parser.py
│   │   ├── report_generator.py
│   │   └── config_validator.py
│   └── main.py
├── outputs/
│   ├── reports/
│   ├── candidates/
│   └── logs/
├── config/
│   ├── gmail_credentials.json
│   └── calendar_credentials.json
├── requirements.txt
└── README.md
```

## API Integration

### Gmail API Setup
1. Go to Google Cloud Console
2. Create a new project
3. Enable Gmail API
4. Create credentials
5. Download and save as `config/gmail_credentials.json`

### GitHub API Setup
1. Go to GitHub Settings
2. Generate new token
3. Add to `recruiter_config.toml`:
```toml
[integration.api_configs.github]
token = "your_github_token"
```

### LinkedIn API Setup (Optional)
1. Create LinkedIn Developer account
2. Create new application
3. Add credentials to config:
```toml
[integration.api_configs.linkedin]
client_id = "your_client_id"
client_secret = "your_client_secret"
```

## Security

### Data Protection
- Sensitive data masking
- Encrypted storage
- Secure API handling
- Access control

### Configuration
```toml
[security]
mask_sensitive_data = true
encrypt_output_files = true
audit_trail = true
```

## Troubleshooting

### Common Issues

1. Email Processing Issues
   - Check Gmail API credentials
   - Verify email search settings
   - Check attachment types

2. GitHub Analysis Issues
   - Verify GitHub token
   - Check rate limits
   - Verify repository access

3. Report Generation Issues
   - Check output directory permissions
   - Verify template files
   - Check file format settings

### Logging
- Check `outputs/logs/app.log` for detailed error information
- Enable debug logging in `recruiter_config.toml`:
```toml
[logging]
log_level = "DEBUG"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Development Setup
1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
python -m pytest tests/
```

3. Check code style:
```bash
flake8 src/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
1. Check the troubleshooting guide
2. Review the documentation
3. Open an issue on GitHub
4. Contact the maintainers

## Acknowledgments

- Gmail API
- GitHub API
- LinkedIn API
- Google Calendar API
- All contributors and users 