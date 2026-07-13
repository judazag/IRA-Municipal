from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import to_shape
from pydantic import BaseModel
from shapely import wkb, wkt
from shapely.geometry import mapping
from sqlalchemy.orm import Session

from collections import Counter
from src import db as src_db
try:
    from src.models import MunicipioFeatures
except Exception:
    MunicipioFeatures = None


class MunicipioSummary(BaseModel):
    divipola: str
    municipio: Optional[str] = None
    ira_score: Optional[float] = None
    ira_level: Optional[str] = None


app = FastAPI(title="IRA Municipal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _parquet_path() -> Path:
    # Expected location: data/03_primary/municipio_features.parquet
    return _project_root() / "data" / "03_primary" / "municipio_features.parquet"


def _normalize_geom(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, WKBElement):
        try:
            return mapping(to_shape(value))
        except Exception:
            return None
    if isinstance(value, bytes):
        try:
            return mapping(wkb.loads(value))
        except Exception:
            return None
    if isinstance(value, str):
        try:
            if value.startswith('SRID='):
                _, wkt_text = value.split(';', 1)
                return mapping(wkt.loads(wkt_text))
            return mapping(wkt.loads(value))
        except Exception:
            return None
    if hasattr(value, 'geom_type'):
        try:
            return mapping(value)
        except Exception:
            return None
    return None


def _normalize_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime,)):
        return value.isoformat()
    if isinstance(value, WKBElement):
        return _normalize_geom(value)
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except Exception:
            return value.hex()
    if isinstance(value, str):
        return value
    if hasattr(value, 'item'):
        try:
            return value.item()
        except Exception:
            pass
    return value


def _row_to_dict(row: pd.Series) -> Dict[str, Any]:
    d: Dict[str, Any] = {}
    for k, v in row.items():
        try:
            if pd.isna(v):
                d[k] = None
            else:
                d[k] = _normalize_value(v)
        except Exception:
            d[k] = v
    return d


@app.on_event("startup")
def load_data() -> None:
    # Prefer DB if available
    use_db = False
    try:
        use_db = src_db.test_connection()
    except Exception:
        use_db = False
    app.state.use_db = bool(use_db) and MunicipioFeatures is not None
    if not app.state.use_db:
        path = _parquet_path()
        if not path.exists():
            app.state.df = None
            return
        # Read parquet into a pandas DataFrame
        df = pd.read_parquet(path)
        # Ensure divipola is string
        if "divipola" in df.columns:
            df["divipola"] = df["divipola"].astype(str)
        app.state.df = df



def get_db():
    db = src_db.get_session()
    try:
        yield db
    finally:
        try:
            db.close()
        except Exception:
            pass


@app.get("/healthz")
def healthz() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/municipios", response_model=List[MunicipioSummary])
def list_municipios(
    q: Optional[str] = Query(None, description="Buscar por nombre de municipio"),
    page: int = 1,
    per_page: int = 200,
    db: Session = Depends(get_db)
):
    # If DB available, query it
    if getattr(app.state, 'use_db', False):
        q_obj = db.query(MunicipioFeatures)
        if q:
            q_obj = q_obj.filter(MunicipioFeatures.municipio.ilike(f"%{q}%"))
        start = (page - 1) * per_page
        rows = q_obj.offset(start).limit(per_page).all()
        results = []
        for r in rows:
            results.append(
                MunicipioSummary(
                    divipola=r.divipola,
                    municipio=r.municipio,
                    ira_score=r.ira_score,
                    ira_level=r.ira_level,
                ).dict()
            )
        return results

    # Fallback to parquet
    df: pd.DataFrame = getattr(app.state, 'df', None)
    if df is None:
        raise HTTPException(status_code=503, detail="Data not available: municipio_features.parquet not found")

    out = df.copy()
    if q:
        qlow = q.lower()
        if "municipio" in out.columns:
            out = out[out["municipio"].str.lower().str.contains(qlow, na=False)]

    start = (page - 1) * per_page
    end = start + per_page
    results = []
    for _, row in out.iloc[start:end].iterrows():
        div = str(row.get("divipola", ""))
        results.append(
            MunicipioSummary(
                divipola=div,
                municipio=row.get("municipio"),
                ira_score=row.get("ira_score"),
                ira_level=row.get("ira_level"),
            ).dict()
        )
    return results


@app.get("/municipios/geojson")
def municipios_geojson(
    q: Optional[str] = Query(None, description="Buscar por nombre de municipio"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    features = []
    if getattr(app.state, 'use_db', False):
        q_obj = db.query(MunicipioFeatures)
        if q:
            q_obj = q_obj.filter(MunicipioFeatures.municipio.ilike(f"%{q}%"))
        for inst in q_obj.all():
            geom = _normalize_geom(getattr(inst, 'geom'))
            props = {
                c.name: _normalize_value(getattr(inst, c.name))
                for c in MunicipioFeatures.__table__.columns
                if c.name != 'geom'
            }
            features.append({
                'type': 'Feature',
                'geometry': geom,
                'properties': props,
            })
        return {'type': 'FeatureCollection', 'features': features}

    df: pd.DataFrame = getattr(app.state, 'df', None)
    if df is None:
        raise HTTPException(status_code=503, detail='Data not available')
    out = df.copy()
    if q:
        qlow = q.lower()
        if 'municipio' in out.columns:
            out = out[out['municipio'].str.lower().str.contains(qlow, na=False)]
    for _, row in out.iterrows():
        geom = _normalize_geom(row.get('geom')) if 'geom' in out.columns else None
        props = {
            col: _normalize_value(row[col])
            for col in out.columns
            if col != 'geom'
        }
        features.append({
            'type': 'Feature',
            'geometry': geom,
            'properties': props,
        })
    return {'type': 'FeatureCollection', 'features': features}


@app.get("/metrics")
def metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    if getattr(app.state, 'use_db', False):
        rows = db.query(MunicipioFeatures).all()
        total = len(rows)
        ira_scores = [r.ira_score for r in rows if r.ira_score is not None]
        average_ira_score = sum(ira_scores) / len(ira_scores) if ira_scores else None
        counts = Counter([r.ira_level or 'Unknown' for r in rows])
        top = sorted(
            [r for r in rows if r.ira_score is not None],
            key=lambda r: r.ira_score,
            reverse=True,
        )[:5]
        return {
            'total_municipios': total,
            'average_ira_score': average_ira_score,
            'count_by_level': dict(counts),
            'top_municipios': [
                {
                    'divipola': r.divipola,
                    'municipio': r.municipio,
                    'ira_score': r.ira_score,
                    'ira_level': r.ira_level,
                }
                for r in top
            ],
        }

    df: pd.DataFrame = getattr(app.state, 'df', None)
    if df is None:
        raise HTTPException(status_code=503, detail='Data not available')
    total = len(df)
    average_ira_score = None
    if 'ira_score' in df.columns:
        valid_scores = df['ira_score'].dropna().astype(float)
        if len(valid_scores) > 0:
            average_ira_score = float(valid_scores.mean())
    count_by_level = {}
    if 'ira_level' in df.columns:
        count_by_level = df['ira_level'].fillna('Unknown').value_counts().to_dict()
    top_df = df[df['ira_score'].notna()].sort_values('ira_score', ascending=False).head(5)
    return {
        'total_municipios': int(total),
        'average_ira_score': average_ira_score,
        'count_by_level': {str(k): int(v) for k, v in count_by_level.items()},
        'top_municipios': [
            {
                'divipola': str(row.get('divipola')),
                'municipio': row.get('municipio'),
                'ira_score': row.get('ira_score'),
                'ira_level': row.get('ira_level'),
            }
            for _, row in top_df.iterrows()
        ],
    }


@app.get("/municipios/{divipola}")
def municipio_detail(divipola: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    if getattr(app.state, 'use_db', False):
        inst = db.get(MunicipioFeatures, divipola)
        if not inst:
            raise HTTPException(status_code=404, detail="Municipio not found")
        data = {}
        for c in MunicipioFeatures.__table__.columns:
            data[c.name] = _normalize_value(getattr(inst, c.name))
        return data

    df: pd.DataFrame = getattr(app.state, 'df', None)
    if df is None:
        raise HTTPException(status_code=503, detail="Data not available")
    row = df[df.get("divipola") == divipola]
    if row.empty:
        raise HTTPException(status_code=404, detail="Municipio not found")
    return _row_to_dict(row.iloc[0])


@app.get("/municipios/{divipola}/dimensiones")
def municipio_dimensiones(divipola: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    if getattr(app.state, 'use_db', False):
        inst = db.get(MunicipioFeatures, divipola)
        if not inst:
            raise HTTPException(status_code=404, detail="Municipio not found")
        dims = {}
        for c in MunicipioFeatures.__table__.columns:
            name = c.name
            if "dim" in name.lower() or "dimension" in name.lower() or "score" in name.lower():
                dims[name] = _normalize_value(getattr(inst, name))
        return dims

    df: pd.DataFrame = getattr(app.state, 'df', None)
    if df is None:
        raise HTTPException(status_code=503, detail="Data not available")
    row = df[df.get("divipola") == divipola]
    if row.empty:
        raise HTTPException(status_code=404, detail="Municipio not found")
    row = row.iloc[0]
    dims = {}
    for col in row.index:
        if "dim" in col.lower() or "dimension" in col.lower() or "score" in col.lower():
            dims[col] = _normalize_value(row[col])
    return dims


@app.get("/alertas")
def alertas(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    if getattr(app.state, 'use_db', False):
        q_obj = db.query(MunicipioFeatures)
        # filter by ira_level or ira_score
        q_obj = q_obj.filter(
            (MunicipioFeatures.ira_level.in_(["Alto", "Crítico", "Crítico ", "Alto "]))
            | (MunicipioFeatures.ira_score >= 0.5)
        )
        rows = q_obj.all()
        res = []
        for r in rows:
            res.append({"divipola": r.divipola, "municipio": r.municipio, "ira_level": r.ira_level, "ira_score": r.ira_score})
        return res

    df: pd.DataFrame = getattr(app.state, 'df', None)
    if df is None:
        raise HTTPException(status_code=503, detail="Data not available")
    out = df.copy()
    # Prefer explicit ira_level, fallback to ira_score
    if "ira_level" in out.columns:
        mask = out["ira_level"].isin(["Alto", "Crítico", "Crítico ", "Alto "])
    elif "ira_score" in out.columns:
        mask = out["ira_score"] >= 0.5
    else:
        mask = [False] * len(out)
    res = []
    for _, row in out[mask].iterrows():
        res.append({"divipola": str(row.get("divipola")), "municipio": row.get("municipio"), "ira_level": row.get("ira_level"), "ira_score": row.get("ira_score")})
    return res


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
