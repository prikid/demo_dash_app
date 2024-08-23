from typing import Literal

import requests


class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def _make_request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}/{endpoint}"
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, **kwargs):
        return self._make_request("POST", endpoint ** kwargs)

    def get(self, endpoint: str, **kwargs):
        return self._make_request("GET", endpoint, **kwargs)
