from fastapi.testclient import TestClient


def test_get_club_settings_creates_defaults(
    client: TestClient,
) -> None:
    response = client.get(
        "/club-settings"
    )

    assert response.status_code == 200

    settings = response.json()

    assert settings["setting_key"] == "default"
    assert settings["club_name"] == "CyberClub"
    assert settings["branch"] == "#1"

    assert (
        settings["lottery_ticket_price"]
        == "85.00"
    )


def test_get_club_settings_returns_same_record(
    client: TestClient,
) -> None:
    first_response = client.get(
        "/club-settings"
    )

    second_response = client.get(
        "/club-settings"
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    assert (
        first_response.json()["id"]
        == second_response.json()["id"]
    )


def test_update_club_settings(
    client: TestClient,
) -> None:
    response = client.patch(
        "/club-settings",
        json={
            "club_name": "КиберДом",
            "branch": "1 этаж",
            "lottery_ticket_price": 100,
        },
    )

    assert response.status_code == 200

    settings = response.json()

    assert settings["club_name"] == "КиберДом"
    assert settings["branch"] == "1 этаж"

    assert (
        settings["lottery_ticket_price"]
        == "100.00"
    )


def test_update_club_settings_trims_text(
    client: TestClient,
) -> None:
    response = client.patch(
        "/club-settings",
        json={
            "club_name": "  КиберДом  ",
            "branch": "  Первый этаж  ",
        },
    )

    assert response.status_code == 200

    settings = response.json()

    assert settings["club_name"] == "КиберДом"
    assert settings["branch"] == "Первый этаж"


def test_update_club_settings_rejects_blank_name(
    client: TestClient,
) -> None:
    response = client.patch(
        "/club-settings",
        json={
            "club_name": "   ",
        },
    )

    assert response.status_code == 422

    assert response.json()["detail"] == (
        "Название клуба не может быть пустым."
    )


def test_update_club_settings_writes_action_log(
    client: TestClient,
) -> None:
    update_response = client.patch(
        "/club-settings",
        json={
            "club_name": "КиберДом",
            "branch": "1 этаж",
            "lottery_ticket_price": 95,
        },
    )

    assert update_response.status_code == 200

    settings = update_response.json()

    logs_response = client.get(
        "/action-logs",
        params={
            "event_type": (
                "club_setting_updated"
            ),
            "entity_type": (
                "club_setting"
            ),
        },
    )

    assert logs_response.status_code == 200

    action_logs = logs_response.json()

    assert len(action_logs) == 1

    action_log = action_logs[0]

    assert action_log["entity_id"] == settings["id"]

    assert action_log["message"] == (
        "Изменены настройки клуба."
    )

    details = action_log["details"]

    assert details["before"] == {
        "club_name": "CyberClub",
        "branch": "#1",
        "lottery_ticket_price": "85.00",
    }

    assert details["after"] == {
        "club_name": "КиберДом",
        "branch": "1 этаж",
        "lottery_ticket_price": "95.00",
    }


def test_same_settings_do_not_write_action_log(
    client: TestClient,
) -> None:
    first_response = client.patch(
        "/club-settings",
        json={
            "club_name": "CyberClub",
            "branch": "#1",
            "lottery_ticket_price": 85,
        },
    )

    assert first_response.status_code == 200

    logs_response = client.get(
        "/action-logs",
        params={
            "event_type": (
                "club_setting_updated"
            ),
        },
    )

    assert logs_response.status_code == 200
    assert logs_response.json() == []