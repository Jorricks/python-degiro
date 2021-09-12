from typing import Mapping


class ClientInfo:
    """Data Class for the user currently authenticated with DeGiro."""

    def __init__(self, client_info: Mapping):
        self.__account_id: str = client_info["intAccount"]
        self.__username: str = client_info["username"]
        self.__first_name: str = client_info["firstContact"]["firstName"]
        self.__last_name: str = client_info["firstContact"]["lastName"]
        self.__email: str = client_info["email"]

    @property
    def account_id(self) -> str:
        return self.__account_id

    @property
    def username(self) -> str:
        return self.__username

    @property
    def first_name(self) -> str:
        return self.__first_name

    @property
    def last_name(self) -> str:
        return self.__last_name

    @property
    def email(self) -> str:
        return self.__email
