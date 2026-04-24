import subprocess
import re
import json
import pandas as pd

df = pd.read_csv("jobs-prefinal.csv")

def get_job_description_with_curl(url):
    """
    Fetch a URL using curl and try to extract the job description.
    Note: This works best if the job description is embedded in the initial HTML
    or passed via a JSON-LD script tag.
    """
    try:
        # Execute curl command: follow redirects, wait 10s, hide progress meter
        cmd = ['curl', '-s', '-L', '--max-time', '10', url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode != 0:
            return f"ERROR: curl failed with code {result.returncode}"
        
        html_content = result.stdout
        
        # Attempt 1: Look for the specific div class you mentioned
        # This uses regex to extract content between the div tags
        pattern = r'<div\s+[^>]*class="[^"]*GDU7fA[^"]*"[^>]*>(.*?)</div>'
        matches = re.findall(pattern, html_content, re.DOTALL)
        
        if matches:
            # Clean the extracted HTML (remove tags, normalize spaces)
            clean_text = re.sub(r'<[^>]+>', ' ', matches[0])
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            if len(clean_text) > 50:
                return clean_text
        
        # Attempt 2: Look for JSON-LD structured data (often contains descriptions)
        json_ld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
        json_matches = re.findall(json_ld_pattern, html_content, re.DOTALL)
        
        for json_str in json_matches:
            try:
                data = json.loads(json_str)
                # Recursively search for description fields
                if isinstance(data, dict):
                    if 'description' in data:
                        return data['description']
                    for key, value in data.items():
                        if isinstance(value, dict) and 'description' in value:
                            return value['description']
            except:
                continue
        
        return "ERROR: Job description block not found in static HTML"
        
    except subprocess.TimeoutExpired:
        return "ERROR: Request timed out"
    except Exception as e:
        return f"ERROR: {str(e)}"

for i in len(df):
    data["Job_Description"][i] = get_job_description_with_curl(df["URL"][i])
 
