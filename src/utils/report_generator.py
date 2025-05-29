import json
import os
from datetime import datetime

class ReportGenerator:
    def __init__(self, config):
        self.config = config
        self.timestamp = datetime.now().isoformat()
    
    def generate_reports(self, candidates):
        """Generate both NDJSON and Markdown reports"""
        # Ensure output directory exists
        os.makedirs('outputs', exist_ok=True)
        
        # Sort candidates by total score
        sorted_candidates = sorted(candidates, key=lambda x: x.get('total_score', 0), reverse=True)
        
        # Generate NDJSON report
        self.generate_ndjson_report(sorted_candidates)
        
        # Generate Markdown summary
        self.generate_markdown_report(sorted_candidates)
        
        return sorted_candidates
    
    def generate_ndjson_report(self, candidates):
        """Generate NDJSON format report"""
        with open('outputs/report.ndjson', 'w') as f:
            for i, candidate in enumerate(candidates):
                record = {
                    'candidate_id': f"{i+1:03d}",
                    'filename': candidate.get('filename', ''),
                    'email': candidate.get('email', ''),
                    'github_username': candidate.get('github_username', ''),
                    'skills_score': candidate.get('skills_score', 0),
                    'experience_score': candidate.get('experience_score', 0),
                    'education_score': candidate.get('education_score', 0),
                    'github_score': candidate.get('github_score', 0),
                    'total_score': candidate.get('total_score', 0),
                    'experience_years': candidate.get('experience_years', 0),
                    'education': candidate.get('education', ''),
                    'skills': candidate.get('skills', []),
                    'timestamp': self.timestamp
                }
                f.write(json.dumps(record) + '\n')
    
    def generate_markdown_report(self, candidates):
        """Generate Markdown summary report"""
        top_candidates = candidates[:self.config['output']['top_candidates']]
        
        with open('outputs/summary.md', 'w') as f:
            f.write(f"# Resume Evaluation Report\n\n")
            f.write(f"**Generated:** {self.timestamp}\n\n")
            
            f.write(f"## Top {len(top_candidates)} Candidates\n\n")
            f.write("| Rank | Email | Total Score | Skills | Experience | GitHub | Years Exp |\n")
            f.write("|------|-------|-------------|--------|------------|---------|----------|\n")
            
            for i, candidate in enumerate(top_candidates):
                rank = i + 1
                email = candidate.get('email', 'N/A')
                total_score = f"{candidate.get('total_score', 0):.1f}/100"
                skills_score = f"{candidate.get('skills_score', 0):.1f}/100"
                github_score = f"{candidate.get('github_score', 0):.1f}/100"
                experience_years = candidate.get('experience_years', 0)
                
                f.write(f"| {rank} | {email} | {total_score} | {skills_score} | {experience_years} years | {github_score} | {experience_years} |\n")
            
            f.write(f"\n## Processing Summary\n\n")
            f.write(f"- **Total Resumes Processed:** {len(candidates)}\n")
            f.write(f"- **Candidates with GitHub:** {sum(1 for c in candidates if c.get('github_username'))}\n")
            f.write(f"- **Average Total Score:** {sum(c.get('total_score', 0) for c in candidates) / len(candidates):.1f}/100\n")
            
            # Skills breakdown
            all_skills = []
            for candidate in candidates:
                all_skills.extend(candidate.get('skills', []))
            
            if all_skills:
                skill_counts = {}
                for skill in all_skills:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1
                
                f.write(f"\n## Most Common Skills\n\n")
                sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                for skill, count in sorted_skills:
                    f.write(f"- **{skill}:** {count} candidates\n")