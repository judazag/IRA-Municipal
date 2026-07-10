import time
import io
import requests
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
from sodapy import Socrata
from src.config import config
from src.logger import get_logger

logger = get_logger("data_ingestion")

# ─── CATÁLOGO DE DATASETS ─────────────────────────────────────────────────────

DATASETS_BASE = {
    "uejq-wxrr": ("eva",              "EVA 2019-2024"),
    "fyc7-sbtz": ("frontera_agricola","Frontera Agrícola"),
    "rtxu-twjm": ("distritos_riego",  "Distritos de Riego"),
    "hc6u-q778": ("informalidad",     "Informalidad de Tierras"),
    "w3uf-w9ey": ("finagro",          "Créditos Finagro"),
    "hp9r-jxuu": ("ideam",            "Estaciones IDEAM"),
    "nsz2-kzcq": ("ideam",            "Normales Climatológicas"),
}

DATASETS_APTITUD = {
    "kwvf-nwea": ("cafe",          "Nacional"),
    "qaa2-6p2j": ("cafe",          "Quindío"),
    "ggaa-6f3s": ("cafe",          "Nariño"),
    "879x-8fjs": ("cafe",          "Meta"),
    "h4ms-ukui": ("cafe",          "Cesar"),
    "jdjx-qer4": ("cacao",         "Nacional"),
    "mqnw-3mh7": ("cacao",         "Nariño"),
    "rudm-65w2": ("cacao",         "Huila"),
    "mb3q-3sz7": ("cacao",         "Quindío"),
    "y9yk-egv6": ("cacao",         "Cesar"),
    "tx7u-frn2": ("aguacate",      "Nacional"),
    "7iny-qc7t": ("aguacate",      "Quindío"),
    "4ia2-7v6d": ("aguacate",      "Cesar"),
    "eyi3-xt36": ("aguacate",      "Caldas"),
    "636v-m2ev": ("aguacate",      "Huila"),
    "jypt-2gk9": ("aguacate",      "Guaviare"),
    "25qu-8req": ("aguacate",      "Huila_Lorena"),
    "fy4v-wdq8": ("aguacate",      "Cundinamarca"),
    "69q9-rai5": ("aguacate",      "Providencia"),
    "xt32-m7dh": ("mango",         "Nacional"),
    "3et4-t2c5": ("mango",         "Cesar"),
    "y4cn-bxu2": ("mango",         "Providencia"),
    "rcfj-3e57": ("platano_banano","Nacional_Banano"),
    "u2p6-8yb3": ("platano_banano","Cundinamarca"),
    "dem5-6d9s": ("platano_banano","Atlántico"),
    "ivuy-xix4": ("platano_banano","Quindío"),
    "b54w-9ds5": ("platano_banano","La_Guajira"),
    "s677-e5cz": ("platano_banano","Meta"),
    "6wzx-ggdn": ("platano_banano","Huila"),
    "3yy6-rhsa": ("platano_banano","Guaviare"),
    "anfi-qbc9": ("platano_banano","Nariño"),
    "ajqd-rrw4": ("platano_banano","Providencia"),
    "5rh6-a2iu": ("platano_banano","Quindío_Banano"),
    "8fa5-z4v3": ("pina",          "Nacional"),
    "64hn-54ty": ("pina",          "Guaviare"),
    "urxm-qzje": ("papaya",        "Nacional"),
    "qas8-ccb3": ("papaya",        "Providencia"),
    "hxs5-w7gt": ("maracuya",      "Nacional"),
    "y9hs-jfab": ("maracuya",      "Providencia"),
    "q6xp-whkm": ("gulupa",        "Nacional"),
    "aikj-ub3k": ("granadilla",    "Nacional"),
    "mhhn-vmqz": ("granadilla",    "Nariño"),
    "9med-ri2n": ("granadilla",    "Huila"),
    "emsg-94di": ("fresa",         "Nacional"),
    "p9xp-sm4v": ("cana_panelera", "Nacional"),
    "6x5b-q3gn": ("cana_panelera", "Cundinamarca"),
    "3mhn-7v7g": ("cana_panelera", "Nariño"),
    "pkzc-fdc6": ("cana_panelera", "Providencia"),
    "frjn-92um": ("maiz",          "Nacional_Tradicional"),
    "a5yc-uszt": ("maiz",          "Nacional_Tecnificado_S1"),
    "tzga-4zse": ("maiz",          "Nacional_Tecnificado_S2"),
    "2jg2-cz3h": ("maiz",          "Nariño"),
    "5xf8-ad6s": ("maiz",          "Atlántico"),
    "v7fj-zkda": ("maiz",          "Huila"),
    "7w2f-3igv": ("maiz",          "Guaviare"),
    "nrux-cqtm": ("maiz",          "Cesar_S1"),
    "rbyp-j3mc": ("maiz",          "Cesar_S2"),
    "difg-83ug": ("maiz",          "La_Guajira"),
    "debn-kdjs": ("maiz",          "Providencia"),
    "g39x-8d2s": ("maiz",          "Boyacá"),
    "ibc9-9f7c": ("arroz",         "Nacional_Secano"),
    "53g3-xmry": ("arroz",         "Cesar"),
    "29cv-av7d": ("arroz",         "Cundinamarca"),
    "xk39-mtxv": ("arroz",         "Huila"),
    "2qt2-dhv7": ("soya",          "Nacional_S1"),
    "hixf-wnis": ("soya",          "Nacional_S2"),
    "4vcv-s5e4": ("soya",          "Meta_S1"),
    "sndv-njkv": ("soya",          "Meta_S2"),
    "jwn7-76wn": ("papa",          "Nacional_S1"),
    "s455-c4e6": ("papa",          "Nacional_S2"),
    "krw4-fwxq": ("papa",          "Nacional_Diacol_S1"),
    "xcau-7myt": ("papa",          "Nacional_Diacol_S2"),
    "pxyg-5a3u": ("papa",          "Nariño"),
    "eu27-em7n": ("papa",          "Boyacá"),
    "btsg-jtqh": ("cebolla",       "Nacional_S1"),
    "nxvg-ufyf": ("cebolla",       "Nacional_S2"),
    "s8ha-htq3": ("cebolla",       "Quindío_S1"),
    "3v25-65vb": ("cebolla",       "Quindío_S2"),
    "gmhx-jpnm": ("cebolla",       "Boyacá_Junca"),
    "j3wf-8pc3": ("cebolla",       "Providencia"),
    "ejwn-f7s3": ("pimenton",      "Nacional"),
    "jk8t-3tkp": ("pimenton",      "Providencia"),
    "yhkr-7mkb": ("aji",           "Nacional"),
    "kdv9-gkv3": ("aji",           "Atlántico"),
    "6qqs-nvat": ("aji",           "Providencia"),
    "3km6-irsn": ("frijol",        "Cundinamarca_S1"),
    "kkgy-qrxf": ("frijol",        "Cundinamarca_S2"),
    "a43r-dc7n": ("frijol",        "Nariño"),
    "x759-i2ry": ("frijol",        "La_Guajira"),
    "feta-2znm": ("frijol",        "Huila_S1"),
    "pfbw-b9ii": ("frijol",        "Huila_S2"),
    "xav2-8ydm": ("frijol",        "Providencia_Caupi"),
    "4r7r-xeii": ("arveja",        "Nariño"),
    "qxjk-6yi9": ("arveja",        "Cundinamarca"),
    "kt5r-xnym": ("leguminosas",   "Boyacá"),
    "ybku-2354": ("guandul",       "Providencia"),
    "uumx-3w28": ("yuca",          "La_Guajira"),
    "4nrr-z5es": ("yuca",          "Atlántico"),
    "y54p-nmuh": ("yuca",          "Guaviare"),
    "s285-a6ur": ("yuca",          "Meta"),
    "siim-cru8": ("yuca",          "Providencia"),
    "ktcq-6bpt": ("mora",          "Nariño"),
    "h47g-czi9": ("mora",          "Quindío"),
    "icwf-97sk": ("mora",          "Cundinamarca"),
    "xsme-6vyj": ("tomate",        "Huila"),
    "ijus-ubej": ("zanahoria",     "Cundinamarca"),
    "jggq-mvpu": ("brocoli",       "Nariño"),
    "72wu-5rhp": ("lechuga",       "Nariño"),
    "gcsg-vnpm": ("hortalizas",    "Cundinamarca"),
    "vmtc-ncna": ("citricos",      "Cesar_Naranja"),
    "ucuk-raek": ("citricos",      "Quindío_Limon"),
    "28p6-pmgg": ("citricos",      "Atlántico_Limon"),
    "stbn-yd46": ("citricos",      "Nariño_Limon"),
    "shk3-wean": ("citricos",      "Providencia"),
    "v534-yr4y": ("citricos",      "Guaviare"),
    "2ish-f4p6": ("patilla",       "Meta_S1"),
    "gd2m-mne6": ("patilla",       "Meta_S2"),
    "ya3i-feur": ("patilla",       "La_Guajira"),
    "uw8p-y6se": ("patilla",       "Providencia"),
    "pi86-3vyw": ("melon",         "La_Guajira"),
    "rtjr-qdfb": ("melon",         "Atlántico"),
    "ezuf-ch6k": ("melon",         "Providencia"),
    "u27e-3x6i": ("ahuyama",       "Atlántico"),
    "mvw3-dyd9": ("ahuyama",       "La_Guajira"),
    "x7ng-52ik": ("ahuyama",       "Providencia"),
    "r55b-dpkh": ("quinua",        "Nariño"),
    "c7qw-4mck": ("pirarucu",      "Nacional"),
    "sf4k-mkw2": ("tilapia",       "Nacional"),
    "9cr3-4384": ("trucha",        "Huila"),
    "76gh-h4ct": ("peces_nativos", "Huila"),
    "2cfr-3988": ("guanabana",     "Providencia"),
    "dy4b-zarf": ("coco",          "Providencia"),
    "7xfm-jym2": ("chontaduro",    "Guaviare"),
    "n5rr-wiea": ("arbol_pan",     "Providencia"),
    "yqqe-3s5c": ("batata",        "Providencia"),
    "2m9w-xveu": ("name",          "Providencia"),
}

# ─── CONECTOR SODA ────────────────────────────────────────────────────────────

class ConectorSODA:
    BASE_DOMAIN = "www.datos.gov.co"

    def __init__(self):
        self.client = Socrata(self.BASE_DOMAIN, None, timeout=config.soda.timeout)
        self.page_size = config.soda.page_size

    def _total(self, dataset_id: str) -> int:
        r = self.client.get(dataset_id, select="count(*)")
        return int(r[0]["count"])

    def descargar(self, dataset_id: str, nombre: str, columnas: list = None) -> pd.DataFrame:
        total = self._total(dataset_id)
        logger.info(f"Descargando {nombre} ({dataset_id}) — {total:,} registros")
        registros = []
        offset, pagina = 0, 1
        while offset < total:
            for intento in range(3):
                try:
                    params = {"limit": self.page_size, "offset": offset, "order": ":id"}
                    if columnas:
                        params["select"] = ", ".join(columnas)
                    registros.extend(self.client.get(dataset_id, **params))
                    logger.info(f"  Página {pagina} — {offset:,} a {min(offset+self.page_size,total):,} de {total:,}")
                    break
                except Exception as e:
                    if intento == 2:
                        raise
                    logger.warning(f"  Reintento {intento+1}/3: {e}")
                    time.sleep(2 ** intento)
            offset += self.page_size
            pagina += 1
            time.sleep(0.2)
        return pd.DataFrame.from_records(registros)

    def cerrar(self):
        self.client.close()

    def __enter__(self): return self
    def __exit__(self, *args): self.cerrar()

# ─── FUNCIONES DE INGESTA ─────────────────────────────────────────────────────

def guardar_parquet(df: pd.DataFrame, ruta: str) -> Path:
    path = Path(ruta)
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pandas(df), path, compression="snappy")
    mb = path.stat().st_size / (1024 * 1024)
    logger.info(f"Guardado: {path} ({mb:.1f} MB)")
    return path

def ingestar_soda(dataset_id: str, nombre: str, fuente: str, columnas: list = None) -> pd.DataFrame:
    with ConectorSODA() as soda:
        df = soda.descargar(dataset_id, nombre, columnas)
    guardar_parquet(df, f"{config.paths.raw}/{fuente}/{nombre}.parquet")
    return df

def ingestar_nbi() -> pd.DataFrame:
    logger.info("Descargando NBI Censo 2018...")
    url = "https://www.dane.gov.co/files/censo2018/informacion-tecnica/CNPV-2018-NBI.xlsx"
    r = requests.get(url, timeout=30)
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="Municipios", header=None, skiprows=10)
    df.columns = [
        "cod_depto","nombre_depto","cod_municipio","nombre_municipio",
        "nbi_total","miseria_total","vivienda_total","servicios_total",
        "hacinamiento_total","inasistencia_total","dependencia_total",
        "nbi_cabecera","miseria_cabecera","vivienda_cabecera","servicios_cabecera",
        "hacinamiento_cabecera","inasistencia_cabecera","dependencia_cabecera",
        "nbi_rural","miseria_rural","vivienda_rural","servicios_rural",
        "hacinamiento_rural","inasistencia_rural","dependencia_rural",
    ]
    df = df.dropna(subset=["cod_municipio"])
    df["cod_depto"] = df["cod_depto"].astype(float).astype(int).astype(str).str.zfill(2)
    df["cod_municipio"] = df["cod_municipio"].astype(float).astype(int).astype(str).str.zfill(3)
    df["divipola"] = df["cod_depto"] + df["cod_municipio"]
    df = df[df["cod_municipio"] != "000"]
    guardar_parquet(df, f"{config.paths.raw}/nbi/nbi_2018.parquet")
    logger.info(f"NBI: {len(df):,} municipios")
    return df

def ingestar_ipm(ruta_archivo: str) -> pd.DataFrame:
    logger.info("Cargando IPM Municipal 2018...")
    df = pd.read_excel(ruta_archivo, sheet_name="4_IPM Mpio dominios", header=0, dtype={"ID": str})
    df.columns = ["divipola","municipio","ipm_total","ipm_cabecera","ipm_rural"]
    df = df.dropna(subset=["divipola"])
    df["divipola"] = df["divipola"].str.zfill(5)
    guardar_parquet(df, f"{config.paths.raw}/ipm/ipm_municipal_2018.parquet")
    logger.info(f"IPM: {len(df):,} municipios")
    return df

def ingestar_ipm_privaciones(ruta_archivo: str) -> pd.DataFrame:
    logger.info("Cargando IPM Privaciones 2018...")
    df = pd.read_excel(ruta_archivo, sheet_name="6_Privaciones IPM Dpt-Mpio", header=1, dtype={"ID": str})
    df = df.dropna(subset=["ID"])
    df = df.rename(columns={"ID": "divipola", "Municipio": "municipio"})
    df["divipola"] = df["divipola"].str.zfill(5)
    guardar_parquet(df, f"{config.paths.raw}/ipm/ipm_privaciones_2018.parquet")
    logger.info(f"IPM Privaciones: {len(df):,} municipios | {len(df.columns)-2} privaciones")
    return df

def ingestar_sipsa_a(ruta_archivo: str) -> pd.DataFrame:
    logger.info("Cargando SIPSA-A...")
    df = pd.read_csv(ruta_archivo, sep=";", encoding="latin-1", dtype=str)
    col_divipola = "Divipola Municipio / ISO 3166-1 País Proc."
    df["divipola"] = df[col_divipola].str.replace("'", "").str.zfill(5)
    df["Cant Kg"] = pd.to_numeric(df["Cant Kg"], errors="coerce")
    guardar_parquet(df, f"{config.paths.raw}/sipsa_a/sipsa_a.parquet")
    logger.info(f"SIPSA-A: {len(df):,} registros | {df['divipola'].nunique():,} municipios")
    return df

def ingestar_sipsa_p(ruta_archivo: str) -> pd.DataFrame:
    logger.info("Cargando SIPSA-P...")
    df = pd.read_csv(ruta_archivo, sep=";", encoding="utf-8-sig")
    df["Precio promedio por kilogramo*"] = pd.to_numeric(
        df["Precio promedio por kilogramo*"].astype(str).str.replace(".", "").str.replace(",", "."),
        errors="coerce"
    )
    guardar_parquet(df, f"{config.paths.raw}/sipsa_p/sipsa_p.parquet")
    logger.info(f"SIPSA-P: {len(df):,} registros | {df['Mercado'].nunique()} mercados")
    return df

def ingestar_noaa_oni() -> pd.DataFrame:
    logger.info("Descargando NOAA ONI...")
    r = requests.get(config.apis.noaa_oni_url, timeout=15)
    lineas = [l.split() for l in r.text.strip().split("\n")[1:] if l.strip()]
    df = pd.DataFrame(lineas, columns=["season","year","total","anom"])
    for col in ["total","anom"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    guardar_parquet(df, f"{config.paths.raw}/noaa/oni.parquet")
    logger.info(f"NOAA ONI: {len(df):,} registros")
    return df

def ingestar_aptitud(solo_cultivos: list = None) -> pd.DataFrame:
    datasets = DATASETS_APTITUD
    if solo_cultivos:
        datasets = {k: v for k, v in DATASETS_APTITUD.items() if v[0] in solo_cultivos}

    logger.info(f"Descargando {len(datasets)} datasets de aptitud...")
    dfs, ok, error = [], 0, 0

    COLS_APTITUD = ["cod_depart","cod_dane_m","aptitud","gridcode","area_ha"]
    MAPEO_DIVIPOLA = ["cod_dane_m","cod_dane_municipio","cod_mpio"]

    with ConectorSODA() as soda:
        for dataset_id, (cultivo, cobertura) in datasets.items():
            nombre = f"{cultivo}_{cobertura}".lower().replace(" ", "_")
            try:
                try:
                    df = soda.descargar(dataset_id, nombre, COLS_APTITUD)
                except Exception:
                    logger.warning(f"  Fallback sin columnas: {nombre}")
                    df = soda.descargar(dataset_id, nombre, None)

                col_div = next((c for c in MAPEO_DIVIPOLA if c in df.columns), None)
                if not col_div:
                    logger.warning(f"  Sin DIVIPOLA en {nombre} — columnas: {list(df.columns)}")
                    error += 1
                    continue

                df["divipola"] = df[col_div].astype(str).str.zfill(5)
                df["area_ha"] = pd.to_numeric(df.get("area_ha", pd.Series()), errors="coerce")
                df["gridcode"] = pd.to_numeric(df.get("gridcode", pd.Series()), errors="coerce")
                df["cultivo"] = cultivo
                df["cobertura"] = cobertura
                df = df.dropna(subset=["divipola","area_ha"])
                df = df[df["divipola"].str.len() == 5]

                cols = ["divipola","aptitud","gridcode","area_ha","cultivo","cobertura"]
                dfs.append(df[[c for c in cols if c in df.columns]])
                ok += 1

            except Exception as e:
                logger.error(f"  Error en {nombre}: {e}")
                error += 1

    if not dfs:
        return pd.DataFrame()

    df_total = pd.concat(dfs, ignore_index=True)
    guardar_parquet(df_total, f"{config.paths.raw}/aptitud_suelos/aptitud_todos.parquet")
    logger.info(f"Aptitud: {len(df_total):,} registros | ✅ {ok} | ❌ {error}")
    return df_total
