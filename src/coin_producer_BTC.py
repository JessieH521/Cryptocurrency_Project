import time
from quixstreams import Application   # 流式数据处理的库，处理 Kafka 消息的对象，负责从 Kafka 中获取数据和发布数据。
import json
from pprint import pprint
from connect_api import get_latest_coin_data    # 现在从 connect_api.py 导入


# 创建了一个 Quix Streams 的应用实例，创建了一个名为 coins 的 Kafka 主题，输出JSON，连接到本地的 Kafka 服务，
def main():
    app = Application(broker_address="localhost:9092", consumer_group="BTC_coin_group")
    coins_topic = app.topic(name="BTC_coins", value_serializer="json")

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








