import re
import os
from pathlib import Path

class SecureCVLoader:
    """
    Loads and sanitizes the master CV to prevent PII leakage to the LLM.
    Enforces structural integrity and GDPR compliance.
    """
    
    PII_PATTERNS = {
        "email": r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
        "phone": r'(\+44\s?\(0\)\s?\d{10}|\d{5}\s\d{6}|\d{11}|07\d{9})',
        "url": r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*',
        "address": r'\d+\s[A-Z][a-z]+\s(?:Street|Road|Ave|Avenue|Lane|Dr|Drive|Way|Ct|Court)'
    }

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Master CV not found at {file_path}")

    def load_and_sanitize(self) -> str:
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sanitized = content
        # Mask PII with placeholders
        for label, pattern in self.PII_PATTERNS.items():
            sanitized = re.sub(pattern, f"[REDACTED_{label.upper()}]", sanitized)
            
        return sanitized

    def validate_structure(self, content: str) -> bool:
        """Basic check for Sprout headers."""
        required_headers = ["EXPERIENCE", "EDUCATION", "SKILLS"]
        found = [h for h in required_headers if h in content.upper()]
        return len(found) == len(required_headers)

if __name__ == "__main__":
    # Test run
    loader = SecureCVLoader("c:/Users/renan/Desktop/Side_projects/Ai agent/cold email agent/CV_automation/master_CV.md")
    try:
        clean_cv = loader.load_and_sanitize()
        print("Successfully loaded and sanitized CV.")
        if loader.validate_structure(clean_cv):
            print("Structure validated.")
        else:
            print("Structure validation failed - Missing headers.")
            
        print("\nPreview (First 500 chars):")
        print(clean_cv[:500])
    except Exception as e:
        print(f"Error: {e}")
