import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class DatabaseConfig(BaseModel):
    host: str = os.getenv("POSTGRES_HOST", "localhost")
    port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    db: str = os.getenv("POSTGRES_DB", "ira_municipal")
    user: str = os.getenv("POSTGRES_USER", "ira_user")
    password: str = os.getenv("POSTGRES_PASSWORD", "")

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    @property
    def url_psycopg2(self) -> str:
        return f"host={self.host} port={self.port} dbname={self.db} user={self.user} password={self.password}"


class SodaConfig(BaseModel):
    base_url: str = os.getenv("SODA_BASE_URL", "https://www.datos.gov.co/resource")
    timeout: int = int(os.getenv("SODA_TIMEOUT", "30"))
    page_size: int = int(os.getenv("SODA_PAGE_SIZE", "50000"))


class ExternalApisConfig(BaseModel):
    noaa_oni_url: str = os.getenv("NOAA_ONI_URL", "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt")
    ideam_dhime_url: str = os.getenv("IDEAM_DHIME_URL", "http://dhime.ideam.gov.co/atencionciudadano/")


class PathsConfig(BaseModel):
    data_raw: str = os.getenv("DATA_RAW", "data/raw")
    data_processed: str = os.getenv("DATA_PROCESSED", "data/processed")


class Config(BaseModel):
    database: DatabaseConfig = DatabaseConfig()
    soda: SodaConfig = SodaConfig()
    apis: ExternalApisConfig = ExternalApisConfig()
    paths: PathsConfig = PathsConfig()


# Instancia global
config = Config()
