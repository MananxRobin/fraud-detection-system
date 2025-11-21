import time
import json
import pandas as pd
from confluent_kafka import Producer
import socket

# Configuration
conf = {
    'bootstrap.servers': '127.0.0.1:9092',
    'client.id': socket.gethostname()
}

producer = Producer(conf)
topic = 'financial_transactions'


def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result. """
    if err is not None:
        print(f'❌ Message delivery failed: {err}')
    # else:
    #     print(f'✅ Message delivered to {msg.topic()} [{msg.partition()}]')


# Load Data
print("Loading data...")
try:
    df = pd.read_csv('PS_20174392719_1491204439457_log.csv', nrows=1000)
except FileNotFoundError:
    print("❌ Error: CSV file not found. Please check the file name.")
    exit()

print(f"Starting streaming to {topic}...")

for index, row in df.iterrows():
    transaction = row.to_dict()
    transaction['timestamp'] = time.time()

    try:
        # Send to Kafka
        producer.produce(
            topic,
            json.dumps(transaction).encode('utf-8'),
            callback=delivery_report
        )

        # Trigger the callback to clear the queue buffer
        producer.poll(0)

        print(f"Sent: {transaction['nameOrig']} | ${transaction['amount']}")
        time.sleep(0.5)  # Simulate real-time delay

    except BufferError:
        print("⚠️ Buffer full, waiting...")
        producer.flush()

# Ensure all messages are sent before exiting
producer.flush()