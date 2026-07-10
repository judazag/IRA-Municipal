import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.config import config
from src.logger import get_logger

logger = get_logger("db")

def get_engine():
    return create_engine(
        config.database.url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )

def get_connection():
    return psycopg2.connect(config.database.url_psycopg2)

def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def test_connection() -> bool:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Conexión a PostgreSQL exitosa")
        return True
    except Exception as e:
        logger.error(f"Error conectando a PostgreSQL: {e}")
        return False
