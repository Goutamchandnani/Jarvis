# main.py

import json
from src.agents.job_link_scraper import JobLinkScraper
from src.agents.cv_generator import CVGenerator
from src.utils.pdf_generator import PDFGenerator
from datetime import datetime
import os
import sys

def main():
    """Main orchestrator for the two-part agent system"""
    
    print("="*60)
    print("🤖 AGENTIC AI RESUME CREATOR")
    print("="*60)
    
    # Load configuration
    api_key_path = 'config/api_keys.json'
    if not os.path.exists(api_key_path):
        print(f"❌ Error: {api_key_path} not found. Please create it with your Gemini API key.")
        return

    with open(api_key_path, 'r') as f:
        api_keys = json.load(f)
        
    if not api_keys.get('gemini_api_key'):
        print("❌ Error: gemini_api_key not found in config/api_keys.json")
        return
    
    # ========================================
    # PART 1: SCRAPE JOB LINKS
    # ========================================
    print("\n" + "="*60)
    print("PART 1: JOB LINK SCRAPING")
    print("="*60)
    
    scraper = JobLinkScraper()
    job_links = scraper.scrape_all_platforms()
    
    # Save scraped links
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    links_file = f'data/jobs/scraped_links_{timestamp}.json'
    scraper.save_links(job_links, links_file)
    
    # Generate summary report
    print("\n📊 SCRAPING SUMMARY:")
    print(f"   Total Jobs Found: {len(job_links)}")
    print(f"   Priority Jobs: {len([j for j in job_links if j.get('priority')])}")
    print(f"   Secondary Jobs: {len([j for j in job_links if not j.get('priority')])}")
    print(f"\n   By Platform:")
    for source in ['LinkedIn', 'Indeed', 'Glassdoor']:
        count = len([j for j in job_links if j.get('source') == source])
        print(f"   - {source}: {count}")
    
    if not job_links:
        print("⚠️ No jobs found. Exiting.")
        return

    # ========================================
    # PART 2: GENERATE TAILORED CVS
    # PART 2: CV GENERATION
    # ========================================
    print("\n" + "="*60)
    print("PART 2: CV GENERATION")
    print("="*60)
    
    cv_generator = CVGenerator(
        api_key=api_keys['gemini_api_key'],
        current_cv_path='data/profile/my_current_cv.json',
        project_pool_path='data/profile/project_pool.json'
    )
    
    # For MVP, maybe limit to fewer CVs to save tokens/time if needed, but keeping 100 as per request
    tailored_cvs = cv_generator.generate_all_cvs(job_links, max_cvs=5) 
    
    # Save all results
    results_file = f'data/results/results_{timestamp}.json'
    os.makedirs('data/results', exist_ok=True)
    
    results = {
        'timestamp': timestamp,
        'jobs_scraped': len(job_links),
        'cvs_generated': len(tailored_cvs),
        'job_links': job_links,
        'tailored_cvs': tailored_cvs
    }
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # ========================================
    # GENERATE PDF REPORTS
    # ========================================
    print("\n" + "="*60)
    print("GENERATING PDF CVS")
    print("="*60)
    
    pdf_gen = PDFGenerator()
    
    for i, cv_data in enumerate(tailored_cvs, 1):
        try:
            pdf_gen.generate_resume_pdf(
                cv_data['tailored_cv']['tailored_cv'],
                cv_data['job']['title'],
                cv_data['job']['company']
            )
        except Exception as e:
            print(f"❌ Error generating PDF for {cv_data['job']['company']}: {e}")
    
    # ========================================
    # FINAL SUMMARY
    # ========================================
    print("\n" + "="*60)
    print("✅ COMPLETE!")
    print("="*60)
    print(f"\n📊 FINAL SUMMARY:")
    print(f"   Jobs Scraped: {len(job_links)}")
    print(f"   CVs Generated: {len(tailored_cvs)}")
    if tailored_cvs:
        avg_score = sum([cv['tailored_cv']['job_analysis']['match_score'] for cv in tailored_cvs]) / len(tailored_cvs)
        print(f"   Average Match Score: {avg_score:.1f}")
    
    print(f"\n📁 FILES SAVED:")
    print(f"   Job Links: {links_file}")
    print(f"   Results: {results_file}")
    print(f"   CV JSONs: data/resumes/tailored_json/")
    print(f"   CV PDFs: data/resumes/generated/")
    
    if tailored_cvs:
        print(f"\n🎯 TOP MATCHES:")
        top_matches = sorted(tailored_cvs, key=lambda x: x['tailored_cv']['job_analysis']['match_score'], reverse=True)[:5]
        for i, cv in enumerate(top_matches, 1):
            print(f"   {i}. {cv['tailored_cv']['job_analysis']['match_score']}% - {cv['job']['title']} at {cv['job']['company']}")
            print(f"      {cv['job']['url']}")

if __name__ == "__main__":
    main()
