# Agentic AI Resume Creator 🚀

An autonomous AI agent that finds strictly relevant AI/ML internship opportunities and generates perfectly tailored CVs to maximize your interview chances.

## 🌟 Key Features

*   **Smart Job Scraping**: 
    *   Scrapes LinkedIn for jobs posted in the **last 24 hours**.
    *   **Strict Filtering**: Uses Regex-based filtering to ensure only "AI/ML" + "Intern/Trainee" roles are selected. No generic software jobs or senior roles.
    *   Multi-source architecture (Ready for Startups, ATS, etc.).
*   **Dynamic Project Selection**:
    *   Maintains a pool of your detailed project descriptions.
    *   Analyzing the job description, the AI **dynamically picks the best 2-3 projects** that demonstrate the required skills.
    *   Replaces generic specific bullets with targeted project highlights.
*   **Tailored Content Generation**:
    *   Uses **Google Gemini Pro/Flash** to rewrite your Professional Summary and Experience bullets.
    *   Optimizes keywords for ATS (Applicant Tracking Systems).
*   **Privacy First**:
    *   Your API keys and personal data (`data/`) are strictly ignored by git.

## 🛠️ Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Goutamchandnani/Jarvis.git
    cd Jarvis
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Keys**
    *   Open `config/api_keys.json`.
    *   Add your Gemini API Key:
    ```json
    {
        "gemini_api_key": "YOUR_KEY_HERE"
    }
    ```

4.  **Prepare Your Profile**
    *   **Generic CV**: Update `data/profile/my_current_cv.json` with your base details.
    *   **Project Pool**: Add your best projects to `data/profile/project_pool.json`.

## ⚡ Usage

Run the main agent:

```bash
python main.py
```

**The Agent will:**
1.  🔍 Scrape LinkedIn for fresh AI Intern jobs.
2.  🧹 Filter out irrelevant or mismatched titles.
3.  🧠 Analyze each valid job description.
4.  ✍️ Generate a tailored CV JSON and PDF (in `data/resumes/`).

## 📂 Project Structure

```
.
├── src/
│   ├── agents/
│   │   ├── job_link_scraper.py   # Scrapes & filters jobs
│   │   └── cv_generator.py       # Interacts with Gemini API
│   └── utils/
│       └── pdf_generator.py      # Converts JSON CV to PDF
├── data/                         # (Ignored by Git)
│   ├── profile/                  # Your inputs (CV + Projects)
│   └── resumes/                  # Generated outputs
├── config/
│   └── api_keys.json             # API Configuration
└── main.py                       # Entry point
```


