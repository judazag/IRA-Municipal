import time
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
from sodapy import Socrata
from pipeline.utils.config import config
from pipeline.utils.logger import get_logger

logger = get_logger("ingesta.soda")

class ConectorSODA:
    """
    Conector genérico para la SODA API de datos.gov.co.
    Maneja paginación, reintentos y almacenamiento en Parquet.
    """

    BASE_DOMAIN = "www.datos.gov.co"

    def __init__(self):
        self.client = Socrata(
            self.BASE_DOMAIN,
            None,  # Sin token — acceso público
            timeout=config.soda.timeout,
        )
        self.page_size = config.soda.page_size
        self.raw_path = Path(config.paths.data_raw)

    def _get_total_registros(self, dataset_id: str, where: str = None) -> int:
        params = {"select": "count(*)"}
        if where:
            params["where"] = where
        resultado = self.client.get(dataset_id, **params)
        return int(resultado[0]["count"])

    def descargar(
        self,
        dataset_id: str,
        nombre: str,
        columnas: list = None,
        where: str = None,
        max_reintentos: int = 3,
    ) -> pd.DataFrame:
        """
        Descarga un dataset completo de la SODA API con paginación.

        Args:
            dataset_id: ID del dataset en datos.gov.co
            nombre: Nombre descriptivo para logs y archivo
            columnas: Lista de columnas a seleccionar (None = todas)
            where: Filtro SoQL opcional
            max_reintentos: Número de reintentos por página

        Returns:
            DataFrame con todos los registros
        """
        logger.info(f"Iniciando descarga: {nombre} ({dataset_id})")

        # Total de registros
        total = self._get_total_registros(dataset_id, where)
        logger.info(f"Total registros a descargar: {total:,}")

        registros = []
        offset = 0
        pagina = 1

        while offset < total:
            intento = 0
            while intento < max_reintentos:
                try:
                    params = {
                        "limit": self.page_size,
                        "offset": offset,
                        "order": ":id",
                    }
                    if columnas:
                        params["select"] = ", ".join(columnas)
                    if where:
                        params["where"] = where

                    resultado = self.client.get(dataset_id, **params)
                    registros.extend(resultado)

                    logger.info(
                        f"  Página {pagina} — registros {offset:,} a {min(offset + self.page_size, total):,} de {total:,}"
                    )
                    break

                except Exception as e:
                    intento += 1
                    logger.warning(f"  Error en página {pagina}, intento {intento}/{max_reintentos}: {e}")
                    if intento == max_reintentos:
                        logger.error(f"  Falló página {pagina} después de {max_reintentos} intentos")
                        raise
                    time.sleep(2 ** intento)  # Backoff exponencial

            offset += self.page_size
            pagina += 1
            time.sleep(0.2)  # Rate limiting

        df = pd.DataFrame.from_records(registros)
        logger.info(f"Descarga completa: {len(df):,} registros — {nombre}")
        return df

    def guardar_parquet(
        self,
        df: pd.DataFrame,
        fuente: str,
        nombre: str,
        año: str = None,
    ) -> Path:
        """
        Guarda un DataFrame en formato Parquet particionado por fuente.

        Args:
            df: DataFrame a guardar
            fuente: Nombre de la fuente (ej: 'eva', 'sipsa_a')
            nombre: Nombre del archivo
            año: Año para particionado opcional

        Returns:
            Path del archivo guardado
        """
        if año:
            ruta = self.raw_path / fuente / f"año={año}"
        else:
            ruta = self.raw_path / fuente

        ruta.mkdir(parents=True, exist_ok=True)
        archivo = ruta / f"{nombre}.parquet"

        tabla = pa.Table.from_pandas(df)
        pq.write_table(tabla, archivo, compression="snappy")

        tamaño_mb = archivo.stat().st_size / (1024 * 1024)
        logger.info(f"Guardado: {archivo} ({tamaño_mb:.1f} MB)")
        return archivo

    def descargar_y_guardar(
        self,
        dataset_id: str,
        nombre: str,
        fuente: str,
        columnas: list = None,
        where: str = None,
        año: str = None,
    ) -> pd.DataFrame:
        """
        Descarga y guarda en Parquet en un solo paso.
        """
        df = self.descargar(dataset_id, nombre, columnas, where)
        self.guardar_parquet(df, fuente, nombre, año)
        return df

    def cerrar(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.cerrar()
