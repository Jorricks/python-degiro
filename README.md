# DegiroAPI

An unofficial API for the trading platform Degiro written in Python with the ability to get real time data and historical data for products.

## Credits

This project is a fork from [DegiroAPI](https://github.com/lolokraus/DegiroAPI) by [lolokrauz](https://github.com/lolokraus).
It was not actively maintained anymore, hence the creation of this repository.

## Added changes

Over the original repository the following things were added:
- Pre-commit hooks.
- Style and type checking.
- Dependencies handled by the setup instead of the user.
- Typing information all over the code.
- Removed logic from `__init__`.
- Renaming of function, parameters and variables to adhere to pythons snake_case.

## Getting Started

### Installing

``` python
pip install degiroapi
```

### Logging in

``` python
frmo degiroapi.degiro import DeGiro
degiro = DeGiro()
degiro.login("username", "password")
```

### Logging out

``` python
degiro.logout()
```

## Available Functions

* login
* logout
* get_data
* search_products
* product_info
* transactions
* orders
* delete_order
* real_time_price
* get_stock_list
* buy_order
* sell_order

## get_data

Printing your current cash funds:

``` python
from degiroapi.data_type import DataType
cashfunds = degiro.get_data(DataType.CASHFUNDS)
for data in cashfunds:
    print(data)
```

Printing your current portfolio, argument True to filter out products with a size of 0, False or no Argument to show all:

``` python
from degiroapi.data_type import DataType
portfolio = degiro.get_data(DataType.PORTFOLIO, True)
for data in portfolio:
    print(data)
```

## search_products

Searching for a product:

``` python
products = degiro.search_products('Pfizer')
print(Product(products[0]).id)
```

## product_info

Printing info for a specified product ID:

``` python
info = degiro.product_info(331823)
print(info["id"], info["name"], info["currency"], info["closePrice"])
```

## transactions

Printing your transactions in a given time interval:

``` python
from datetime import datetime, timedelta

transactions = degiro.transactions(datetime(2019, 1, 1), datetime.now())
print(pretty_json(transactions))
```

## orders

Printing your order history(the maximum timespan is 90 days)
With argument True, this function only returns open orders

``` python
from datetime import datetime, timedelta

orders = degiro.orders(datetime.now() - timedelta(days=90), datetime.now())
print(pretty_json(orders))

orders = degiro.orders(datetime.now() - timedelta(days=90), datetime.now(), True)
print(pretty_json(orders))
```

## delete_order

Deleting an open order with the orderId

``` python
orders = degiro.orders(datetime.now() - timedelta(days=1), datetime.now(), True)
degiro.delete_order(orders[0]['orderId'])
```

``` python
degiro.delete_order("f278d56f-eaa0-4dc7-b067-45c6b4b3d74f")
```

## real_time_price

Get the real time price and the historical data of a stock:

``` python
from degiro.interval_type import IntervalType

products = degiro.search_products('nrz')
# Interval can be set to One_Day, One_Week, One_Month, Three_Months, Six_Months, One_Year, Three_Years, Five_Years, Max
realprice = degiro.real_time_price(Product(products[0]).id, IntervalType.One_Day)

# getting the real time price
print(realprice[0]['data']['lastPrice'])
print(pretty_json(realprice[0]['data']))

# getting historical data
print(realprice[1]['data'])
```

## get_stock_list

Get the symbols of the S&P500 stocks:

``` python
sp5symbols = []
products = degiro.get_stock_list(14, 846)
for product in products:
    sp5symbols.append(Product(product).symbol)
```

Get the symbols of the german30 stocks:

``` python
daxsymbols = []
products = degiro.get_stock_list(6, 906)
for product in products:
    daxsymbols.append(Product(product).symbol)
```

## buy_order

Placing a buy order is dependent on the order Type:

### Limit order

You have to set a limit order price to which the order gets executed.
**arguments**: order type, product id, execution time type (either 1 for "valid on a daily basis", or 3 for unlimited, size, limit(the limit price)

``` python
from degiroapi.order_type import OrderType
degiro.buy_order(OrderType.LIMIT, Product(products[0]).id, 3, 1, 30)
```

### StopLimit order

Sets a limit order when the stoploss price is reached (not bought for more than the limit at the stop loss price):
**arguments**: order type, product id, execution time type (either 1 for "valid on a daily basis", or 3 for "unlimited"), size, limit(the limit price), stop_loss(stop loss price)

``` python
from degiroapi.order_type import OrderType
degiro.buy_order(OrderType.STOPLIMIT, Product(products[0]).id, 3, 1, 38, 38)
```

### Market order

Bought at the market price:
**arguments**: order type, product id, execution time type (either 1 for "valid on a daily basis", or 3 for "unlimited"), size

``` python
from degiroapi.order_type import OrderType
degiro.buy_order(OrderType.MARKET, Product(products[0]).id, 3, 1)
```

### StopLoss order

The stop loss price has to be higher than the current price, when current price reaches the stoploss price the order is placed:
**arguments**: order type, product id, execution time type (either 1 for "valid on a daily basis", or 3 for "unlimited"), size

``` python
from degiroapi.order_type import OrderType
degiro.buy_order(OrderType.STOPLOSS, Product(products[0]).id, 3, 1, None, 38)
```

## sell_order

Placing a sell order is dependent on the order Type:
Equivalent to the buy orders:

``` python
from degiroapi.order_type import OrderType
degiro.sell_order(OrderType.LIMIT, Product(products[0]).id, 3, 1, 40)
```

``` python
from degiroapi.order_type import OrderType
degiro.sell_order(OrderType.STOPLIMIT, Product(products[0]).id, 3, 1, 37, 38)
```

``` python
from degiroapi.order_type import OrderType
degiro.sell_order(OrderType.MARKET, Product(products[0]).id, 3, 1)
```

``` python
from degiroapi.order_type import OrderType
degiro.sell_order(OrderType.STOPLOSS, Product(products[0]).id, 3, 1, None, 38)
```

## Usage

For documented examples see [examples.py](https://github.com/lolokraus/DegiroAPI/blob/master/examples/examples.py)

## Contributing

How great this project will turn out to be, totally depends on you.
If you think you have a great addition, please create a PR :).
If you are unfamilar with `pull requests`, please take a look [here](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request).

### Requirements
In order for your commit to be accepted, please install pre-commit.
This will run a couple of tools to make sure the formatting of the code is good and there are no obvious mistakes.

### Installing pre-commit
```shell
pre-commit install
```
Now everytime you will commit, it will automatically run the pre-commit hooks.
If you are using Pycharm, the errors appear in `git(left bottom) -> console`.
