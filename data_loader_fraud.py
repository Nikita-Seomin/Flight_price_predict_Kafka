import json
import time
import random
from confluent_kafka import Producer
import threading
import pandas as pd
import config
from preprocrsing import get_unique_categories


def start_producer(producer_id, topic, dataset, num_messages):
    producer = Producer(config.DATA_LOAD_CONFIG)

    for i in range(num_messages):
        if i >= len(dataset):  # Exit if the data is finished
            break
        sample_x = dataset.iloc[i].to_dict()  # Correctly access the row and convert to dictionary
        message = json.dumps(sample_x)

        producer.produce(topic, key=str(producer_id), value=message)
        producer.flush()
        print(f"Producer sent: {message}")

        # Random delay
        delay = random.uniform(0.2, 1.0)
        time.sleep(delay)


def load_dataset():
    df = pd.read_csv('Clean_Dataset.csv')  # Make sure the path is correct
    # dataset = df.to_dict(orient='records')
    return df

def main():
    num_producers = 3  # Number of Producers
    num_messages = 100  # Number of messages each Producer will send

    dataset = load_dataset()
    dataset = get_unique_categories(dataset)

    # Start multiple Producers
    threads = []
    for i in range(num_producers):
        thread = threading.Thread(
            target=start_producer,
            args=(i + 1, config.DATA_LOAD_TOPIC, dataset, num_messages)
        )
        threads.append(thread)
        thread.start()

    # Wait for all Producers to finish
    for thread in threads:
        thread.join()

if __name__ == "__main__":  # Corrected line
    main()
