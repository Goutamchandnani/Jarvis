# src/agents/job_link_scraper.py

import json
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os
import random

class JobLinkScraper:
    def __init__(self):
        self.priority_roles = [
            "AI Intern",
            "AI Research Intern"
        ]
        self.secondary_roles = []
        self.job_links = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_all_platforms(self):
        """Main orchestrator - scrapes ALL sources for all roles"""
        print("🔍 Starting COMPREHENSIVE job link scraping...")
        
        all_jobs = []
        
        # 1. LinkedIn (Priority - Last 24h)
        print("\n=== 1️⃣ LinkedIn Jobs (Last 24h) ===")
        for role in self.priority_roles:
            jobs = self.search_linkedin_advanced(role, hours_old=24)
            all_jobs.extend(jobs)
            time.sleep(random.uniform(2, 5))

        # 2. Startup Boards
        # print("\n=== 2️⃣ Startup Job Boards ===")
        # for role in self.priority_roles:
        #     all_jobs.extend(self.search_startups(role))
        #     time.sleep(2)
            
        # 3. Company Career Pages & ATS
        # print("\n=== 3️⃣ Company Career Pages & ATS ===")
        # Search companies once generally or per role? 
        # Better to search once to avoid spamming the same sites
        # all_jobs.extend(self.search_company_careers())
        
        # ATS search is per keyword usually, or just dumping all jobs
        # all_jobs.extend(self.search_ats_boards())
        
        # 4. Graduate Schemes
        # print("\n=== 4️⃣ Graduate Schemes ===")
        # all_jobs.extend(self.search_graduate_schemes())
        
        # 5. Tech Boards
        # print("\n=== 5️⃣ Tech-Specific Boards ===")
        # for role in self.priority_roles:
        #     all_jobs.extend(self.search_tech_boards(role))
        #     time.sleep(1)
        
        # Remove duplicates
        unique_jobs = self.remove_duplicates(all_jobs)
        
        # Filter relevant jobs
        relevant_jobs = self.filter_jobs(unique_jobs)
        
        self.print_summary(relevant_jobs)
        
        return relevant_jobs

    def search_startups(self, role):
        """Search Startup Job Boards"""
        jobs = []
        print(f"  🔍 Searching Startups for: {role}")
        
        # Y Combinator
        try:
            url = "https://www.ycombinator.com/jobs"
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'html.parser')
                # YC structure changes often, looking for generic match
                links = soup.find_all('a', href=True)
                for link in links:
                    if '/companies/' in link['href'] and any(w in link.text.lower() for w in role.lower().split()):
                        jobs.append({
                            'title': link.text.strip(),
                            'company': 'YC Startup', 
                            'url': f"https://www.ycombinator.com{link['href']}",
                            'source': 'YCombinator',
                            'scraped_at': datetime.now().isoformat()
                        })
        except Exception as e:
            print(f"    ⚠️ YC error: {e}")

        # Wellfound (AngelList) - tricky to scrape directly due to auth/JS, 
        # but we can try the basic role page if public
        try:
            q = role.replace(' ', '-').lower()
            url = f"https://wellfound.com/role/r/{q}/l/United-Kingdom"
            # Note: Wellfound often blocks simple requests or requires login. 
            # Skipping strictly to avoid blocking the whole run if it hangs.
            pass 
        except: 
            pass
            
        return jobs

    def search_company_careers(self):
        """Search target company career pages directly"""
        jobs = []
        companies = {
            'DeepMind': 'https://www.deepmind.com/careers',
            'Graphcore': 'https://www.graphcore.ai/jobs',
            'Faculty AI': 'https://faculty.ai/careers/',
            'BenevolentAI': 'https://www.benevolent.com/careers',
            'Revolut': 'https://www.revolut.com/careers/',
            'Monzo': 'https://monzo.com/careers/',
            'Deliveroo': 'https://careers.deliveroo.co.uk/'
        }
        
        print(f"  🔍 Checking {len(companies)} target companies...")
        
        for company, url in companies.items():
            try:
                resp = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(resp.content, 'html.parser')
                
                # Generic finder for keywords in links
                links = soup.find_all('a', href=True)
                for link in links:
                    txt = link.text.lower()
                    if any(k in txt for k in ['graduate', 'intern', 'ai', 'machine learning', 'data']):
                        full_url = link['href']
                        if not full_url.startswith('http'):
                            # Basic urljoin logic
                            from urllib.parse import urljoin
                            full_url = urljoin(url, full_url)
                            
                        jobs.append({
                            'title': link.text.strip(),
                            'company': company,
                            'url': full_url,
                            'source': 'CompanyDirect',
                            'scraped_at': datetime.now().isoformat()
                        })
            except:
                continue
                
        return jobs

    def search_ats_boards(self):
        """Search Greenhouse/Lever API endpoints"""
        jobs = []
        # Greenhouse
        gh_companies = ['airbnb', 'stripe', 'notion', 'figma']
        for co in gh_companies:
            try:
                url = f"https://boards-api.greenhouse.io/v1/boards/{co}/jobs"
                data = requests.get(url, timeout=5).json()
                for j in data.get('jobs', []):
                    if any(k in j['title'].lower() for k in ['ai', 'data', 'graduate', 'intern']):
                        loc = j.get('location', {}).get('name', '').lower()
                        if 'uk' in loc or 'london' in loc or 'remote' in loc:
                            jobs.append({
                                'title': j['title'],
                                'company': co.title(),
                                'url': j['absolute_url'],
                                'source': 'Greenhouse',
                                'scraped_at': datetime.now().isoformat()
                            })
            except: continue
            
        # Lever
        lev_companies = ['spotify', 'netflix']
        for co in lev_companies:
            try:
                url = f"https://api.lever.co/v0/postings/{co}"
                data = requests.get(url, timeout=5).json()
                for j in data:
                    if any(k in j['text'].lower() for k in ['ai', 'data', 'graduate', 'intern']):
                        loc = j.get('categories', {}).get('location', '').lower()
                        if 'uk' in loc or 'london' in loc or 'remote' in loc:
                            jobs.append({
                                'title': j['text'],
                                'company': co.title(),
                                'url': j['hostedUrl'],
                                'source': 'Lever',
                                'scraped_at': datetime.now().isoformat()
                            })
            except: continue
            
        return jobs

    def search_graduate_schemes(self):
        """Search graduate scheme aggregators"""
        jobs = []
        urls = [
            'https://www.prospects.ac.uk/jobs', 
            'https://targetjobs.co.uk/job-search'
        ]
        # These sites are complex to scrape with just requests/bs4 due to dynamic content, 
        # stick to simple parsing if possible or skip to avoid errors.
        return jobs # Placeholder for now to avoid breaking run with bad selectors

    def search_tech_boards(self, role):
        """Search tech boards like RemoteOK etc"""
        jobs = []
        # RemoteOK API
        try:
            q = role.replace(' ', '-').lower()
            url = "https://remoteok.com/api"
            # RemoteOK dumps all jobs, client side filtering needed usually
            # Getting explicit JSON is better
            pass
        except: pass
        return jobs

    def print_summary(self, jobs):
        from collections import Counter
        sources = Counter([j['source'] for j in jobs])
        print("\n📊 BREAKDOWN BY SOURCE:")
        for source, count in sources.most_common():
            print(f"   {source}: {count}")
    
    def filter_jobs(self, jobs):
        """
        Filter jobs to ensure they match the user's STRICT target roles:
        - AI Intern
        - AI Trainee
        - AI Research Intern
        """
        import re
        print("\n🧹 Filtering jobs (STRICT REGEX MODE: AI + Intern/Trainee)...")
        filtered = []
        
        # 1. Target Phrases (Phrases that if found, automatically qualify the job)
        valid_phrases = [
            r'\bai intern\b', 
            r'\bai trainee\b', 
            r'\bai research intern\b',
            r'\bartificial intelligence intern\b',
            r'\bmachine learning intern\b',
            r'\bml intern\b',
            r'\bai placement\b',
            r'\bartificial intelligence placement\b'
        ]
        
        # 2. Component Logic (Title must have [AI term] AND [Intern term])
        # Note: 'ai' must be a whole word to avoid matching 'trAIning', 'remAIl', etc.
        ai_terms = [
            r'\bai\b', 
            r'\bartificial intelligence\b', 
            r'\bmachine learning\b', 
            r'\bml\b', 
            r'\bdeep learning\b', 
            r'\bcomputer vision\b', 
            r'\bnlp\b', 
            r'\bllm\b', 
            r'\bgenerative ai\b'
        ]
        
        intern_terms = [
            r'\bintern\b', 
            r'\binternship\b', 
            r'\btrainee\b', 
            r'\bplacement\b', 
            r'\bstudent\b',
            r'\bundergraduate\b'
        ]
        
        # Blacklist 
        blacklist = ['senior', 'manager', 'lead', 'director', 'marketing', 'sales', 'hr', 'recruiter', 'agent', 'attorney', 'counsel']

        for job in jobs:
            title = job['title'].lower()
            
            # 1. exclusions
            if any(bad in title for bad in blacklist):
                 print(f"  🗑️  Dropped (Blacklist): {job['title']}")
                 continue
                 
            # 2. Check strict criteria using Regex
            is_valid = False
            
            # Check phrases
            for pattern in valid_phrases:
                if re.search(pattern, title):
                    is_valid = True
                    break
            
            # If phrase didn't match, check component combination
            if not is_valid:
                has_ai = any(re.search(pattern, title) for pattern in ai_terms)
                has_intern = any(re.search(pattern, title) for pattern in intern_terms)
                
                if has_ai and has_intern:
                    is_valid = True
                
            if is_valid:
                filtered.append(job)
            else:
                # Debug print for "Trainee Patent Attorney" or "Internship Trainee"
                if "trainee" in title or "intern" in title:
                     print(f"  🗑️  Dropped (Strict Mismatched): {job['title']}")
                else:
                     pass # Don't spam console for obviously wrong ones
                
        return filtered
    
    def search_linkedin_advanced(self, role, hours_old=24):
        """
        Advanced LinkedIn search with multiple filters
        Parameters:
        - hours_old: 24, 168 (week), 720 (month)
        """
        import re
        jobs = []
        
        # Time filters mapping
        time_filters = {
            24: 'r86400',      # Past 24 hours
            168: 'r604800',    # Past week
            720: 'r2592000'    # Past month
        }
        
        time_filter = time_filters.get(hours_old, 'r86400')
        
        # EXACT PHRASE SEARCH: Add quotes around the role
        # e.g. AI Intern -> "AI Intern"
        search_query = f'"{role}"'.replace(' ', '%20')
        
        base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        
        # UK Geo ID: 101165590
        params = {
            'keywords': search_query,
            'location': 'United Kingdom',
            'geoId': '101165590',
            'f_E': '1,2',           # Experience: Entry Level (1), Internship (2)
            'f_TPR': time_filter,   # Time Posted Range
            'f_JT': 'F,I',          # Job Type: Full-time (F), Internship (I)
            'sortBy': 'DD',         # Sort by Date (Newest first)
            'start': 0
        }
        
        print(f"\nExample Query: \"{role}\" (Last {hours_old}h)")
        
        # Scrape up to 4 pages (100 jobs) to keep it safe but effective
        for page in range(0, 4):
            params['start'] = page * 25
            
            try:
                response = requests.get(base_url, params=params, headers=self.headers, timeout=10)
                
                if response.status_code != 200:
                    print(f"  ⚠️ Status {response.status_code} on page {page}")
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('li')
                
                if not job_cards:
                    # If no jobs found on this page, stop
                    break
                
                for card in job_cards:
                    try:
                        base_card = card.find('div', class_='base-card')
                        if not base_card:
                            continue
                        
                        title_elem = base_card.find('h3', class_='base-search-card__title')
                        company_elem = base_card.find('h4', class_='base-search-card__subtitle')
                        location_elem = base_card.find('span', class_='job-search-card__location')
                        link_elem = base_card.find('a', class_='base-card__full-link')
                        date_elem = base_card.find('time', class_='job-search-card__listdate')
                        
                        if title_elem and company_elem and link_elem:
                            job_url = link_elem.get('href', '')
                            clean_url = job_url.split('?')[0] if '?' in job_url else job_url
                            
                            # --- INLINE FILTERING ---
                            # Only accept if title STRICTLY matches requirements
                            title_text = title_elem.text.strip()
                            title_lower = title_text.lower()
                            
                            # 1. Regex Validation
                            valid_phrases = [
                                r'\bai intern\b', r'\bai trainee\b', r'\bai research intern\b',
                                r'\bartificial intelligence intern\b', r'\bmachine learning intern\b', 
                                r'\bml intern\b'
                            ]
                            
                            is_valid = False
                            for pattern in valid_phrases:
                                if re.search(pattern, title_lower):
                                    is_valid = True
                                    break
                            
                            # If not exact phrase, check very strict component match
                            # Must have (AI words) AND (Intern words)
                            if not is_valid:
                                ai_terms = [r'\bai\b', r'\bartificial intelligence\b', r'\bml\b']
                                intern_terms = [r'\bintern\b', r'\binternship\b', r'\btrainee\b']
                                
                                has_ai = any(re.search(p, title_lower) for p in ai_terms)
                                has_intern = any(re.search(p, title_lower) for p in intern_terms)
                                if has_ai and has_intern:
                                    is_valid = True
                            
                            if not is_valid:
                                # Silently skip irrelevant ones to avoid user confusion
                                continue
                                
                            job = {
                                'title': title_text,
                                'company': company_elem.text.strip(),
                                'location': location_elem.text.strip() if location_elem else 'Remote/UK',
                                'url': clean_url,
                                'date_posted': date_elem.get('datetime') if date_elem else f'Last {hours_old}h',
                                'source': 'LinkedIn',
                                'search_role': role,
                                'scraped_at': datetime.now().isoformat()
                            }
                            
                            jobs.append(job)
                            print(f"  ✓ {job['title']} at {job['company']}")
                    
                    except Exception as e:
                        continue
                
                # Polite rate limiting between pages
                time.sleep(1.5)
            
            except Exception as e:
                print(f"  ❌ Page {page} error: {e}")
                break
        
        print(f"  ✅ Found {len(jobs)} jobs for \"{role}\"")
        return jobs

    def remove_duplicates(self, jobs):
        """Remove duplicate jobs based on title + company"""
        seen = set()
        unique = []
        
        for job in jobs:
            key = f"{job['title'].lower()}|{job['company'].lower()}"
            if key not in seen:
                seen.add(key)
                unique.append(job)
        
        return unique
    
    def save_links(self, jobs, filename='data/jobs/scraped_links.json'):
        """Save job links to file"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved {len(jobs)} job links to {filename}")
