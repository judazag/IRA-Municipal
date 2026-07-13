import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import db
from sqlalchemy import text

engine = db.get_engine()
with engine.connect() as conn:
    r = conn.execute(text('select count(*) from municipio_features'))
    print('count ->', r.scalar())
