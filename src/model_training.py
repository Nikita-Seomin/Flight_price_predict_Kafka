import json
import time
import random
from confluent_kafka import Consumer, Producer
from river import compose, preprocessing, metrics, linear_model
import pandas as pd
from src import config


def data_preparation(sample):
    sample_x = pd.DataFrame([sample])
    sample_y = float(sample_x.pop('price').values[0])
    sample_x = sample_x.to_dict(orient='records')[0]
    # print(sample_x, sample_y)
    return sample_x, sample_y

def prepare_data_for_visualizer(sample_x, y_true, y_pred, metric_rmse, metric_mae):
    return {
        'true_value': y_true,
        'predicted_value': y_pred,
        'metric_rmse': metric_rmse.get(),
        'metric_mae': metric_mae.get()
    }

if __name__ == "__main__":  # Corrected here
    consumer = Consumer(config.MODEL_TRAINING_CONSUMER_CONFIG)
    training_producer = Producer(config.MODEL_TRAINING_PRODUCER_CONFIG)
    metrics_producer = Producer(config.METRICS_PRODUCER_CONFIG)

    consumer.subscribe([config.DATA_MINER_TOPIC])

    # Инициализация модели
    model = compose.Pipeline(
        preprocessing.StandardScaler(),
        linear_model.LinearRegression()
    )

    metric_rmse = metrics.RMSE()
    metric_mae = metrics.MAE()

    while True:
        message = consumer.poll(1000)
        if message is None:
            continue
        message_value = message.value().decode('utf-8')

        try:
            sample = json.loads(message_value)
            sample_x, sample_y = data_preparation(sample)
            # print(sample_x, sample_y)

            # Обучение модели
            model.learn_one(sample_x, sample_y)
            y_pred = model.predict_one(sample_x)
            metric_rmse.update(sample_y, y_pred)
            metric_mae.update(sample_y, y_pred)
            print(sample_y, y_pred)

            to_visualizer = prepare_data_for_visualizer(sample_x, sample_y, y_pred, metric_rmse, metric_mae)
            # print(to_visualizer)

            # Отправка результатов обучения в топик model_results
            training_producer.produce(
                config.MODEL_TRAINING_TOPIC, key='1',
                value=json.dumps(to_visualizer)
            )
            training_producer.flush()

            # Отправка метрик в топик metrics
            metrics_producer.produce(
                config.METRICS_TOPIC, key='1',
                value=json.dumps({"RMSE": metric_rmse.get(), "MAE": metric_mae.get()})
            )
            metrics_producer.flush()

            # Случайная задержка
            delay = random.uniform(0.2, 1.0)
            time.sleep(delay)
            print()

        except json.JSONDecodeError as e:
            print(f"Ошибка JSON: {e}")
            print(f"Содержимое сообщения: {message_value}")
