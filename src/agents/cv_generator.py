# src/agents/cv_generator.py

import json
import google.generativeai as genai
from datetime import datetime
import time
import os
import requests
from bs4 import BeautifulSoup

class CVGenerator:
    def __init__(self, api_key, current_cv_path, project_pool_path=None):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.current_cv = self.load_json(current_cv_path)
        self.project_pool = self.load_json(project_pool_path) if project_pool_path else []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def load_json(self, path):
        """Load JSON file content"""
        if not path or not os.path.exists(path):
            print(f"⚠️ Warning: File not found at {path}")
            return [] if 'pool' in str(path) else {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def fetch_job_description(self, job_url, source):
        """Fetch full job description from URL using requests"""
        try:
            # Simple GET request
            response = requests.get(job_url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                print(f"  ⚠️ Status {response.status_code} fetching JD")
                return ''
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Platform-specific selectors
            desc_elem = None
            if 'linkedin.com' in job_url:
                desc_elem = soup.find('div', class_='description__text') or \
                           soup.find('div', class_='show-more-less-html__markup') or \
                           soup.find('section', class_='description')
            elif 'indeed.com' in job_url or 'indeed.co.uk' in job_url:
                desc_elem = soup.find('div', id='jobDescriptionText')
            elif 'glassdoor' in job_url:
                desc_elem = soup.find('div', class_='jobDescriptionContent')
            else:
                desc_elem = soup.find('div', class_='description') or soup.find('div', id='job-description')
            
            description = desc_elem.text.strip() if desc_elem else ''
            
            if not description:
                # Fallback: try to find any large text block
                paragraphs = soup.find_all('p')
                long_paragraphs = [p.text.strip() for p in paragraphs if len(p.text.strip()) > 50]
                if long_paragraphs:
                    description = ' '.join(long_paragraphs)
            
            return description
            
        except Exception as e:
            print(f"  ❌ Error fetching JD: {e}")
            return ''
    
    def generate_tailored_cv(self, job):
        """Generate tailored CV using Gemini API"""
        
        print(f"\n🎯 Tailoring CV for: {job['title']} at {job['company']}")
        
        # Fetch full job description
        print("  📄 Fetching job description...")
        job_description = self.fetch_job_description(job['url'], job['source'])
        
        if not job_description:
            print("  ⚠️  No job description found (or blocked), using title only...")
            job_description = f"Job Title: {job['title']} at {job['company']}. Location: {job['location']}. (Full description could not be fetched)."
        else:
            print(f"  ✓ Got JD ({len(job_description)} chars)")
        
        # Create prompt with current CV and job details
        prompt = f"""You are an expert ATS resume optimizer for graduate AI/ML positions.

MY GENERIC CV CONTENT:
{json.dumps(self.current_cv, indent=2)}

AVAILABLE PROJECT POOL (Select the best 2-3 for this job):
{json.dumps(self.project_pool, indent=2)}

JOB I'M APPLYING TO:
Title: {job['title']}
Company: {job['company']}
Location: {job['location']}
URL: {job['url']}

FULL JOB DESCRIPTION:
{job_description}

YOUR TASK:
Create a tailored version of my CV specifically for this job.

STEP 1: PROJECT SELECTION
- Analyze the Job Description to identify the most relevant technical skills and domain requirements.
- From the "AVAILABLE PROJECT POOL", select the 2 (or max 3) projects that BEST demonstrate these skills.
- DO NOT use projects that are irrelevant if better options exist in the pool.
- You may also use the experiences from the Generic CV if they are highly relevant.

STEP 2: TAILORING
- **Summary**: Customize the professional summary to highlight the specific tech stack and soft skills asked for in the JD.
- **Skills**: Reorder my skills to put the ones mentioned in the JD at the top.
- **Projects**: Write the project descriptions for the SELECTED projects. 
    - Focus on the "Key Contributions" that match the job.
    - Use strong action verbs.
    - Highlight the specific technologies used (e.g., if JD asks for Next.js, emphasize Next.js usage in DocuCare).
- **Experience**: Tailor the experience bullets similarly.

OUTPUT FORMAT:
Return ONLY valid JSON.

{{
  "job_analysis": {{
    "match_score": 85,
    "key_requirements": ["req1", "req2"],
    "selected_projects_reasoning": "Selected DocuCare because..."
  }},
  "tailored_cv": {{
    "personal_info": {{ ... (same as generic) ... }},
    "professional_summary": "...",
    "skills": {{ ... }},
    "experience": [ ... ],
    "projects": [
      {{
        "title": "Title",
        "date": "Date",
        "technologies": ["tech1", "tech2"],
        "description": "One line summary",
        "achievements": ["bullet 1", "bullet 2", "bullet 3"]
      }}
    ],
    "education": {{ ... }},
    "certifications": [ ... ]
  }}
}}"""

        try:
            print("  🤖 Calling Gemini API...")
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            
            response_text = response.text.replace('```json', '').replace('```', '').strip()
            
            tailored_cv_data = json.loads(response_text)
            
            print(f"  ✅ CV tailored! Match score: {tailored_cv_data['job_analysis']['match_score']}")
            
            return {
                'job': job,
                'job_description': job_description,
                'tailored_cv': tailored_cv_data,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"  ❌ Error generating CV: {e}")
            return None
    
    def generate_all_cvs(self, job_links, max_cvs=100):
        """Generate tailored CVs for all job links"""
        
        print(f"\n🎨 Starting CV generation for {len(job_links)} jobs...")
        
        results = []
        
        # Prioritize high-priority jobs
        priority_jobs = [j for j in job_links if j.get('priority', False)]
        other_jobs = [j for j in job_links if not j.get('priority', False)]
        
        all_jobs = priority_jobs + other_jobs
        all_jobs = all_jobs[:max_cvs]  # Limit total
        
        for i, job in enumerate(all_jobs, 1):
            print(f"\n[{i}/{len(all_jobs)}] Processing: {job['title']} at {job['company']}")
            
            cv_data = self.generate_tailored_cv(job)
            
            if cv_data:
                results.append(cv_data)
                
                # Save individual CV
                self.save_cv(cv_data, i)
            
            # Rate limiting (avoid hitting API limits)
            if i < len(all_jobs):
                time.sleep(2)
        
        print(f"\n✅ Generated {len(results)} tailored CVs!")
        return results
    
    def save_cv(self, cv_data, index):
        """Save tailored CV as JSON"""
        
        # Save JSON
        json_dir = 'data/resumes/tailored_json'
        os.makedirs(json_dir, exist_ok=True)
        
        safe_company = "".join(c for c in cv_data['job']['company'] if c.isalnum() or c in (' ', '-'))[:30]
        safe_title = "".join(c for c in cv_data['job']['title'] if c.isalnum() or c in (' ', '-'))[:40]
        
        json_filename = f"{index:03d}_{safe_company}_{safe_title}.json"
        json_path = os.path.join(json_dir, json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(cv_data, f, indent=2, ensure_ascii=False)
        
        print(f"  💾 Saved: {json_filename}")
