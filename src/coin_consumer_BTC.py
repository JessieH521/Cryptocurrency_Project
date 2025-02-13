from quixstreams import Application
from quixstreams.sinks.community.postgresql import PostgreSQLSink
from constants import (
    POSTGRES_DBNAME,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER)
from pprint import pprint

# 解析 Kafka 消息数据 message,是来自 Kafka 的 JSON 数据,返回一个 Python 字典，用于后续存入数据库.
def extract_coin_data(message):
    latest_quote = message["quote"]["USD"]
    return{
        "coin": message["name"],
        "price_usd": latest_quote["price"],
        "volume": latest_quote["volume_24h"],
        "updated": message["last_updated"]
    }

# 创建 PostgreSQL 数据库 Sink, 目标表是 bitcoin.
def create_postgres_sink():
    sink = PostgreSQLSink(
        host=POSTGRES_HOST, # type: ignore
        port=POSTGRES_PORT, # type: ignore
        dbname=POSTGRES_DBNAME, # type: ignore
        user=POSTGRES_USER,  # type: ignore
        password=POSTGRES_PASSWORD, # type: ignore
        table_name="bitcoin",
        schema_auto_update=True,)    # 如果数据模式变了（比如新字段），自动更新 PostgreSQL 表结构。
    
    return sink

# 1. 主程序逻辑, Application 连接 Kafka， app 是实例
def main():
    app = Application(
        broker_address="localhost:9092",
        consumer_group="BTC_coin_group",        # Kafka 消费者组（多个 consumer 共享读取）
        auto_offset_reset="earliest",
    )

    # 2. 订阅 Kafka 主题 coins，消息格式是 JSON
    #  app 是 Application 类的一个实例，代表 QuixStreams 的应用对象。它的作用是 管理 Kafka 连接、订阅主题、处理数据流，并最终存入数据库。
    coins_topic = app.topic(name="BTC_coins", value_deserializer="json")

    sdf = app.dataframe(topic=coins_topic)

    # 3. transformations, 转换数据：从 Kafka 消息中提取 coin、price_usd、volume、updated 等字段
    sdf = sdf.apply(extract_coin_data)

    # 4. 处理后的数据存入 PostgreSQL bitcoin 表
    # sink to postgres
    postgres_sink = create_postgres_sink()

    sdf.sink(postgres_sink)

    # 每次收到 Kafka 消息，就打印处理后的 coin_data
    sdf.update(lambda transformed_data: pprint(transformed_data))
    
    # 5. 启动 QuixStreams 应用，消费 Kafka 数据，并存入数据库
    app.run()  

if __name__ == "__main__":
    main()














