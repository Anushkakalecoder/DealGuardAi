from app.core.database import Base, SessionLocal, engine
from app.main import seed_database
from app.services.evaluation_service import run_evaluation

seed_database()
with SessionLocal() as db:
    result = run_evaluation(db, scenarios=1000, seed=42)
    import json
    print(json.dumps(result, indent=2))
