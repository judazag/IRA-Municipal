"""Script placeholder: cargar municipio_features.parquet a PostgreSQL/PostGIS.

Uso (ejemplo):
    python scripts/ingest_to_db.py --parquet data/03_primary/municipio_features.parquet --db-url postgresql://user:pass@host/db

Actualmente este script solo imprime resumen; puedes ampliarlo para usar SQLAlchemy/GeoAlchemy2 y cargar geometrías.
"""
import argparse
from pathlib import Path
import sys

import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import WKTElement
from shapely import wkt as shapely_wkt
from shapely.geometry import MultiPolygon, Polygon

try:
    # ensure project root is in path when running as script
    proj_root = Path(__file__).resolve().parents[1]
    if str(proj_root) not in sys.path:
        sys.path.insert(0, str(proj_root))
    from src.models import Base, MunicipioFeatures
except Exception:
    # fallback import if running from project root
    from models import Base, MunicipioFeatures


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--parquet", default="data/04_model_output/ira_municipal_final.parquet")
    p.add_argument("--db-url", default=None)
    p.add_argument("--batch", type=int, default=500)
    args = p.parse_args()

    path = Path(args.parquet)
    if not path.exists():
        print(f"Parquet not found: {path}")
        return
    df = pd.read_parquet(path)
    print(f"Loaded {len(df)} rows from {path}")
    print("Columns:", list(df.columns))

    if not args.db_url:
        print("No DB URL provided; exiting.")
        return

    engine = create_engine(args.db_url)
    Session = sessionmaker(bind=engine)

    # create tables if not exists
    Base.metadata.create_all(engine)

    session = Session()
    inserted = 0
    try:
        for idx, row in df.iterrows():
            div = str(row.get('divipola') or row.get('DIVIPOLA') or '')
            if not div:
                continue
            mf = MunicipioFeatures(divipola=div)
            # copy known columns if present
            if 'municipio' in row.index:
                mf.municipio = row.get('municipio')
            if 'ira_score' in row.index and not pd.isna(row.get('ira_score')):
                try:
                    mf.ira_score = float(row.get('ira_score'))
                except Exception:
                    mf.ira_score = None
            elif 'ira_riesgo' in row.index and not pd.isna(row.get('ira_riesgo')):
                try:
                    mf.ira_score = float(row.get('ira_riesgo'))
                except Exception:
                    mf.ira_score = None
            if 'ira_level' in row.index and not pd.isna(row.get('ira_level')):
                mf.ira_level = row.get('ira_level')
            elif 'nivel_ira' in row.index and not pd.isna(row.get('nivel_ira')):
                mf.ira_level = row.get('nivel_ira')

            # sample numeric fields
            if 'produccion_total_ton' in row.index:
                mf.produccion_total_ton = row.get('produccion_total_ton')
            if 'area_sembrada_total_ha' in row.index:
                mf.area_sembrada_total_ha = row.get('area_sembrada_total_ha')
            if 'n_cultivos' in row.index:
                mf.n_cultivos = row.get('n_cultivos')

            # geometry if present: accept WKT or shapely geometry
            geom_val = None
            if 'geom' in row.index and not pd.isna(row.get('geom')):
                geom_val = row.get('geom')
            elif 'geometry' in row.index and not pd.isna(row.get('geometry')):
                geom_val = row.get('geometry')

            if geom_val is not None:
                try:
                    # Accept raw WKT string or shapely geometry
                    if hasattr(geom_val, 'wkt'):
                        g = geom_val
                    else:
                        g = shapely_wkt.loads(str(geom_val))
                    # Ensure MultiPolygon type to match column
                    if isinstance(g, Polygon):
                        g = MultiPolygon([g])
                    mf.geom = WKTElement(g.wkt, srid=4326)
                except Exception:
                    # skip geometry if unable to convert
                    mf.geom = None

            session.merge(mf)
            inserted += 1
            if inserted % args.batch == 0:
                session.commit()
                print(f"Inserted {inserted} rows...")

        session.commit()
        print(f"Finished inserting {inserted} rows")
    except Exception as e:
        session.rollback()
        print("Error during insert:", e)
    finally:
        session.close()


if __name__ == "__main__":
    main()
