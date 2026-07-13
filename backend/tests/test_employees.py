from uuid import uuid4

from fastapi.testclient import TestClient


def create_employee(
    client: TestClient,
    *,
    name: str = "Рома",
) -> dict:
    response = client.post(
        "/employees",
        json={
            "name": name,
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_employee(
    client: TestClient,
) -> None:
    employee = create_employee(client)

    assert employee["name"] == "Рома"
    assert employee["is_active"] is True
    assert "id" in employee
    assert "created_at" in employee
    assert "updated_at" in employee


def test_create_employee_writes_action_log(
    client: TestClient,
) -> None:
    employee = create_employee(
        client,
        name="Рома",
    )

    response = client.get(
        "/action-logs",
        params={
            "event_type": "employee_created",
            "entity_type": "employee",
        },
    )

    assert response.status_code == 200

    action_logs = response.json()

    assert len(action_logs) == 1

    action_log = action_logs[0]

    assert action_log["entity_id"] == employee["id"]

    assert action_log["message"] == (
        "Добавлен сотрудник «Рома»."
    )

    assert action_log["details"] == {
        "name": "Рома",
        "is_active": True,
    }


def test_get_employee_by_id(
    client: TestClient,
) -> None:
    employee = create_employee(client)

    response = client.get(
        f"/employees/{employee['id']}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == employee["id"]
    assert response.json()["name"] == "Рома"


def test_duplicate_employee_name_returns_409(
    client: TestClient,
) -> None:
    create_employee(
        client,
        name="Рома",
    )

    response = client.post(
        "/employees",
        json={
            "name": "  рома  ",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Сотрудник с именем 'рома' уже существует."
    )


def test_update_employee(
    client: TestClient,
) -> None:
    employee = create_employee(client)

    response = client.patch(
        f"/employees/{employee['id']}",
        json={
            "name": "Роман",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Роман"


def test_update_employee_writes_action_log(
    client: TestClient,
) -> None:
    employee = create_employee(
        client,
        name="Рома",
    )

    response = client.patch(
        f"/employees/{employee['id']}",
        json={
            "name": "Роман",
        },
    )

    assert response.status_code == 200

    logs_response = client.get(
        "/action-logs",
        params={
            "event_type": "employee_updated",
            "entity_type": "employee",
        },
    )

    assert logs_response.status_code == 200

    action_logs = logs_response.json()

    assert len(action_logs) == 1

    action_log = action_logs[0]

    assert action_log["entity_id"] == employee["id"]

    assert action_log["message"] == (
        "Изменён сотрудник «Роман»."
    )

    assert (
        action_log["details"]["before"]["name"]
        == "Рома"
    )

    assert (
        action_log["details"]["after"]["name"]
        == "Роман"
    )


def test_archive_and_restore_employee(
    client: TestClient,
) -> None:
    employee = create_employee(client)

    archive_response = client.post(
        f"/employees/{employee['id']}/archive"
    )

    assert archive_response.status_code == 200
    assert archive_response.json()["is_active"] is False

    restore_response = client.post(
        f"/employees/{employee['id']}/restore"
    )

    assert restore_response.status_code == 200
    assert restore_response.json()["is_active"] is True


def test_archive_employee_writes_action_log(
    client: TestClient,
) -> None:
    employee = create_employee(
        client,
        name="Рома",
    )

    response = client.post(
        f"/employees/{employee['id']}/archive"
    )

    assert response.status_code == 200

    logs_response = client.get(
        "/action-logs",
        params={
            "event_type": "employee_archived",
            "entity_type": "employee",
        },
    )

    assert logs_response.status_code == 200

    action_logs = logs_response.json()

    assert len(action_logs) == 1

    action_log = action_logs[0]

    assert action_log["entity_id"] == employee["id"]

    assert action_log["message"] == (
        "Сотрудник «Рома» перенесён в архив."
    )

    assert action_log["details"] == {
        "name": "Рома",
        "is_active": False,
    }


def test_restore_employee_writes_action_log(
    client: TestClient,
) -> None:
    employee = create_employee(
        client,
        name="Рома",
    )

    archive_response = client.post(
        f"/employees/{employee['id']}/archive"
    )

    assert archive_response.status_code == 200

    restore_response = client.post(
        f"/employees/{employee['id']}/restore"
    )

    assert restore_response.status_code == 200

    logs_response = client.get(
        "/action-logs",
        params={
            "event_type": "employee_restored",
            "entity_type": "employee",
        },
    )

    assert logs_response.status_code == 200

    action_logs = logs_response.json()

    assert len(action_logs) == 1

    action_log = action_logs[0]

    assert action_log["entity_id"] == employee["id"]

    assert action_log["message"] == (
        "Сотрудник «Рома» восстановлен из архива."
    )

    assert action_log["details"] == {
        "name": "Рома",
        "is_active": True,
    }


def test_inactive_employees_can_be_included(
    client: TestClient,
) -> None:
    employee = create_employee(client)

    archive_response = client.post(
        f"/employees/{employee['id']}/archive"
    )

    assert archive_response.status_code == 200

    active_response = client.get(
        "/employees"
    )

    assert active_response.status_code == 200
    assert active_response.json() == []

    all_response = client.get(
        "/employees",
        params={
            "include_inactive": True,
        },
    )

    assert all_response.status_code == 200
    assert len(all_response.json()) == 1


def test_unknown_employee_returns_404(
    client: TestClient,
) -> None:
    unknown_employee_id = uuid4()

    response = client.get(
        f"/employees/{unknown_employee_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Сотрудник не найден."
    )