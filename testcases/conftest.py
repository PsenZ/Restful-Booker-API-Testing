from __future__ import annotations

import copy
from collections.abc import Generator

import pytest

from common.api_client import ApiClient
from common.booking_api import BookingApi
from config.settings import settings


@pytest.fixture(scope="session")
def api_client() -> Generator[ApiClient, None, None]:
    client = ApiClient(settings.base_url, settings.timeout)
    yield client
    client.close()


@pytest.fixture(scope="session")
def booking_api(api_client: ApiClient) -> BookingApi:
    return BookingApi(api_client)


@pytest.fixture(scope="session")
def auth_token(booking_api: BookingApi) -> str:
    response = booking_api.create_token(settings.username, settings.password)
    assert response.status_code == 200, f"获取 token 失败: {response.text}"
    token = response.json().get("token")
    assert token, f"未获得 token: {response.text}"
    return token


@pytest.fixture
def booking_payload() -> dict:
    return {
        "firstname": "Auto",
        "lastname": "Tester",
        "totalprice": 188,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-09-01", "checkout": "2026-09-08"},
        "additionalneeds": "Breakfast",
    }


@pytest.fixture
def created_booking(booking_api: BookingApi, auth_token: str, booking_payload: dict) -> Generator[int, None, None]:
    response = booking_api.create_booking(copy.deepcopy(booking_payload))
    assert response.status_code == 200, f"测试数据创建失败: {response.text}"
    booking_id = response.json()["bookingid"]
    yield booking_id
    booking_api.delete_booking(booking_id, auth_token)
