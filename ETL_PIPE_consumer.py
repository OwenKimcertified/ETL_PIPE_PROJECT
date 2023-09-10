from kafka import KafkaConsumer

brokers = ["localhost:9091", "localhost:9092", "localhost:9093"]
consumer = KafkaConsumer("ETL_PIPE_LOGGING", bootstrap_servers = brokers)

for message in consumer:
    print(message)