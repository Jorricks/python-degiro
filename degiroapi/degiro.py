import datetime
import json
from typing import List, Mapping, Optional, Tuple, Union

import requests

from degiroapi.client_info import ClientInfo
from degiroapi.data_type import DataType
from degiroapi.exceptions import DeGiroRequiresTOTP
from degiroapi.interval_type import IntervalType
from degiroapi.order_type import OrderType


class DeGiro:
    """Class for executing API requests against DeGiro"""

    __LOGIN_URL = "https://trader.degiro.nl/login/secure/login"
    __LOGIN_URL_TOTP = "https://trader.degiro.nl/login/secure/login/totp"
    __CONFIG_URL = "https://trader.degiro.nl/login/secure/config"

    __LOGOUT_URL = "https://trader.degiro.nl/trading/secure/logout"

    __CLIENT_INFO_URL = "https://trader.degiro.nl/pa/secure/client"

    __GET_STOCKS_URL = "https://trader.degiro.nl/products_s/secure/v5/stocks"
    __PRODUCT_SEARCH_URL = "https://trader.degiro.nl/product_search/secure/v5/products/lookup"
    __PRODUCT_INFO_URL = "https://trader.degiro.nl/product_search/secure/v5/products/info"
    __TRANSACTIONS_URL = "https://trader.degiro.nl/reporting/secure/v4/transactions"
    __ORDERS_URL = "https://trader.degiro.nl/reporting/secure/v4/order-history"
    __ACCOUNT_URL = "https://trader.degiro.nl/reporting/secure/v6/accountoverview"

    __PLACE_ORDER_URL = "https://trader.degiro.nl/trading/secure/v5/checkOrder"
    __ORDER_URL = "https://trader.degiro.nl/trading/secure/v5/order/"
    __DIVIDENDS_URL = "https://trader.degiro.nl/reporting/secure/v3/ca/"

    __DATA_URL = "https://trader.degiro.nl/trading/secure/v5/update/"
    __PRICE_DATA_URL = "https://charting.vwdservices.com/hchart/v1/deGiro/data.js"

    __GET_REQUEST = 0
    __POST_REQUEST = 1
    __DELETE_REQUEST = 2
    __PUT_REQUEST = 3

    def __init__(self):
        self.session = requests.Session()
        self.client_token: Optional[str] = None
        self.session_id: Optional[str] = None
        self.client_info: Optional[ClientInfo] = None

    def login(self, username: str, password: str, totp: Optional[str] = None) -> Mapping:
        login_payload = {
            "username": username,
            "password": password,
            "isPassCodeReset": False,
            "isRedirectToMobile": False,
        }
        if totp:
            login_payload["oneTimePassword"] = totp

        try:
            login_response = self.__request(
                DeGiro.__LOGIN_URL_TOTP if totp else DeGiro.__LOGIN_URL,
                None,
                login_payload,
                request_type=DeGiro.__POST_REQUEST,
                error_message="Could not login.",
            )
        except Exception as exc:
            if "totpNeeded" in str(exc):
                raise DeGiroRequiresTOTP("You need to enter a Time-based One-time Password with the login credentials.")
            raise exc

        self.session_id = login_response["sessionId"]  # type: ignore
        client_info_payload = {"sessionId": self.session_id}
        client_info_response = self.__request(
            DeGiro.__CLIENT_INFO_URL, None, client_info_payload, error_message="Could not get client info."
        )
        self.client_info = ClientInfo(client_info_response["data"])  # type: ignore

        cookie = {"JSESSIONID": self.session_id}

        client_token_response = self.__request(
            DeGiro.__CONFIG_URL,
            cookie=cookie,
            request_type=DeGiro.__GET_REQUEST,
            error_message="Could not get client config.",
        )
        self.client_token = client_token_response["data"]["clientId"]  # type: ignore

        return client_info_response  # type: ignore

    def logout(self) -> None:
        logout_payload = {
            "intAccount": self.client_info.account_id,
            "sessionId": self.session_id,
        }
        self.__request(
            DeGiro.__LOGOUT_URL + ";jsessionid=" + self.session_id,
            None,
            logout_payload,
            error_message="Could not log out",
        )

    def __request(
        self,
        url: str,
        cookie: Optional[Mapping] = None,
        payload: Optional[Union[Mapping, List[Tuple], bytes]] = None,
        headers: Optional[Mapping] = None,
        data: Optional[Union[Mapping, List[Tuple], bytes, str]] = None,
        post_params: Optional[Union[Mapping, List[Tuple], bytes]] = None,
        request_type: int = __GET_REQUEST,
        error_message: str = "An error occurred.",
    ) -> Union[Mapping, List]:

        if request_type == DeGiro.__DELETE_REQUEST:
            response = self.session.delete(url, json=payload)
        elif request_type == DeGiro.__GET_REQUEST and cookie:
            response = self.session.get(url, cookies=cookie)
        elif request_type == DeGiro.__GET_REQUEST:
            response = self.session.get(url, params=payload)
        elif request_type == DeGiro.__POST_REQUEST and headers and data:
            response = self.session.post(url, headers=headers, params=payload, data=data)
        elif request_type == DeGiro.__POST_REQUEST and post_params:
            response = self.session.post(url, params=post_params, json=payload)
        elif request_type == DeGiro.__POST_REQUEST:
            response = self.session.post(url, json=payload)
        elif request_type == DeGiro.__PUT_REQUEST:
            response = self.session.put(url, params=post_params, json=payload)
        else:
            raise ValueError(f"Unknown request type: {request_type}")

        if response.status_code == 200 or response.status_code == 201:
            try:
                return response.json()
            except Exception:
                raise ValueError("No data was returned.")
        else:
            raise Exception(f"{error_message} Response: {response.text}")

    def account_overview(self, from_date: datetime.datetime, to_date: datetime.datetime) -> Union[List, Mapping]:
        account_payload = {
            "fromDate": from_date.strftime("%d/%m/%Y"),
            "toDate": to_date.strftime("%d/%m/%Y"),
            "intAccount": self.client_info.account_id,
            "sessionId": self.session_id,
        }
        return self.__request(  # type: ignore
            DeGiro.__ACCOUNT_URL, None, account_payload, error_message="Could not get account overview."
        )["data"]

    def get_exchange_rate(self, exchange):
        exchange_ids = {
            "EUR/USD": "705366",
            "EUR/GBP": "714324",
            "EUR/CHF": "714322",
            "EUR/JPY": "1316472",
            "GBP/USD": "1788982",
        }
        last_rate = self.real_time_price(exchange_ids[exchange], interval=IntervalType.One_Day)[0]["data"]["lastPrice"]
        return last_rate

    def search_products(self, search_text: str, limit: int = 1) -> List[Mapping]:
        product_search_payload = {
            "searchText": search_text,
            "limit": limit,
            "offset": 0,
            "intAccount": self.client_info.account_id,
            "sessionId": self.session_id,
        }
        return self.__request(  # type: ignore
            DeGiro.__PRODUCT_SEARCH_URL, None, product_search_payload, error_message="Could not get products."
        )["products"]

    def product_info(self, product_id: int) -> Mapping:
        product_info_payload = {"intAccount": self.client_info.account_id, "sessionId": self.session_id}
        return self.__request(  # type: ignore
            DeGiro.__PRODUCT_INFO_URL,
            None,
            product_info_payload,
            headers={"content-type": "application/json"},
            data=json.dumps([str(product_id)]),
            request_type=DeGiro.__POST_REQUEST,
            error_message="Could not get product info.",
        )["data"][str(product_id)]

    def transactions(
        self, from_date: datetime.datetime, to_date: datetime.datetime, group_transactions: bool = False
    ) -> List[Mapping]:
        transactions_payload = {
            "fromDate": from_date.strftime("%d/%m/%Y"),
            "toDate": to_date.strftime("%d/%m/%Y"),
            "group_transactions_by_order": group_transactions,
            "intAccount": self.client_info.account_id,
            "sessionId": self.session_id,
        }
        return self.__request(  # type: ignore
            DeGiro.__TRANSACTIONS_URL, None, transactions_payload, error_message="Could not get transactions."
        )["data"]

    def orders(
        self, from_date: datetime.datetime, to_date: datetime.datetime, not_executed: bool = False
    ) -> List[Mapping]:
        orders_payload = {
            "fromDate": from_date.strftime("%d/%m/%Y"),
            "toDate": to_date.strftime("%d/%m/%Y"),
            "intAccount": self.client_info.account_id,
            "sessionId": self.session_id,
        }
        # max 90 days
        if (to_date - from_date).days > 90:
            raise Exception("The maximum timespan is 90 days")
        data = self.__request(DeGiro.__ORDERS_URL, None, orders_payload, error_message="Could not get orders.")[
            "data"
        ]  # type: ignore
        data_not_executed = []
        if not_executed:
            for d in data:
                if d["isActive"]:
                    data_not_executed.append(d)
            return data_not_executed
        else:
            return data

    def delete_order(self, order_id: str) -> Union[Mapping, List, str]:
        delete_order_params = {
            "intAccount": self.client_info.account_id,
            "sessionId": self.session_id,
        }

        return self.__request(
            DeGiro.__ORDER_URL + order_id + ";jsessionid=" + self.session_id,
            None,
            delete_order_params,
            request_type=DeGiro.__DELETE_REQUEST,
            error_message="Could not delete order" + " " + order_id,
        )

    @staticmethod
    def filter_cash_funds(cash_funds: Mapping) -> List[Mapping]:
        data = []
        for item in cash_funds["cashFunds"]["value"]:
            if item["value"][2]["value"] != 0:
                data.append(item["value"][1]["value"] + " " + str(item["value"][2]["value"]))
        return data

    @staticmethod
    def filter_portfolio(portfolio: Mapping, filter_zero: bool = False) -> List[Mapping]:
        data: List[Mapping] = []
        for item in portfolio["portfolio"]["value"]:
            position_type = size = price = value = break_even_price = None
            for i in item["value"]:
                size = i["value"] if i["name"] == "size" else size
                position_type = i["value"] if i["name"] == "positionType" else position_type
                price = i["value"] if i["name"] == "price" else price
                value = i["value"] if i["name"] == "value" else value
                break_even_price = i["value"] if i["name"] == "breakEvenPrice" else break_even_price
            data.append(
                {
                    "id": item["id"],
                    "positionType": position_type,
                    "size": size,
                    "price": price,
                    "value": value,
                    "breakEvenPrice": break_even_price,
                }
            )
        if filter_zero:
            data_non_zero: List[Mapping] = []
            for d in data:
                if d["size"] != 0.0:
                    data_non_zero.append(d)
            return data_non_zero
        else:
            return data

    def get_data(self, datatype: str, filter_zero: bool = False) -> List[Mapping]:
        data_payload = {datatype: 0}

        if datatype == DataType.CASH_FUNDS:
            return self.filter_cash_funds(
                self.__request(  # type: ignore
                    DeGiro.__DATA_URL + str(self.client_info.account_id) + ";jsessionid=" + self.session_id,
                    None,
                    data_payload,
                    error_message="Could not get data",
                )
            )
        elif datatype == DataType.PORTFOLIO:
            return self.filter_portfolio(
                self.__request(  # type: ignore
                    DeGiro.__DATA_URL + str(self.client_info.account_id) + ";jsessionid=" + self.session_id,
                    None,
                    data_payload,
                    error_message="Could not get data",
                ),
                filter_zero,
            )
        else:
            return self.__request(
                DeGiro.__DATA_URL + str(self.client_info.account_id) + ";jsessionid=" + self.session_id,
                None,
                data_payload,
                error_message="Could not get data",
            )  # type: ignore

    def real_time_price(self, product_id: int, interval: str):
        product_info = self.product_info(product_id)

        vw_id = product_info["vwdId"]
        vw_id_type = product_info["vwdIdentifierType"]

        price_payload = {
            "requestid": 1,
            "period": interval,
            "series": [vw_id_type + ":" + vw_id, "price:" + vw_id_type + ":" + vw_id],
            "userToken": self.client_token,
        }

        return self.__request(  # type: ignore
            DeGiro.__PRICE_DATA_URL, None, price_payload, error_message="Could not get real time price"
        )["series"]

    def buy_order(
        self,
        order_type: int,
        product_id: str,
        time_type: int,
        size: int,
        limit: Optional[Union[int, float]] = None,
        stop_loss: Optional[Union[int, float]] = None,
    ) -> str:
        return self.__place_order(
            "BUY",
            order_type=order_type,
            product_id=product_id,
            time_type=time_type,
            size=size,
            limit=limit,
            stop_loss=stop_loss,
        )

    def sell_order(
        self,
        order_type: int,
        product_id: str,
        time_type: int,
        size: int,
        limit: Optional[Union[int, float]] = None,
        stop_loss: Optional[Union[int, float]] = None,
    ) -> str:
        return self.__place_order(
            "SELL",
            order_type=order_type,
            product_id=product_id,
            time_type=time_type,
            size=size,
            limit=limit,
            stop_loss=stop_loss,
        )

    def __place_order(
        self,
        buy_sell: str,
        order_type: int,
        product_id: str,
        time_type: int,
        size: int,
        limit: Optional[Union[int, float]],
        stop_loss: Optional[Union[int, float]],
    ) -> str:
        if buy_sell not in (
            "SELL",
            "BUY",
        ):
            raise ValueError("Parameter buy_sell should either be 'SELL' or 'BUY'")

        place_order_params = {
            "intAccount": self.client_info.account_id,
            "sessionId": self.session_id,
        }
        place_order_payload = {
            "buySell": buy_sell,
            "orderType": order_type,
            "productId": product_id,
            "timeType": time_type,
            "size": size,
            "price": limit,
            "stopPrice": stop_loss,
        }
        if (
            order_type != OrderType.STOP_LIMIT
            and order_type != OrderType.MARKET
            and order_type != OrderType.LIMIT
            and order_type != OrderType.STOP_LOSS
        ):
            raise Exception("Invalid order type")

        if time_type != 1 and time_type != 3:
            raise Exception("Invalid time type")

        place_check_order_response = self.__request(
            DeGiro.__PLACE_ORDER_URL + ";jsessionid=" + self.session_id,
            None,
            place_order_payload,
            place_order_params,
            request_type=DeGiro.__POST_REQUEST,
            error_message="Could not place order",
        )

        confirmation_id = place_check_order_response["data"]["confirmationId"]  # type: ignore

        self.__request(
            DeGiro.__ORDER_URL + confirmation_id + ";jsessionid=" + self.session_id,
            None,
            place_order_payload,
            place_order_params,
            request_type=DeGiro.__POST_REQUEST,
            error_message="Could not confirm order",
        )
        return confirmation_id

    def modify_order(
        self,
        order_type: int,
        order_id: str,
        product_id: str,
        buy_sell: str,
        time_type: int,
        size: int,
        limit: Optional[Union[int, float]] = None,
    ) -> Mapping:
        if buy_sell not in (
            "SELL",
            "BUY",
        ):
            raise ValueError("Parameter buy_sell should either be 'SELL' or 'BUY'")

        modify_order_params = {
            "intAccount": self.client_info.account_id,
            "sessionId": self.session_id,
        }
        modify_order_payload = {
            "buySell": buy_sell,
            "orderType": order_type,
            "productId": product_id,
            "timeType": time_type,
            "size": size,
        }
        if order_type == OrderType.LIMIT:
            modify_order_payload["price"] = limit
        elif order_type == OrderType.STOP_LOSS:
            modify_order_payload["stopPrice"] = limit

        return self.__request(  # type: ignore
            DeGiro.__ORDER_URL + order_id + ";jsessionid=" + self.session_id,
            None,
            modify_order_payload,
            modify_order_params,
            request_type=DeGiro.__PUT_REQUEST,
            error_message="Could not modify order" + " " + order_id,
        )

    def future_dividends(self) -> List[Mapping]:
        dividends_payload = {"intAccount": self.client_info.account_id, "sessionId": self.session_id}
        return self.__request(  # type: ignore
            DeGiro.__DIVIDENDS_URL + str(self.client_info.account_id),
            None,
            dividends_payload,
            error_message="Could not get future dividends.",
        )["data"]

    def get_stock_list(self, index_id: int, stock_country_id: int) -> List[Mapping]:
        stock_list_params = {
            "indexId": index_id,
            "stockCountryId": stock_country_id,
            "offset": 0,
            "limit": None,
            "requireTotal": "true",
            "sortColumns": "name",
            "sortTypes": "asc",
            "intAccount": self.client_info.account_id,
            "sessionId": self.session_id,
        }
        return self.__request(
            DeGiro.__GET_STOCKS_URL, None, stock_list_params, error_message="Could not get stock list"
        )[
            "products"
        ]  # type: ignore
