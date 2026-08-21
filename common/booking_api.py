"""Restful-Booker 业务接口层，测试和压测脚本均通过此层调用。"""

from __future__ import annotations

from typing import Any, Protocol


class RequestClient(Protocol):
    def request(self, method: str, path: str, **kwargs: Any) -> Any: ...


class BookingApi:
    def __init__(self, client: RequestClient) -> None:
        self.client = client

    def health_check(self) -> Any:
        return self.client.request("GET", "/ping")

    def get_booking_ids(self, **params: str) -> Any:
        return self.client.request("GET", "/booking", params=params)

    def get_booking(self, booking_id: int) -> Any:
        return self.client.request("GET", f"/booking/{booking_id}")

    def create_booking(self, payload: dict[str, Any]) -> Any:
        return self.client.request("POST", "/booking", json=payload)

    def create_token(self, username: str, password: str) -> Any:
        return self.client.request("POST", "/auth", json={"username": username, "password": password})

    def update_booking(self, booking_id: int, payload: dict[str, Any], token: str | None = None) -> Any:
        return self.client.request("PUT", f"/booking/{booking_id}", json=payload, headers=self._auth(token))

    def partial_update_booking(self, booking_id: int, payload: dict[str, Any], token: str | None = None) -> Any:
        return self.client.request("PATCH", f"/booking/{booking_id}", json=payload, headers=self._auth(token))

    def delete_booking(self, booking_id: int, token: str | None = None) -> Any:
        return self.client.request("DELETE", f"/booking/{booking_id}", headers=self._auth(token))

    @staticmethod
    def _auth(token: str | None) -> dict[str, str]:
        return {"Cookie": f"token={token}"} if token else {}
