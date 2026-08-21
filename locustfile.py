"""小规模压测：locust -f locustfile.py --headless -u 50 -r 5 -t 2m --html reports/locust-report.html"""

from __future__ import annotations

from typing import Any

from locust import HttpUser, between, task

from common.booking_api import BookingApi
from config.settings import settings


class LocustRequestClient:
    """将 Locust HttpSession 适配成与 requests 封装一致的 request 接口。"""

    def __init__(self, user: HttpUser) -> None:
        self.user = user

    def request(self, method: str, path: str, **kwargs: Any) -> Any:
        headers = {"Content-Type": "application/json", "Accept": "application/json", **kwargs.pop("headers", {})}
        return self.user.client.request(
            method,
            path,
            headers=headers,
            name=f"{method} {path}",
            catch_response=True,
            **kwargs,
        )


class BookerLoadTestUser(HttpUser):
    host = settings.base_url
    wait_time = between(0.2, 1.0)

    def on_start(self) -> None:
        self.booking_api = BookingApi(LocustRequestClient(self))

    @task(6)
    def list_bookings(self) -> None:
        with self.booking_api.get_booking_ids() as response:
            if response.status_code != 200:
                response.failure(f"预期 200，实际 {response.status_code}")

    @task(3)
    def health_check(self) -> None:
        with self.booking_api.health_check() as response:
            if response.status_code != 201:
                response.failure(f"预期 201，实际 {response.status_code}")

    @task(1)
    def create_booking(self) -> None:
        payload = {
            "firstname": "Load", "lastname": "Tester", "totalprice": 100,
            "depositpaid": True, "bookingdates": {"checkin": "2026-09-01", "checkout": "2026-09-02"},
            "additionalneeds": "None",
        }
        with self.booking_api.create_booking(payload) as response:
            if response.status_code != 200:
                response.failure(f"预期 200，实际 {response.status_code}")
