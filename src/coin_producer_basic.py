import time
from quixstreams import Application   # 流式数据处理的库，处理 Kafka 消息的对象，负责从 Kafka 中获取数据和发布数据。
from constants import COINMARKET_API
from requests import Session, Timeout, TooManyRedirects  
# requests 库 提供的一种 会话管理（Session） 方式，用于在多个 HTTP 请求之间保持连接。
import json
from pprint import pprint

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

# 2.创建了一个 Quix Streams 的应用实例，创建了一个名为 coins 的 Kafka 主题，输出JSON，连接到本地的 Kafka 服务，
def main():
    app = Application(broker_address="localhost:9092", consumer_group="coin_group")
    coins_topic = app.topic(name="coins", value_serializer="json")

    # 3. # 获取 Kafka 生产者对象 producer，负责向 Kafka 主题发送消息。
    with app.get_producer() as producer:
        while True:
            coin_latest = get_latest_coin_data("BTC")

            # 4. 将获取到的数据序列化为 Kafka 消息
            kafka_message = coins_topic.serialize(key=coin_latest["symbol"], value=coin_latest)

            print(f"produce event with key = {kafka_message.key}, price = {coin_latest['quote']['USD']['price']}")

            # 5.将序列化后的消息发送到 Kafka 主题 coins 中
            producer.produce(topic=coins_topic.name, key=kafka_message.key, value=kafka_message.value)

            time.sleep(30)    # 每次抓取数据后会有 30 秒的延迟


if __name__ == "__main__":
    main()








