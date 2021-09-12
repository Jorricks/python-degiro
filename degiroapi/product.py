import datetime
from typing import Mapping


class Product:
    """A data class for a stock/product of DeGiro."""

    def __init__(self, product: Mapping[str, str]):
        self.__id = product["id"]
        self.__name = product["name"]
        self.__isin = product["isin"]
        self.__symbol = product["symbol"]
        self.__currency = product["currency"]
        self.__product_type = product["productTypeId"]
        self.__tradable = product["tradable"]
        self.__close_price = product["closePrice"]
        self.__close_price_date = datetime.datetime.strptime(product["closePriceDate"], "%Y-%m-%d").date()

    @property
    def id(self) -> str:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def isin(self) -> str:
        return self.__isin

    @property
    def symbol(self) -> str:
        return self.__symbol

    @property
    def currency(self) -> str:
        return self.__currency

    @property
    def product_type(self) -> str:
        return self.__product_type

    @property
    def tradable(self) -> str:
        return self.__tradable

    @property
    def close_price(self) -> str:
        return self.__close_price

    @property
    def close_price_date(self) -> datetime.date:
        return self.__close_price_date
