import json
import os
from datetime import datetime

class ReportGenerator:
    def __init__(self, config):
        self.config = config
        self.timestamp = datetime.now().isoformat()
    
    def generate_reports(self, candidates):
        """Generate both JSON and Markdown reports"""
        # Ensure output directory exists
        os.makedirs('outputs', exist_ok=True)
        
        # Sort candidates by total score
        sorted_candidates = sorted(candidates, key=lambda x: x.get('total_score', 0), reverse=True)
        
        # Generate JSON report
        self.generate_json_report(sorted_candidates)
        
        # Generate Markdown summary
        self.generate_markdown_report(sorted_candidates)
        
        return sorted_candidates
    
    def generate_json_report(self, candidates):
        """Generate JSON format report"""
        # Calculate summary statistics
        github_candidates = [c for c in candidates if c.get('github_username')]
        total_repos = sum(c.get('github_data', {}).get('repo_stats', {}).get('total_repos', 0) for c in github_candidates)
        total_contributions = sum(c.get('github_data', {}).get('contribution_stats', {}).get('total_contributions', 0) for c in github_candidates)
        total_stars = sum(c.get('github_data', {}).get('repo_stats', {}).get('total_stars', 0) for c in github_candidates)
        
        # Collect all languages and topics
        all_languages = {}
        all_topics = {}
        for candidate in github_candidates:
            languages = candidate.get('github_data', {}).get('repo_stats', {}).get('languages', {})
            topics = candidate.get('github_data', {}).get('repo_stats', {}).get('topics', {})
            for lang, count in languages.items():
                all_languages[lang] = all_languages.get(lang, 0) + count
            for topic, count in topics.items():
                all_topics[topic] = all_topics.get(topic, 0) + count
        
        # Collect all skills
        all_skills = {}
        for candidate in candidates:
            for skill in candidate.get('skills', []):
                all_skills[skill] = all_skills.get(skill, 0) + 1
        
        # Create summary report
        summary = {
            'timestamp': self.timestamp,
            'summary': {
                'total_candidates': len(candidates),
                'candidates_with_github': len(github_candidates),
                'average_total_score': sum(c.get('total_score', 0) for c in candidates) / len(candidates),
                'github_statistics': {
                    'total_repositories': total_repos,
                    'total_contributions': total_contributions,
                    'total_stars': total_stars,
                    'average_repos_per_profile': total_repos / len(github_candidates) if github_candidates else 0,
                    'average_contributions_per_profile': total_contributions / len(github_candidates) if github_candidates else 0
                },
                'top_languages': dict(sorted(all_languages.items(), key=lambda x: x[1], reverse=True)[:5]),
                'top_topics': dict(sorted(all_topics.items(), key=lambda x: x[1], reverse=True)[:5]),
                'top_skills': dict(sorted(all_skills.items(), key=lambda x: x[1], reverse=True)[:10])
            },
            'candidates': []
        }
        
        # Add candidate details
        for i, candidate in enumerate(candidates):
            github_data = candidate.get('github_data', {})
            contribution_stats = github_data.get('contribution_stats', {})
            repo_stats = github_data.get('repo_stats', {})
            
            candidate_data = {
                'rank': i + 1,
                'email': candidate.get('email', ''),
                'github_username': candidate.get('github_username', ''),
                'scores': {
                    'total': candidate.get('total_score', 0),
                    'skills': candidate.get('skills_score', 0),
                    'experience': candidate.get('experience_score', 0),
                    'education': candidate.get('education_score', 0),
                    'github': candidate.get('github_score', 0)
                },
                'experience_years': candidate.get('experience_years', 0),
                'education': candidate.get('education', ''),
                'skills': candidate.get('skills', []),
                'github_stats': {
                    'total_repos': repo_stats.get('total_repos', 0),
                    'total_stars': repo_stats.get('total_stars', 0),
                    'total_forks': repo_stats.get('total_forks', 0),
                    'total_contributions': contribution_stats.get('total_contributions', 0),
                    'commits': contribution_stats.get('commits', 0),
                    'pull_requests': contribution_stats.get('pull_requests', 0),
                    'issues': contribution_stats.get('issues', 0),
                    'recent_activity': contribution_stats.get('recent_activity', 0),
                    'languages': repo_stats.get('languages', {}),
                    'topics': repo_stats.get('topics', {})
                }
            }
            summary['candidates'].append(candidate_data)
        
        # Write to JSON file
        with open('outputs/summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
    
    def generate_markdown_report(self, candidates):
        """Generate Markdown summary report"""
        top_candidates = candidates[:self.config['output']['top_candidates']]
        
        with open('outputs/summary.md', 'w') as f:
            f.write(f"# Resume Evaluation Report\n\n")
            f.write(f"**Generated:** {self.timestamp}\n\n")
            
            # GitHub Statistics Summary
            github_candidates = [c for c in candidates if c.get('github_username')]
            if github_candidates:
                f.write("## GitHub Statistics Summary\n\n")
                total_repos = sum(c.get('github_data', {}).get('repo_stats', {}).get('total_repos', 0) for c in github_candidates)
                total_contributions = sum(c.get('github_data', {}).get('contribution_stats', {}).get('total_contributions', 0) for c in github_candidates)
                total_stars = sum(c.get('github_data', {}).get('repo_stats', {}).get('total_stars', 0) for c in github_candidates)
                
                f.write(f"- **Total GitHub Profiles:** {len(github_candidates)}\n")
                f.write(f"- **Total Repositories:** {total_repos}\n")
                f.write(f"- **Total Contributions:** {total_contributions}\n")
                f.write(f"- **Total Stars:** {total_stars}\n")
                f.write(f"- **Average Repositories per Profile:** {total_repos/len(github_candidates):.1f}\n")
                f.write(f"- **Average Contributions per Profile:** {total_contributions/len(github_candidates):.1f}\n\n")
            
            f.write(f"## Top {len(top_candidates)} Candidates\n\n")
            f.write("| Rank | Email | Total Score | Skills | Experience | GitHub | Years Exp | Repos | Contributions |\n")
            f.write("|------|-------|-------------|--------|------------|---------|----------|-------|--------------|\n")
            
            for i, candidate in enumerate(top_candidates):
                rank = i + 1
                email = candidate.get('email', 'N/A')
                total_score = f"{candidate.get('total_score', 0):.1f}/100"
                skills_score = f"{candidate.get('skills_score', 0):.1f}/100"
                github_score = f"{candidate.get('github_score', 0):.1f}/100"
                experience_years = candidate.get('experience_years', 0)
                
                # GitHub statistics
                github_data = candidate.get('github_data', {})
                repo_stats = github_data.get('repo_stats', {})
                contribution_stats = github_data.get('contribution_stats', {})
                total_repos = repo_stats.get('total_repos', 0)
                total_contributions = contribution_stats.get('total_contributions', 0)
                
                f.write(f"| {rank} | {email} | {total_score} | {skills_score} | {experience_years} years | {github_score} | {experience_years} | {total_repos} | {total_contributions} |\n")
            
            f.write(f"\n## Processing Summary\n\n")
            f.write(f"- **Total Resumes Processed:** {len(candidates)}\n")
            f.write(f"- **Candidates with GitHub:** {len(github_candidates)}\n")
            f.write(f"- **Average Total Score:** {sum(c.get('total_score', 0) for c in candidates) / len(candidates):.1f}/100\n")
            
            # GitHub Detailed Statistics
            if github_candidates:
                f.write(f"\n## GitHub Detailed Statistics\n\n")
                
                # Most common languages
                all_languages = {}
                for candidate in github_candidates:
                    languages = candidate.get('github_data', {}).get('repo_stats', {}).get('languages', {})
                    for lang, count in languages.items():
                        all_languages[lang] = all_languages.get(lang, 0) + count
                
                if all_languages:
                    f.write("### Most Common Languages\n\n")
                    sorted_languages = sorted(all_languages.items(), key=lambda x: x[1], reverse=True)[:5]
                    for lang, count in sorted_languages:
                        f.write(f"- **{lang}:** {count} repositories\n")
                
                # Most common topics
                all_topics = {}
                for candidate in github_candidates:
                    topics = candidate.get('github_data', {}).get('repo_stats', {}).get('topics', {})
                    for topic, count in topics.items():
                        all_topics[topic] = all_topics.get(topic, 0) + count
                
                if all_topics:
                    f.write("\n### Most Common Topics\n\n")
                    sorted_topics = sorted(all_topics.items(), key=lambda x: x[1], reverse=True)[:5]
                    for topic, count in sorted_topics:
                        f.write(f"- **{topic}:** {count} repositories\n")
            
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