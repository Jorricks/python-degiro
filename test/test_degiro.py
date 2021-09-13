import json
from unittest.mock import MagicMock, patch

import pytest
import requests as requests

from degiroapi.degiro import DeGiro
from degiroapi.exceptions import DeGiroRequiresTOTP


@patch.object(requests.Session, "post")
@patch.object(requests.Session, "get")
def test_login(patched_get: MagicMock, patched_post: MagicMock):
    patched_post.return_value.status_code = 200
    patched_post.return_value.json = lambda *args, **kwargs: {"sessionId": "abc"}
    patched_get.return_value.status_code = 200
    patched_get.json.return_value = {"hallo": 123}
    # request_post.return_value = request_response_mock
    DeGiro().login(username="abc", password="def", totp=123456)

    patched_post.assert_called_with(
        "https://trader.degiro.nl/login/secure/login/totp",
        json={
            "username": "abc",
            "password": "def",
            "isPassCodeReset": False,
            "isRedirectToMobile": False,
            "oneTimePassword": 123456,
        },
    )
    patched_get.assert_called_with("https://trader.degiro.nl/login/secure/config", cookies={"JSESSIONID": "abc"})


@patch.object(requests.Session, "post")
@patch.object(requests.Session, "get")
def test_login_requires_totp(patched_get: MagicMock, patched_post: MagicMock):
    patched_post.return_value.status_code = 500
    patched_post.return_value.text = json.dumps({"error": "totpNeeded"})
    with pytest.raises(DeGiroRequiresTOTP):
        DeGiro().login(username="abc", password="def")

    patched_post.assert_called_with(
        "https://trader.degiro.nl/login/secure/login",
        json={
            "username": "abc",
            "password": "def",
            "isPassCodeReset": False,
            "isRedirectToMobile": False,
        },
    )
    patched_get.assert_not_called()
