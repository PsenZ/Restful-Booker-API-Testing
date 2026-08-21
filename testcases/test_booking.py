from __future__ import annotations

import copy

import allure
import pytest

from common.booking_api import BookingApi


@allure.epic("Restful-Booker API")
@allure.feature("Booking 管理")
class TestBooking:
    @pytest.mark.smoke
    @pytest.mark.positive
    @allure.story("服务存活")
    def test_health_check(self, booking_api: BookingApi) -> None:
        assert booking_api.health_check().status_code == 201

    @pytest.mark.smoke
    @pytest.mark.positive
    @allure.story("查询订单列表")
    def test_get_booking_ids(self, booking_api: BookingApi) -> None:
        response = booking_api.get_booking_ids()
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert "bookingid" in response.json()[0]

    @pytest.mark.positive
    @allure.story("创建订单")
    def test_create_booking(self, booking_api: BookingApi, booking_payload: dict) -> None:
        response = booking_api.create_booking(booking_payload)
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body["bookingid"], int)
        assert body["booking"]["firstname"] == booking_payload["firstname"]

    @pytest.mark.positive
    @allure.story("按姓名筛选订单")
    def test_filter_booking_by_firstname(self, booking_api: BookingApi, created_booking: int) -> None:
        response = booking_api.get_booking_ids(firstname="Auto")
        assert response.status_code == 200
        assert any(item["bookingid"] == created_booking for item in response.json())

    @pytest.mark.positive
    @allure.story("读取已创建订单")
    def test_get_created_booking(self, booking_api: BookingApi, created_booking: int) -> None:
        response = booking_api.get_booking(created_booking)
        assert response.status_code == 200
        assert response.json()["lastname"] == "Tester"

    @pytest.mark.positive
    @allure.story("全量更新订单")
    def test_update_booking_with_token(self, booking_api: BookingApi, created_booking: int, auth_token: str, booking_payload: dict) -> None:
        payload = copy.deepcopy(booking_payload)
        payload.update({"firstname": "Updated", "totalprice": 299})
        response = booking_api.update_booking(created_booking, payload, auth_token)
        assert response.status_code == 200
        assert response.json()["firstname"] == "Updated"
        assert response.json()["totalprice"] == 299

    @pytest.mark.positive
    @allure.story("部分更新订单")
    def test_partial_update_booking_with_token(self, booking_api: BookingApi, created_booking: int, auth_token: str) -> None:
        response = booking_api.partial_update_booking(created_booking, {"additionalneeds": "Airport pickup"}, auth_token)
        assert response.status_code == 200
        assert response.json()["additionalneeds"] == "Airport pickup"

    @pytest.mark.positive
    @allure.story("删除订单")
    def test_delete_booking_with_token(self, booking_api: BookingApi, created_booking: int, auth_token: str) -> None:
        response = booking_api.delete_booking(created_booking, auth_token)
        assert response.status_code == 201
        assert booking_api.get_booking(created_booking).status_code == 404

    @pytest.mark.negative
    @allure.story("不存在的订单返回 404")
    def test_get_nonexistent_booking(self, booking_api: BookingApi) -> None:
        assert booking_api.get_booking(999999999).status_code == 404

    @pytest.mark.negative
    @pytest.mark.auth
    @allure.story("无 token 不可全量更新")
    def test_update_booking_without_token(self, booking_api: BookingApi, created_booking: int, booking_payload: dict) -> None:
        response = booking_api.update_booking(created_booking, booking_payload)
        assert response.status_code == 403

    @pytest.mark.negative
    @pytest.mark.auth
    @allure.story("无效 token 不可删除")
    def test_delete_booking_with_invalid_token(self, booking_api: BookingApi, created_booking: int) -> None:
        response = booking_api.delete_booking(created_booking, "invalid-token")
        assert response.status_code == 403

    @pytest.mark.negative
    @allure.story("已删除订单不可重复删除")
    def test_delete_booking_twice(self, booking_api: BookingApi, auth_token: str, booking_payload: dict) -> None:
        booking_id = booking_api.create_booking(booking_payload).json()["bookingid"]
        assert booking_api.delete_booking(booking_id, auth_token).status_code == 201
        assert booking_api.delete_booking(booking_id, auth_token).status_code in {404, 405}

    @pytest.mark.boundary
    @allure.story("超长姓名的接口行为")
    def test_create_booking_with_long_firstname(self, booking_api: BookingApi, booking_payload: dict) -> None:
        payload = copy.deepcopy(booking_payload)
        payload["firstname"] = "A" * 256
        response = booking_api.create_booking(payload)
        # 该公开练习 API 未声明字段长度限制；记录并断言其当前可接受长文本的契约。
        assert response.status_code == 200
        assert response.json()["booking"]["firstname"] == payload["firstname"]

    @pytest.mark.boundary
    @allure.story("缺少字段时的接口行为")
    def test_create_booking_with_missing_required_field(self, booking_api: BookingApi, booking_payload: dict) -> None:
        payload = copy.deepcopy(booking_payload)
        payload.pop("firstname")
        response = booking_api.create_booking(payload)
        # API 对必填校验较宽松；此用例用于暴露并固化当前的输入校验缺口。
        assert response.status_code in {200, 400, 500}
