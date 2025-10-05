"""
Configuration de la base de données PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.core.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,
    echo=settings.DEBUG,  
    connect_args={"options": "-c statement_timeout=30000"}  
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency pour obtenir une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Créer toutes les tables (pour les tests)"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Supprimer toutes les tables (pour les tests)"""
    Base.metadata.drop_all(bind=engine)
