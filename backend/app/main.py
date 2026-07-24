from collections import Counter
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


def _parquet_candidates(*names: str) -> List[Path]:
    root = _project_root()
    directories = [
        root / "data" / "04_model_output",
        root / "data" / "03_primary",
        root / "data" / "02_intermediate",
        root / "data",
    ]
    paths: List[Path] = []
    for directory in directories:
        for name in names:
            paths.append(directory / name)
    return paths


def _load_parquet_if_available(*names: str) -> Optional[pd.DataFrame]:
    for path in _parquet_candidates(*names):
        if path.exists():
            try:
                df = pd.read_parquet(path)
                return df
            except Exception:
                continue
    return None


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
            if value.startswith("SRID="):
                _, wkt_text = value.split(";", 1)
                return mapping(wkt.loads(wkt_text))
            return mapping(wkt.loads(value))
        except Exception:
            return None
    if hasattr(value, "geom_type"):
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
            return value.decode("utf-8")
        except Exception:
            return value.hex()
    if isinstance(value, str):
        return value
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return value


def _normalize_level(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        cleaned = cleaned.replace("CrÃ­tico", "Crítico").replace("CrÃtico", "Crítico")
        cleaned = cleaned.replace("Crítico", "Crítico")
        return cleaned
    return value


def _normalize_dataframe(df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
    if df is None:
        return None
    out = df.copy()
    if "divipola" in out.columns:
        out["divipola"] = out["divipola"].astype(str)
    if "ira_level" not in out.columns and "nivel_ira" in out.columns:
        out["ira_level"] = out["nivel_ira"].apply(_normalize_level)
    if "ira_score" not in out.columns and "ira_riesgo" in out.columns:
        out["ira_score"] = pd.to_numeric(out["ira_riesgo"], errors="coerce")
    if "ira_level" in out.columns:
        out["ira_level"] = out["ira_level"].apply(_normalize_level)
    if "ira_score" in out.columns:
        out["ira_score"] = pd.to_numeric(out["ira_score"], errors="coerce")
    if "anio" in out.columns:
        out["anio"] = pd.to_numeric(out["anio"], errors="coerce")
    if "escenario" in out.columns:
        out["escenario"] = out["escenario"].fillna("").astype(str).str.strip()
    return out


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


def _get_municipios_df() -> Optional[pd.DataFrame]:
    municipios_df = getattr(app.state, "municipios_df", None)
    if municipios_df is not None:
        return _normalize_dataframe(municipios_df)
    return _normalize_dataframe(getattr(app.state, "df", None))


def _get_timeline_df() -> Optional[pd.DataFrame]:
    df = getattr(app.state, "timeline_df", None)
    return _normalize_dataframe(df)


def _get_eva_df() -> Optional[pd.DataFrame]:
    df = getattr(app.state, "eva_df", None)
    return _normalize_dataframe(df)


def _get_cultivos_df() -> Optional[pd.DataFrame]:
    df = getattr(app.state, "cultivos_df", None)
    return _normalize_dataframe(df)


def _get_cultivos_or_eva_df() -> Optional[pd.DataFrame]:
    cultivos_df = _get_cultivos_df()
    eva_df = _get_eva_df()

    if cultivos_df is not None and not cultivos_df.empty:
        return cultivos_df
    if eva_df is not None and not eva_df.empty:
        return eva_df
    return cultivos_df if cultivos_df is not None else eva_df


def _get_municipio_cultivos_df() -> Optional[pd.DataFrame]:
    cultivos_df = _get_cultivos_df()
    if cultivos_df is not None and not cultivos_df.empty and "divipola" in cultivos_df.columns:
        return cultivos_df

    eva_df = _get_eva_df()
    if eva_df is not None and not eva_df.empty and "divipola" in eva_df.columns:
        return eva_df

    return None


def _get_alertas_df() -> Optional[pd.DataFrame]:
    df = getattr(app.state, "alertas_df", None)
    return _normalize_dataframe(df)


def _get_geometry_df() -> Optional[pd.DataFrame]:
    return getattr(app.state, "poligonos_df", None)


def _get_geometry_for_divipola(divipola: str) -> Any:
    geometry_df = _get_geometry_df()
    if geometry_df is None or "divipola" not in geometry_df.columns:
        return None
    match = geometry_df[geometry_df["divipola"].astype(str) == str(divipola)]
    if match.empty:
        return None
    row = match.iloc[0]
    return _normalize_geom(row.get("geom")) if "geom" in row.index else None


@app.on_event("startup")
def load_data() -> None:
    use_db = False
    try:
        use_db = src_db.test_connection()
    except Exception:
        use_db = False

    app.state.use_db = bool(use_db) and MunicipioFeatures is not None
    app.state.df = None
    app.state.municipios_df = _normalize_dataframe(
        _load_parquet_if_available("ira_municipal_final.parquet", "municipio_features.parquet")
    )
    app.state.timeline_df = _normalize_dataframe(
        _load_parquet_if_available("ira_timeline_completo.parquet")
    )
    app.state.eva_df = _normalize_dataframe(
        _load_parquet_if_available("eva_historico_municipios.parquet", "eva_limpia.parquet")
    )
    app.state.cultivos_df = _normalize_dataframe(
        _load_parquet_if_available("cultivos_proyeccion_2029.parquet")
    )
    app.state.alertas_df = _normalize_dataframe(
        _load_parquet_if_available("alertas_municipios.parquet")
    )
    app.state.poligonos_df = _normalize_dataframe(
        _load_parquet_if_available("poligonos_municipales.parquet")
    )
    if not app.state.use_db:
        app.state.df = app.state.municipios_df


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
    db: Session = Depends(get_db),
):
    if getattr(app.state, "use_db", False):
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

    df = _get_municipios_df()
    if df is None:
        raise HTTPException(status_code=503, detail="Data not available: parquet files not found")

    out = df.copy()
    if q:
        qlow = q.lower()
        if "municipio" in out.columns:
            out = out[out["municipio"].astype(str).str.lower().str.contains(qlow, na=False)]

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
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    features = []
    if getattr(app.state, "use_db", False):
        q_obj = db.query(MunicipioFeatures)
        if q:
            q_obj = q_obj.filter(MunicipioFeatures.municipio.ilike(f"%{q}%"))
        for inst in q_obj.all():
            geom = _normalize_geom(getattr(inst, "geom"))
            props = {
                c.name: _normalize_value(getattr(inst, c.name))
                for c in MunicipioFeatures.__table__.columns
                if c.name != "geom"
            }
            features.append({"type": "Feature", "geometry": geom, "properties": props})
        return {"type": "FeatureCollection", "features": features}

    df = _get_municipios_df()
    if df is None:
        raise HTTPException(status_code=503, detail="Data not available")
    out = df.copy()
    if q:
        qlow = q.lower()
        if "municipio" in out.columns:
            out = out[out["municipio"].astype(str).str.lower().str.contains(qlow, na=False)]
    for _, row in out.iterrows():
        geom = _normalize_geom(row.get("geom")) if "geom" in out.columns else None
        props = {col: _normalize_value(row[col]) for col in out.columns if col != "geom"}
        features.append({"type": "Feature", "geometry": geom, "properties": props})
    return {"type": "FeatureCollection", "features": features}


@app.get("/metrics")
def metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    if getattr(app.state, "use_db", False):
        rows = db.query(MunicipioFeatures).all()
        total = len(rows)
        ira_scores = [r.ira_score for r in rows if r.ira_score is not None]
        average_ira_score = sum(ira_scores) / len(ira_scores) if ira_scores else None
        counts = Counter([r.ira_level or "Unknown" for r in rows])
        top = sorted(
            [r for r in rows if r.ira_score is not None],
            key=lambda r: r.ira_score,
            reverse=True,
        )[:5]
        return {
            "total_municipios": total,
            "average_ira_score": average_ira_score,
            "count_by_level": dict(counts),
            "top_municipios": [
                {
                    "divipola": r.divipola,
                    "municipio": r.municipio,
                    "ira_score": r.ira_score,
                    "ira_level": r.ira_level,
                }
                for r in top
            ],
        }

    df = _get_municipios_df()
    if df is None:
        raise HTTPException(status_code=503, detail="Data not available")
    total = len(df)
    average_ira_score = None
    if "ira_score" in df.columns:
        valid_scores = df["ira_score"].dropna().astype(float)
        if len(valid_scores) > 0:
            average_ira_score = float(valid_scores.mean())
    count_by_level = {}
    if "ira_level" in df.columns:
        count_by_level = df["ira_level"].fillna("Unknown").value_counts().to_dict()
    top_df = df[df["ira_score"].notna()].sort_values("ira_score", ascending=False).head(5)
    return {
        "total_municipios": int(total),
        "average_ira_score": average_ira_score,
        "count_by_level": {str(k): int(v) for k, v in count_by_level.items()},
        "top_municipios": [
            {
                "divipola": str(row.get("divipola")),
                "municipio": row.get("municipio"),
                "ira_score": row.get("ira_score"),
                "ira_level": row.get("ira_level"),
            }
            for _, row in top_df.iterrows()
        ],
    }


@app.get("/municipios/{divipola}")
def municipio_detail(divipola: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    if getattr(app.state, "use_db", False):
        inst = db.get(MunicipioFeatures, divipola)
        if not inst:
            raise HTTPException(status_code=404, detail="Municipio not found")
        data = {}
        for c in MunicipioFeatures.__table__.columns:
            data[c.name] = _normalize_value(getattr(inst, c.name))
        return data

    df = _get_municipios_df()
    if df is None:
        raise HTTPException(status_code=503, detail="Data not available")
    row = df[df.get("divipola") == divipola]
    if row.empty:
        raise HTTPException(status_code=404, detail="Municipio not found")
    return _row_to_dict(row.iloc[0])


@app.get("/municipios/{divipola}/dimensiones")
def municipio_dimensiones(divipola: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    if getattr(app.state, "use_db", False):
        inst = db.get(MunicipioFeatures, divipola)
        if not inst:
            raise HTTPException(status_code=404, detail="Municipio not found")
        dims = {}
        for c in MunicipioFeatures.__table__.columns:
            name = c.name
            if "dim" in name.lower() or "dimension" in name.lower() or "score" in name.lower():
                dims[name] = _normalize_value(getattr(inst, name))
        return dims

    df = _get_municipios_df()
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


@app.get("/municipios/{divipola}/cultivos")
def municipio_cultivos(divipola: str) -> Dict[str, Any]:
    df = _get_municipio_cultivos_df()
    if df is None:
        raise HTTPException(status_code=503, detail="Data not available")

    sub = df[df["divipola"].astype(str) == str(divipola)].copy()
    if sub.empty:
        raise HTTPException(status_code=404, detail="Municipio not found")

    year = 2024
    if "anio" in sub.columns:
        sub = sub[sub["anio"].astype(str) == str(year)]
        if sub.empty:
            sub = df[df["divipola"].astype(str) == str(divipola)].copy()

    if sub.empty:
        return {"divipola": divipola, "anio": year, "cultivos": []}

    value_col = next(
        (
            col
            for col in [
                "produccion_total_ton",
                "valor",
                "produccion",
                "produccion_ton",
                "volumen",
                "cantidad",
                "area_sembrada_ha",
            ]
            if col in sub.columns
        ),
        None,
    )
    if value_col is None:
        grouped = sub.groupby("cultivo", dropna=False).size().reset_index(name="registros")
        grouped = grouped.sort_values(["registros", "cultivo"], ascending=[False, True])
        top = grouped.head(5)
        return {
            "divipola": divipola,
            "anio": year,
            "cultivos": [
                {"cultivo": str(row["cultivo"]), "valor": None, "registros": int(row["registros"])}
                for _, row in top.iterrows()
            ],
        }

    grouped = sub.groupby("cultivo", dropna=False)[value_col].sum().reset_index(name="valor")
    grouped = grouped.sort_values(["valor", "cultivo"], ascending=[False, True])
    top = grouped.head(5)
    return {
        "divipola": divipola,
        "anio": year,
        "cultivos": [
            {"cultivo": str(row["cultivo"]), "valor": float(row["valor"]), "unidad": value_col}
            for _, row in top.iterrows()
        ],
    }


@app.get("/municipios/{divipola}/cultivos/historico")
def municipio_cultivos_historico(divipola: str) -> Dict[str, Any]:
    df = _get_municipio_cultivos_df()
    if df is None:
        raise HTTPException(status_code=503, detail="Data not available")

    sub = df[df["divipola"].astype(str) == str(divipola)].copy()
    if sub.empty:
        raise HTTPException(status_code=404, detail="Municipio not found")

    value_col = next(
        (
            col
            for col in [
                "produccion_total_ton",
                "valor",
                "produccion",
                "produccion_ton",
                "volumen",
                "cantidad",
                "area_sembrada_ha",
            ]
            if col in sub.columns
        ),
        None,
    )
    if "anio" not in sub.columns:
        return {"divipola": divipola, "serie": []}

    if value_col is None:
        grouped = sub.groupby("anio", dropna=False).size().reset_index(name="registros")
    else:
        grouped = sub.groupby("anio", dropna=False)[value_col].sum().reset_index(name="valor")

    grouped = grouped.sort_values("anio")
    return {
        "divipola": divipola,
        "serie": [
            {"anio": int(row["anio"]), "valor": float(row["valor"]) if value_col else int(row["registros"])}
            for _, row in grouped.iterrows()
        ],
    }


@app.get("/timeline/geojson")
def timeline_geojson(escenario: Optional[str] = Query(None), anio: Optional[int] = Query(None)) -> Dict[str, Any]:
    df = _get_timeline_df()
    if df is None:
        raise HTTPException(status_code=503, detail="Data not available")

    filtered = df.copy()
    if escenario:
        filtered = filtered[filtered["escenario"].astype(str).str.lower() == escenario.lower()]
    if anio is not None and "anio" in filtered.columns:
        filtered = filtered[filtered["anio"].astype(str) == str(anio)]

    features = []
    for _, row in filtered.iterrows():
        divipola = str(row.get("divipola", ""))
        geom = _normalize_geom(row.get("geom")) if "geom" in row.index else None
        if geom is None:
            geom = _get_geometry_for_divipola(divipola)
        props = {
            col: _normalize_value(row[col])
            for col in filtered.columns
            if col != "geom"
        }
        features.append({"type": "Feature", "geometry": geom, "properties": props})

    return {"type": "FeatureCollection", "features": features}


@app.get("/timeline")
def timeline(escenario: Optional[str] = Query(None), anio: Optional[int] = Query(None)) -> Dict[str, Any]:
    df = _get_timeline_df()
    if df is None:
        raise HTTPException(status_code=503, detail="Data not available")

    filtered = df.copy()
    if escenario:
        filtered = filtered[filtered["escenario"].astype(str).str.lower() == escenario.lower()]
    if anio is not None and "anio" in filtered.columns:
        filtered = filtered[filtered["anio"].astype(str) == str(anio)]

    return {
        "escenario": escenario,
        "anio": anio,
        "results": [
            {col: _normalize_value(row[col]) for col in filtered.columns}
            for _, row in filtered.iterrows()
        ],
    }


@app.get("/cultivos/riesgo")
def cultivos_riesgo(anio: Optional[int] = Query(None), escenario: Optional[str] = Query(None)) -> Dict[str, Any]:
    df = _get_cultivos_or_eva_df()
    if df is None:
        raise HTTPException(status_code=503, detail="Data not available")

    filtered = df.copy()
    if anio is not None and "anio" in filtered.columns:
        filtered = filtered[filtered["anio"].astype(str) == str(anio)]
    if escenario and "escenario" in filtered.columns:
        filtered = filtered[filtered["escenario"].astype(str).str.lower() == escenario.lower()]

    if filtered.empty:
        return {"anio": anio, "escenario": escenario, "cultivos": []}

    value_col = next((col for col in ["riesgo", "score", "score_riesgo", "valor", "ira_score"] if col in filtered.columns), None)
    if value_col is None or "cultivo" not in filtered.columns:
        return {"anio": anio, "escenario": escenario, "cultivos": []}

    grouped = filtered.groupby("cultivo", dropna=False)[value_col].mean().reset_index(name="score")
    grouped = grouped.sort_values(["score", "cultivo"], ascending=[False, True])
    return {
        "anio": anio,
        "escenario": escenario,
        "cultivos": [
            {"cultivo": str(row["cultivo"]), "score": float(row["score"])}
            for _, row in grouped.head(10).iterrows()
        ],
    }


@app.get("/alertas/municipio/{divipola}")
def alerta_municipio(divipola: str) -> Dict[str, Any]:
    alertas_df = _get_alertas_df()
    municipios_df = _get_municipios_df()

    if alertas_df is None and municipios_df is None:
        raise HTTPException(status_code=503, detail="Data not available")

    sub = pd.DataFrame()
    if alertas_df is not None and "divipola" in alertas_df.columns:
        sub = alertas_df[alertas_df["divipola"].astype(str) == str(divipola)].copy()

    if sub.empty and municipios_df is not None and "divipola" in municipios_df.columns:
        sub = municipios_df[municipios_df["divipola"].astype(str) == str(divipola)].copy()

    if sub.empty:
        raise HTTPException(status_code=404, detail="Municipio not found")

    row = sub.iloc[0]
    alert_level = next(
        (
            _normalize_value(row[col])
            for col in ["nivel_alerta", "alerta", "alerta_nivel", "ira_level"]
            if col in row.index and pd.notna(row[col])
        ),
        None,
    )
    if alert_level is None and "ira_level" in row.index:
        alert_level = "Crítico" if str(row["ira_level"]).lower() in {"crítico", "critico", "alto"} else row["ira_level"]

    color = "ROJA" if str(alert_level).lower() in {"crítico", "critico", "roja", "alta"} else "AMARILLA"
    return {
        "divipola": divipola,
        "municipio": row.get("municipio"),
        "nivel_alerta": alert_level,
        "color": color,
        "ira_score": row.get("ira_score"),
        "ira_level": row.get("ira_level"),
    }


@app.get("/escenarios")
def escenarios() -> Dict[str, Any]:
    scenario_values: List[str] = []
    for df in (_get_timeline_df(), _get_cultivos_df(), _get_eva_df()) :
        if df is not None and "escenario" in df.columns:
            scenario_values.extend([str(value).strip() for value in df["escenario"].dropna().astype(str).unique() if str(value).strip()])

    unique_scenarios = sorted(dict.fromkeys(scenario_values))
    if not unique_scenarios:
        unique_scenarios = ["Real", "Optimista", "Base", "Pesimista"]
    return {"escenarios": unique_scenarios}


@app.get("/alertas")
def alertas(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    if getattr(app.state, "use_db", False):
        q_obj = db.query(MunicipioFeatures)
        q_obj = q_obj.filter(
            (MunicipioFeatures.ira_level.in_(["Alto", "Crítico", "Crítico ", "Alto "]))
            | (MunicipioFeatures.ira_score >= 0.5)
        )
        rows = q_obj.all()
        res = []
        for r in rows:
            res.append({"divipola": r.divipola, "municipio": r.municipio, "ira_level": r.ira_level, "ira_score": r.ira_score})
        return res

    df = _get_municipios_df()
    if df is None:
        raise HTTPException(status_code=503, detail="Data not available")
    out = df.copy()
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
