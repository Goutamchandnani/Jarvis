# src/utils/pdf_generator.py

from fpdf import FPDF
import json

class PDFGenerator:
    def __init__(self):
        pass
        
    class PDF(FPDF):
        def header(self):
            # No header for now
            pass
            
        def footer(self):
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def generate_resume_pdf(self, cv_data, job_title, company_name):
        """Generate a PDF resume from the tailored CV JSON data"""
        
        pdf = self.PDF()
        pdf.add_page()
        
        # --- Header ---
        # Assuming personal info might be in the root or headers, but the structure from user prompt puts it in root.
        # But wait, the `cv_generator.py` generates `tailored_cv` object which contains:
        # professional_summary, skills, projects, education, certifications.
        # It DOES NOT usually return personal_info in the tailored part (based on the prompt in cv_generator.py).
        # We might need to merge personal info from the original CV or assume it's passed in.
        # For this MVP, I'll assume we can pass personal info or it's missing from the generated part.
        # Let's check `cv_generator.py` prompt... it asks to return:
        # "tailored_cv": { "professional_summary", "skills", "projects", "education", "certifications" }
        # So personal info is missing from the *tailored* output.
        # I should probably just put a placeholder or basic header since I don't easily have the personal info here 
        # unless I pass it through.
        
        # However, for MVP, let's just create a nice clean layout.
        
        pdf.set_font('Helvetica', 'B', 24)
        pdf.cell(0, 10, job_title + " Application", new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.set_font('Helvetica', '', 12)
        pdf.cell(0, 10, f"Targeting: {company_name}", new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.ln(10)
        
        # --- Professional Summary ---
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, 'Professional Summary', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('Helvetica', '', 11)
        pdf.multi_cell(0, 6, cv_data.get('professional_summary', ''))
        pdf.ln(5)
        
        # --- Skills ---
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, 'Technical Skills', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('Helvetica', '', 11)
        skills = cv_data.get('skills', {})
        for category, skill_list in skills.items():
            if skill_list:
                pdf.set_font('Helvetica', 'B', 11)
                pdf.cell(40, 6, category + ":", new_x="RIGHT", new_y="TOP")
                pdf.set_font('Helvetica', '', 11)
                pdf.multi_cell(0, 6, ", ".join(skill_list))
        pdf.ln(5)
        
        # --- Experience/Projects ---
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, 'Relevant Experience & Projects', new_x="LMARGIN", new_y="NEXT")
        
        projects = cv_data.get('projects', [])
        for proj in projects:
            pdf.set_font('Helvetica', 'B', 12)
            title = proj.get('title', '')
            context = proj.get('context', '') or proj.get('company_or_context', '')
            pdf.cell(0, 8, f"{title} - {context}", new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_font('Helvetica', 'I', 10)
            tech = ", ".join(proj.get('technologies', []))
            pdf.cell(0, 6, f"Stack: {tech}", new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_font('Helvetica', '', 11)
            pdf.multi_cell(0, 6, proj.get('description', ''))
            
            # Achievements
            pdf.set_font('Helvetica', '', 10)
            for bullet in proj.get('achievements', []):
                pdf.cell(5) # indent
                pdf.multi_cell(0, 5, f"- {bullet}")
            pdf.ln(3)
            
        # --- Education ---
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, 'Education', new_x="LMARGIN", new_y="NEXT")
        edu = cv_data.get('education', {})
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 8, edu.get('university', ''), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('Helvetica', '', 11)
        pdf.cell(0, 6, f"{edu.get('degree', '')} ({edu.get('graduation', '')})", new_x="LMARGIN", new_y="NEXT")
        if edu.get('relevant_coursework'):
             pdf.multi_cell(0, 6, "Coursework: " + ", ".join(edu['relevant_coursework']))
        pdf.ln(5)
        
        # --- Certifications ---
        certifications = cv_data.get('certifications', [])
        if certifications:
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 10, 'Certifications', new_x="LMARGIN", new_y="NEXT")
            pdf.set_font('Helvetica', '', 11)
            for cert in certifications:
                pdf.multi_cell(0, 6, f"- {cert.get('name', '')} ({cert.get('issuer', '')})")

        # Save
        filename = f"data/resumes/generated/CV_{company_name}_{job_title}.pdf"
        # Sanitize filename
        safe_filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '-', '_', '.', '/')]).replace(' ', '_')
        import os
        os.makedirs(os.path.dirname(safe_filename), exist_ok=True)
        
        pdf.output(safe_filename)
        print(f"  📄 Generated PDF: {safe_filename}")

if __name__ == "__main__":
    # Test
    pass
