import allure
import pytest

from common.booking_api import BookingApi
from config.settings import settings


@allure.epic("Restful-Booker API")
@allure.feature("认证")
class TestAuthentication:
    @pytest.mark.smoke
    @pytest.mark.positive
    @allure.story("正确凭据可获取 token")
    def test_create_token_with_valid_credentials(self, booking_api: BookingApi) -> None:
        response = booking_api.create_token(settings.username, settings.password)
        assert response.status_code == 200
        assert response.json().get("token")

    @pytest.mark.negative
    @allure.story("错误凭据不可获取 token")
    def test_create_token_with_invalid_credentials(self, booking_api: BookingApi) -> None:
        response = booking_api.create_token("invalid-user", "invalid-password")
        assert response.status_code == 200
        assert "token" not in response.json()
        assert response.json().get("reason") == "Bad credentials"
