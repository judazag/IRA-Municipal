from pathlib import Path
import pandas as pd
from shapely.geometry import Polygon

def main():
    out = Path(__file__).resolve().parents[1] / "data" / "03_primary"
    out.mkdir(parents=True, exist_ok=True)

    rows = []
    sample = [
        ("11001", 'Bogotá D.C.', 0.12, 'Bajo', Polygon([(-74.09,4.60),(-74.00,4.60),(-74.00,4.65),(-74.09,4.65)])),
        ("05001", 'Medellín', 0.45, 'Medio', Polygon([(-75.59,6.22),(-75.55,6.22),(-75.55,6.27),(-75.59,6.27)])),
        ("08001", 'Cartagena', 0.62, 'Alto', Polygon([(-75.53,10.38),(-75.48,10.38),(-75.48,10.42),(-75.53,10.42)])),
        ("76001", 'Cali', 0.78, 'Crítico', Polygon([(-76.53,3.40),(-76.48,3.40),(-76.48,3.45),(-76.53,3.45)])),
        ("05002", 'Envigado', 0.35, 'Medio', Polygon([(-75.58,6.16),(-75.55,6.16),(-75.55,6.18),(-75.58,6.18)])),
    ]

    for div, muni, score, level, poly in sample:
        rows.append({
            'divipola': div,
            'municipio': muni,
            'ira_score': float(score),
            'ira_level': level,
            'geom': poly.wkt,
        })

    df = pd.DataFrame(rows)
    path = out / 'municipio_features.parquet'
    df.to_parquet(path, index=False)
    print(f'Wrote sample parquet to {path}')

if __name__ == '__main__':
    main()
