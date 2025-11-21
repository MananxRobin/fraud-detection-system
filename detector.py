import json
import requests
from confluent_kafka import Consumer, KafkaError

# Configuration
conf = {
    'bootstrap.servers': '127.0.0.1:9092',
    'group.id': 'fraud-detection-group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
consumer.subscribe(['financial_transactions'])

PREDICTION_ENDPOINT = 'http://localhost:8000/predict'

print("Listening for suspicious transactions...")

try:
    while True:
        # Poll for a message (wait up to 1.0 second)
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break

        # Process Message
        try:
            data_str = msg.value().decode('utf-8')
            transaction = json.loads(data_str)

            # Send to FastAPI Model
            response = requests.post(PREDICTION_ENDPOINT, json=transaction)

            if response.status_code == 200:
                result = response.json()
                if result['is_fraud']:
                    print(
                        f"🚨 FRAUD DETECTED: {transaction['nameOrig']} | ${transaction['amount']} | Risk: {result['fraud_probability']:.2f}")
                else:
                    print(f"✅ Legit: {transaction['nameOrig']} | ${transaction['amount']}")
            else:
                print("❌ API Error")

        except Exception as e:
            print(f"Error processing message: {e}")

except KeyboardInterrupt:
    pass
finally:
    consumer.close()