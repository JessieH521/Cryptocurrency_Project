from constants import COINMARKET_API
from requests import Session, Timeout, TooManyRedirects
import requests  
import json

API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

# 1. 从 CoinMarketCap API 获取指定加密货币（默认为 "BTC" 比特币）的最新数据
def get_latest_coin_data(target_symbol="BTC"):

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
        response.raise_for_status()  # 检查 HTTP 状态码（非 200 会报错）
        return response.json().get("data", {}).get(target_symbol, None)               
    except (ConnectionError, Timeout, TooManyRedirects, json.JSONDecodeError) as e:
        print(f"API request failed:{e}")
        return None