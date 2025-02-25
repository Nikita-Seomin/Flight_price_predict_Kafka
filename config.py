# Data load
DATA_LOAD_TOPIC = 'data_producer'
DATA_LOAD_CONFIG = {'bootstrap.servers': 'localhost:9095,localhost:9096'}

#Model training
DATA_MINER_TOPIC = 'data_producer'
MODEL_TRAINING_TOPIC = 'model_results'
METRICS_TOPIC = 'metrics'

MODEL_TRAINING_CONSUMER_CONFIG = {'bootstrap.servers': 'localhost:9096',
                                'group.id': 'model_training',
                                'auto.offset.reset': 'earliest'}
MODEL_TRAINING_PRODUCER_CONFIG = {'bootstrap.servers': 'localhost:9095'}
METRICS_PRODUCER_CONFIG = {'bootstrap.servers': 'localhost:9095'}

#Dashboard
DASHBOARD_CONFIG = {"bootstrap.servers": "localhost:9095",
                            "group.id": "streamlit_metrics_consumer",
                            "auto.offset.reset": "earliest"}




