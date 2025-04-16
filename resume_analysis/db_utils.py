import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from resume_analysis.models import Base

DB_PATH = "sqlite:///db/resume_analysis.db"
engine = create_engine(DB_PATH, echo=False)
SessionLocal = sessionmaker(bind=engine)

def create_all_tables():
    Base.metadata.create_all(engine)

def export_table_to_json(session, model, filename):
    rows = session.query(model).all()
    # Convert SQLAlchemy objects to dicts
    def row_to_dict(row):
        d = {c.name: getattr(row, c.name) for c in row.__table__.columns}
        # Convert datetime to isoformat
        for k, v in d.items():
            if hasattr(v, 'isoformat'):
                d[k] = v.isoformat()
        return d
    data = [row_to_dict(r) for r in rows]
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Exported {len(data)} rows to {filename}")
