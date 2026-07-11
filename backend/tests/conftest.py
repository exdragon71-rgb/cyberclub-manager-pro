from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, sessionmaker

import app.models
from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app
from app.models.product import Product


test_database_url = URL.create(
    drivername="postgresql+psycopg2",
    username=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
    database=f"{settings.db_name}_test",
)


test_engine = create_engine(
    test_database_url,
    pool_pre_ping=True,
)


TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


@pytest.fixture(
    scope="session",
    autouse=True,
)
def prepare_test_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(
        bind=test_engine
    )

    Base.metadata.create_all(
        bind=test_engine
    )

    yield

    Base.metadata.drop_all(
        bind=test_engine
    )


@pytest.fixture(
    autouse=True,
)
def clean_test_database() -> Generator[None, None, None]:
    with TestingSessionLocal() as session:
        session.execute(
            delete(Product)
        )
        session.commit()

    yield

    with TestingSessionLocal() as session:
        session.execute(
            delete(Product)
        )
        session.commit()


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(
    db_session: Session,
) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()