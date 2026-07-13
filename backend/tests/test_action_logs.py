from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.action_log import action_log_service


def test_get_action_logs_empty(
    client: TestClient,
) -> None:
    response = client.get(
        "/action-logs",
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_action_logs(
    client: TestClient,
    db_session: Session,
) -> None:
    entity_id = uuid4()

    action_log_service.record(
        db_session,
        event_type="product_created",
        entity_type="product",
        entity_id=entity_id,
        message="Добавлен тестовый товар.",
        details={
            "name": "Lipton Лимон 0,5",
            "price": 130,
        },
    )

    db_session.commit()

    response = client.get(
        "/action-logs",
    )

    assert response.status_code == 200

    action_logs = response.json()

    assert len(action_logs) == 1

    action_log = action_logs[0]

    assert action_log["event_type"] == (
        "product_created"
    )

    assert action_log["entity_type"] == (
        "product"
    )

    assert action_log["entity_id"] == str(
        entity_id
    )

    assert action_log["message"] == (
        "Добавлен тестовый товар."
    )

    assert action_log["details"] == {
        "name": "Lipton Лимон 0,5",
        "price": 130,
    }

    assert action_log["created_at"]


def test_filter_action_logs(
    client: TestClient,
    db_session: Session,
) -> None:
    action_log_service.record(
        db_session,
        event_type="product_created",
        entity_type="product",
        entity_id=uuid4(),
        message="Добавлен товар.",
    )

    action_log_service.record(
        db_session,
        event_type="debt_created",
        entity_type="debt",
        entity_id=uuid4(),
        message="Добавлен долг.",
    )

    action_log_service.record(
        db_session,
        event_type="prize_created",
        entity_type="prize",
        entity_id=uuid4(),
        message="Добавлен приз.",
    )

    db_session.commit()

    response = client.get(
        "/action-logs",
        params={
            "event_type": "debt_created",
            "entity_type": "debt",
        },
    )

    assert response.status_code == 200

    action_logs = response.json()

    assert len(action_logs) == 1

    assert action_logs[0]["event_type"] == (
        "debt_created"
    )

    assert action_logs[0]["entity_type"] == (
        "debt"
    )

    assert action_logs[0]["message"] == (
        "Добавлен долг."
    )