import toml
import os
from typing import Dict, List, Any
import sys

class ConfigValidator:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load the TOML configuration file"""
        try:
            with open(self.config_path, 'r') as f:
                return toml.load(f)
        except Exception as e:
            print(f"Error loading config file: {e}")
            sys.exit(1)
    
    def validate_scoring_weights(self) -> bool:
        """Validate that scoring weights total 100"""
        weights = self.config['scoring']['weights']
        total = sum(weights.values())
        if total != 100:
            print(f"Warning: Scoring weights total {total}, should be 100")
            return False
        return True
    
    def validate_required_fields(self) -> bool:
        """Validate that all required fields are present"""
        required_sections = [
            'email_search', 'scoring', 'skills', 'experience',
            'education', 'github', 'output', 'report'
        ]
        
        for section in required_sections:
            if section not in self.config:
                print(f"Error: Missing required section '{section}'")
                return False
        return True
    
    def validate_email_search(self) -> bool:
        """Validate email search configuration"""
        search = self.config['email_search']
        if not search['subject_keywords']:
            print("Error: No subject keywords specified")
            return False
        if not search['attachment_types']:
            print("Error: No attachment types specified")
            return False
        return True
    
    def validate_skills(self) -> bool:
        """Validate skills configuration"""
        skills = self.config['skills']
        if not skills['required_skills']:
            print("Warning: No required skills specified")
        return True
    
    def validate_experience(self) -> bool:
        """Validate experience requirements"""
        exp = self.config['experience']
        if exp['min_years'] > exp['preferred_years']:
            print("Error: Minimum years cannot be greater than preferred years")
            return False
        if exp['preferred_years'] > exp['max_years']:
            print("Error: Preferred years cannot be greater than maximum years")
            return False
        return True
    
    def validate_github(self) -> bool:
        """Validate GitHub requirements"""
        github = self.config['github']
        if github['min_repositories'] < 0:
            print("Error: Minimum repositories cannot be negative")
            return False
        if github['min_stars'] < 0:
            print("Error: Minimum stars cannot be negative")
            return False
        return True
    
    def validate_output(self) -> bool:
        """Validate output configuration"""
        output = self.config['output']
        if output['top_candidates'] < 1:
            print("Error: Top candidates must be at least 1")
            return False
        return True
    
    def validate_all(self) -> bool:
        """Run all validations"""
        validations = [
            self.validate_required_fields,
            self.validate_scoring_weights,
            self.validate_email_search,
            self.validate_skills,
            self.validate_experience,
            self.validate_github,
            self.validate_output
        ]
        
        all_valid = True
        for validation in validations:
            if not validation():
                all_valid = False
        
        return all_valid
    
    def save_config(self) -> None:
        """Save the configuration back to file"""
        try:
            with open(self.config_path, 'w') as f:
                toml.dump(self.config, f)
            print(f"Configuration saved to {self.config_path}")
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    def update_config(self, section: str, key: str, value: Any) -> None:
        """Update a specific configuration value"""
        if section not in self.config:
            print(f"Error: Section '{section}' not found")
            return
        
        if key not in self.config[section]:
            print(f"Error: Key '{key}' not found in section '{section}'")
            return
        
        self.config[section][key] = value
        print(f"Updated {section}.{key} = {value}")

def main():
    """Main function to run the validator"""
    config_path = "src/config/recruiter_config.toml"
    validator = ConfigValidator(config_path)
    
    print("Validating configuration...")
    if validator.validate_all():
        print("Configuration is valid!")
    else:
        print("\nPlease fix the above issues in your configuration file.")
        print("You can edit the file directly or use the update_config method.")
    
    # Example of how to update configuration
    # validator.update_config('email_search', 'max_results', 20)
    # validator.save_config()

if __name__ == "__main__":
    main() 