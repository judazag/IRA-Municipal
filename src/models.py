from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Numeric,
    Boolean,
    DateTime,
)
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry


Base = declarative_base()


class MunicipioFeatures(Base):
    __tablename__ = 'municipio_features'

    divipola = Column(String(10), primary_key=True, nullable=False)
    municipio = Column(String, nullable=True)
    ira_score = Column(Float, nullable=True)
    ira_level = Column(String(50), nullable=True)

    # Example numerical columns (extend as needed)
    produccion_total_ton = Column(Float, nullable=True)
    area_sembrada_total_ha = Column(Float, nullable=True)
    n_cultivos = Column(Integer, nullable=True)
    rendimiento_promedio = Column(Float, nullable=True)

    # Socioeconomics
    credito_total_cop = Column(Numeric, nullable=True)
    ipm_rural = Column(Float, nullable=True)

    # Geometry (optional)
    geom = Column(Geometry('MULTIPOLYGON', srid=4326), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'divipola': self.divipola,
            'municipio': self.municipio,
            'ira_score': self.ira_score,
            'ira_level': self.ira_level,
        }
