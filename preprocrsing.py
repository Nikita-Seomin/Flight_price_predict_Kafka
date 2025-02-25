import pandas as pd

def get_unique_categories(df):
    df = df.drop('flight', axis=1)
    # Определяем категориальные признаки
    categorical_columns = df.select_dtypes(include=['object']).columns

    # Получаем уникальные значения для каждого категориального признака
    unique_categories = {col: df[col].unique() for col in categorical_columns}

    # Выполняем One-Hot Encoding
    df_encoded = pd.get_dummies(df, columns=categorical_columns)
    df_encoded = df_encoded.applymap(lambda x: 1 if x is True else (0 if x is False else x))

    return df_encoded.drop('Unnamed: 0', axis=1)