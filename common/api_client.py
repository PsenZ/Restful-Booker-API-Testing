"""requests 的轻量封装：复用会话、统一 URL/请求头、超时和异常。"""

from __future__ import annotations

from typing import Any

import requests


class ApiRequestError(RuntimeError):
    """网络或请求层异常，保留原始错误便于排查。"""


class ApiClient:
    def __init__(self, base_url: str, timeout: float = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        """向相对路径发请求；所有调用默认带统一超时与 JSON 请求头。"""
        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = {"Content-Type": "application/json", **kwargs.pop("headers", {})}
        try:
            return self.session.request(
                method=method,
                url=url,
                headers=headers,
                timeout=kwargs.pop("timeout", self.timeout),
                **kwargs,
            )
        except requests.RequestException as exc:
            raise ApiRequestError(f"{method.upper()} {url} 请求失败: {exc}") from exc

    def close(self) -> None:
        self.session.close()
