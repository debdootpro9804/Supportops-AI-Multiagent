
import os
from collections.abc import Iterator
from uuid import uuid4

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, insert, inspect, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.db.models import Customer


@pytest.fixture(scope="session")
def test_engine() -> Iterator[Engine]:
    """Connect to the dedicated PostgreSQL test database."""
    load_dotenv()

    database_url = os.getenv("TEST_DATABASE_URL")

    if not database_url:
        pytest.fail(
            "TEST_DATABASE_URL is missing. "
            "Configure a dedicated test database in .env."
        )

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
    )

    try:
        with engine.connect() as connection:
            connection.execute(select(1))
    except SQLAlchemyError as exc:
        engine.dispose()
        pytest.fail(
            f"Could not connect to the test database: {exc}"
        )

    yield engine
    engine.dispose()


def test_migrations_created_expected_tables(
    test_engine: Engine,
) -> None:
    inspector = inspect(test_engine)

    assert inspector.has_table("customers")
    assert inspector.has_table("alembic_version")


def test_customer_can_be_inserted_and_retrieved(
    test_engine: Engine,
) -> None:
    table = Customer.__table__
    email = f"pytest-{uuid4()}@example.test"

    with test_engine.connect() as connection:
        transaction = connection.begin()

        try:
            inserted = connection.execute(
                insert(table)
                .values(email=email)
                .returning(table.c.id, table.c.email)
            ).one()

            retrieved_email = connection.execute(
                select(table.c.email).where(
                    table.c.id == inserted.id
                )
            ).scalar_one()

            assert retrieved_email == email

        finally:
            transaction.rollback()


def test_customer_email_must_be_unique(
    test_engine: Engine,
) -> None:
    table = Customer.__table__
    email = f"duplicate-{uuid4()}@example.test"

    with test_engine.connect() as connection:
        transaction = connection.begin()

        try:
            connection.execute(
                insert(table).values(email=email)
            )

            with pytest.raises(IntegrityError), connection.begin_nested():
                connection.execute(
                    insert(table).values(email=email)
                )

        finally:
            transaction.rollback()
