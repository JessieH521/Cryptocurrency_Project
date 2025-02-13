import time
from quixstreams import Application   # 流式数据处理的库，处理 Kafka 消息的对象，负责从 Kafka 中获取数据和发布数据。
import json
from pprint import pprint
from connect_api import get_latest_coin_data, fetch_exchange_rates

TARGET_COIN = "ETH"
CURRENCY = "NOK"      # 目标货币（可以选择 SEK, NOK, DKK 等）

# Get exchange rate
exchange_rates = fetch_exchange_rates()

def convert_price(usd_price, CURRENCY="SEK"):
    """ 使用 API 获取的实时汇率转换 USD 价格 """
    if exchange_rates and CURRENCY in exchange_rates:
        return round(usd_price * exchange_rates[CURRENCY], 2)
    return usd_price     # 如果汇率不可用，返回 USD 价格


# 创建了一个 Quix Streams 的应用实例，创建了一个名为 coins 的 Kafka 主题，输出JSON，连接到本地的 Kafka 服务，
def main():
    app = Application(broker_address="localhost:9092", consumer_group="ETH_coin_group")
    coins_topic = app.topic(name="ETH_coins", value_serializer="json")

    # 3. # 获取 Kafka 生产者对象 producer，负责向 Kafka 主题发送消息。
    with app.get_producer() as producer:

        while True:
            coin_latest = get_latest_coin_data(TARGET_COIN)

            # 获取原始美元价格
            usd_price = coin_latest["quote"]["USD"]["price"]

            # 转换价格到所选货币
            local_price = convert_price(usd_price, CURRENCY)

            # 在 coin_latest["quote"] 里新增一个键值对，使其包含选定货币（CURRENCY）的价格
            coin_latest["quote"][CURRENCY] = {"price": local_price}

            # 4. 将获取到的数据序列化为 Kafka 消息
            kafka_message = coins_topic.serialize(key=coin_latest["symbol"], value=coin_latest)

            print(f"produce event with key = {kafka_message.key}, price = {local_price}{CURRENCY}")

            # 5.将序列化后的消息发送到 Kafka 主题 coins 中
            producer.produce(topic=coins_topic.name, key=kafka_message.key, value=kafka_message.value)

            time.sleep(30)    # 每次抓取数据后会有 30 秒的延迟


if __name__ == "__main__":
    main()








