from sqlmodel import SQLModel, create_engine, Session
from core.settings import settings

def _build_database_url() -> str:
    return (
        f"mysql+pymysql://{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )

DATABASE_URL = _build_database_url()
engine = create_engine(DATABASE_URL, echo=False)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()
