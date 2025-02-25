from confluent_kafka import Consumer
import streamlit as st
import json
import pandas as pd
import time
import config

st.set_page_config(page_title="Credit Card Fraud Detection", layout="wide")

# Инициализация состояния сессии
if "RMSE" not in st.session_state:
    st.session_state["RMSE"] = []
if "MAE" not in st.session_state:
    st.session_state["MAE"] = []
if "true_values" not in st.session_state:
    st.session_state["true_values"] = []
if "predicted_values" not in st.session_state:
    st.session_state["predicted_values"] = []

# топик model_results
model_results_consumer = Consumer(config.DASHBOARD_CONFIG)
model_results_consumer.subscribe(["model_results"])

# топик metrics
metrics_consumer = Consumer(config.DASHBOARD_CONFIG)
metrics_consumer.subscribe(["metrics"])

st.header("Flight price predict Dashboard")

# Контейнеры
st.subheader("Root Mean Squared Error (RMSE)")
chart_holder_rmse = st.empty()

st.subheader("MAE")
chart_holder_mae = st.empty()

st.subheader("Последние предсказания")
predictions_chart_holder = st.empty()

while True:
    # Чтение из model_results
    model_message = model_results_consumer.poll(1.0)
    if model_message is not None:
        try:
            model_data = json.loads(model_message.value().decode("utf-8"))
            true_value = model_data.get("true_value")
            predicted_value = model_data.get("predicted_value")

            if true_value is not None and predicted_value is not None:
                st.session_state["true_values"].append(true_value)
                st.session_state["predicted_values"].append(predicted_value)

                # Показываем последние предсказания
                predictions_df = pd.DataFrame({
                    "Реальное значение": st.session_state["true_values"],
                    "Предсказанное значение": st.session_state["predicted_values"]
                })
                predictions_chart_holder.line_chart(predictions_df)
        except json.JSONDecodeError as e:
            print(f"Ошибка декодирования JSON: {e}")

    # Чтение данных из топика metrics
    metrics_message = metrics_consumer.poll(1.0)
    if metrics_message is not None:
        try:
            metrics_data = json.loads(metrics_message.value().decode("utf-8"))
            rmse_value = metrics_data.get("RMSE")
            mae_value = metrics_data.get("MAE")

            if mae_value is not None:
                st.session_state["MAE"].append(mae_value)
                chart_holder_mae.line_chart(st.session_state["MAE"])

            if rmse_value is not None:
                st.session_state["RMSE"].append(rmse_value)
                chart_holder_rmse.line_chart(st.session_state["RMSE"])
        except json.JSONDecodeError as e:
            print(f"Ошибка декодирования JSON: {e}")

    # задержка
    time.sleep(0.1)