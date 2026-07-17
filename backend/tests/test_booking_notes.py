from fastapi.testclient import TestClient


def test_get_empty_booking_note(
    client: TestClient,
) -> None:
    response = client.get(
        "/booking-notes/2026-07-17"
    )

    assert response.status_code == 200

    booking_note = response.json()

    assert booking_note["booking_date"] == (
        "2026-07-17"
    )

    assert booking_note["content"] == ""


def test_save_and_get_booking_note(
    client: TestClient,
) -> None:
    save_response = client.put(
        "/booking-notes/2026-07-17",
        json={
            "content": "30-34 22:00",
        },
    )

    assert save_response.status_code == 200

    saved_booking_note = (
        save_response.json()
    )

    assert saved_booking_note["content"] == (
        "30-34 22:00"
    )

    get_response = client.get(
        "/booking-notes/2026-07-17"
    )

    assert get_response.status_code == 200

    loaded_booking_note = (
        get_response.json()
    )

    assert loaded_booking_note["id"] == (
        saved_booking_note["id"]
    )

    assert loaded_booking_note["content"] == (
        "30-34 22:00"
    )


def test_update_existing_booking_note(
    client: TestClient,
) -> None:
    first_response = client.put(
        "/booking-notes/2026-07-17",
        json={
            "content": "30-34 22:00",
        },
    )

    assert first_response.status_code == 200

    first_booking_note = (
        first_response.json()
    )

    second_response = client.put(
        "/booking-notes/2026-07-17",
        json={
            "content": (
                "30-34 22:00\n"
                "15-18 19:30"
            ),
        },
    )

    assert second_response.status_code == 200

    second_booking_note = (
        second_response.json()
    )

    assert second_booking_note["id"] == (
        first_booking_note["id"]
    )

    assert second_booking_note["content"] == (
        "30-34 22:00\n"
        "15-18 19:30"
    )


def test_booking_dates_are_independent(
    client: TestClient,
) -> None:
    first_response = client.put(
        "/booking-notes/2026-07-17",
        json={
            "content": "30-34 22:00",
        },
    )

    assert first_response.status_code == 200

    second_response = client.put(
        "/booking-notes/2026-07-18",
        json={
            "content": "1-5 18:00",
        },
    )

    assert second_response.status_code == 200

    first_note_response = client.get(
        "/booking-notes/2026-07-17"
    )

    second_note_response = client.get(
        "/booking-notes/2026-07-18"
    )

    assert first_note_response.json()[
        "content"
    ] == "30-34 22:00"

    assert second_note_response.json()[
        "content"
    ] == "1-5 18:00"


def test_booking_note_content_limit(
    client: TestClient,
) -> None:
    response = client.put(
        "/booking-notes/2026-07-17",
        json={
            "content": "x" * 20001,
        },
    )

    assert response.status_code == 422
