# Skill Gap Analysis & Taxonomy Backend

A robust, scalable backend for skill gap analysis, designed for integration with a frontend dashboard. This solution parses resumes and job descriptions (PDF), extracts and analyzes skills using NLP, and stores structured results in a normalized database and JSON files. Built for easy extension to Postgres and production APIs.

---

## 🚀 Features
- **PDF → Markdown/Text**: Converts resumes and job descriptions from PDF to markdown and plain text.
- **Skill Extraction**: Uses NLP/LLM to extract skills, proficiency, and match from unstructured text.
- **Dynamic Skill Taxonomy**: Supports ESCO/O*NET/Custom skills, with categories, related skills, and source tracking.
- **Skill Gap Reports**: Identifies matched, missing, and transferable skills between user and job.
- **Normalized Database**: Stores all entities in SQLite (easy to migrate to Postgres).
- **JSON Exports**: All tables exportable as JSON for dashboard/API consumption.
- **Clean, Modular Codebase**: Follows best practices for Python project structure and extensibility.
- **Makefile Automation**: One-command setup, test, lint, and clean.

---

## 📁 Project Structure

```
resume-analysis/
│
├── data/                # JSON exports, taxonomy, and sample data
├── db/                  # Database artifacts (SQLite DB)
├── resume_analysis/     # Main Python package (all core logic)
│   ├── __init__.py
│   ├── models.py        # ORM models (UserProfile, JobDescription, etc)
│   ├── db_utils.py      # DB setup, session, export helpers
│   ├── skill_analysis.py# NLP extraction, gap analysis
│   ├── taxonomy.py      # Taxonomy management
├── scripts/             # CLI/demo scripts
│   ├── demo_seed.py     # Populate DB with sample data & export JSON
│   └── main.py          # Main pipeline entry point
├── requirements.txt     # Python dependencies
├── Makefile             # Automation for setup, test, lint, clean
├── .env                 # (Optional) Environment variables
└── README.md
```

---

## 🧠 Database Schema Overview

### Core Entities
- **UserProfile**: Candidate info, resume text, LinkedIn, etc.
- **JobDescription**: Job post, required skills, company info.
- **SkillTaxonomy**: Reference skills (ESCO/O*NET/Custom), category, related skills.
- **ExtractedSkill**: Skills found in resume/job, linked to taxonomy, with confidence/proficiency.
- **SkillGapReport**: Comparison of user vs job (overall fit, summary).
- **SkillGapDetail**: Line-level skill match/gap details for a report.

### Relationships
```
UserProfile           JobDescription
     |                       |
     |                       |
     +---- ExtractedSkill ---+
                |
         SkillTaxonomy
                |
        SkillGapReport
                |
         SkillGapDetail
```

---

## 🛠️ Setup & Usage

### 1. Clone & Install
```bash
git clone <repo-url>
cd resume-analysis
make setup
```

### 2. Run Demo/Test (populate DB and export JSON)
```bash
make test
```
- Outputs: `data/*.json` (for dashboard/frontend), `db/resume_analysis.db`

### 3. Lint & Format
```bash
make lint   # Check code style
make format # Auto-format code
```

### 4. Clean Build/Data Artifacts
```bash
make clean
```

---

## 📦 Integration Guide (for Frontend)
- **JSON Data**: All tables exported as JSON in `data/` (see `user_profiles.json`, `job_descriptions.json`, etc).
- **Database**: Full normalized SQLite DB in `db/resume_analysis.db` (can be migrated to Postgres).
- **Schema**: See models in `resume_analysis/models.py` and above overview.
- **Sample Data**: Run `make test` to generate realistic sample data for UI development.
- **Resume/Job Uploads**: Place PDFs in the project root or as configured.

---

## 📝 Customization & Scaling
- **Switch to Postgres**: Change the SQLAlchemy DB URL in `resume_analysis/db_utils.py`.
- **Add Skills/Taxonomies**: Update `data/skills_taxonomy.json` or extend taxonomy loader.
- **Integrate API**: Extend the package with FastAPI/Flask for production endpoints.
- **Dashboard**: Use JSON or DB as your data source for charts, tables, and analytics.

---

## 👨‍💻 For Developers
- All code is modular and ready for extension.
- Add new scripts to `scripts/` and new modules to `resume_analysis/`.
- Use the Makefile for all routine tasks.

---

## 📬 Questions?
Contact the backend developer or open an issue in the repo for support or feature requests.

---

**Happy building!**
