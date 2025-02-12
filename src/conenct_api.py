from constants import COINMARKET_API
from requests import Session, Timeout, TooManyRedirects  
import json

def get_latest_coin_data(target_symbol="BTC"):
    API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

    parameters = {"symbol": target_symbol, "convert": "USD"}
    # 发送请求时的参数：传入的加密货币符号（如 "BTC"），返回的数据中包含以美元（USD）计价的信息。

    headers = {
        "Accepts": "application/json",       
        "X-CMC_PRO_API_KEY": COINMARKET_API,
    }

    session = Session()
    session.headers.update(headers)      # 发送 HTTP 请求， 将请求头添加到会话中。

    try:
        response = session.get(API_URL, params=parameters)    # 发送 HTTP GET 请求
        return json.loads(response.text).get("data", {}).get(target_symbol, {})                  # 将返回的 JSON 转换为 Python 字典
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

    response = session.get(API_URL, params=parameters)    # 发送 GET 请求到 CoinMarketCap API，并返回响应。
    return json.loads(response.text)["data"][target_symbol]   # 返回 从 JSON 响应中提取出指定加密货币的数据（例如 "BTC"）



