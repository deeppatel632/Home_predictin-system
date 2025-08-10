"""Utility script to build model artifacts for Bangalore Home Price Prediction.
Run from the Workshop directory:

    python build_artifacts.py

Outputs:
    artifacts/columns.json
    artifacts/bangalore_home_prices_model.pkl

Requires the raw dataset located at ../Bengaluru_House_Data.csv.xls
"""
from __future__ import annotations
import json
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = (BASE_DIR.parent / "Bengaluru_House_Data.csv.xls").resolve()
ARTIFACT_DIR = BASE_DIR / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "bangalore_home_prices_model.pkl"
COLUMNS_JSON = ARTIFACT_DIR / "columns.json"


def log(msg: str):
    print(f"[build] {msg}")


def is_float(x: str) -> bool:
    try:
        float(x)
        return True
    except Exception:
        return False


def convert_sqft_to_num(x: str):
    try:
        if '-' in x:
            a, b = x.split('-')
            return (float(a) + float(b)) / 2
        return float(x)
    except Exception:
        return np.nan


def remove_pps_outliers(df: pd.DataFrame) -> pd.DataFrame:
    df_out = pd.DataFrame()
    for _loc, subdf in df.groupby('location'):
        m = subdf.price_per_sqft.mean()
        st = subdf.price_per_sqft.std()
        reduced = subdf[(subdf.price_per_sqft > (m - st)) & (subdf.price_per_sqft <= (m + st))]
        df_out = pd.concat([df_out, reduced], ignore_index=True)
    return df_out


def remove_bhk_outliers(df: pd.DataFrame) -> pd.DataFrame:
    exclude_indices = np.array([], dtype=int)
    for location, location_df in df.groupby('location'):
        bhk_stats = {}
        for bhk, bhk_df in location_df.groupby('bhk'):
            bhk_stats[bhk] = {
                'mean': bhk_df.price_per_sqft.mean(),
                'std': bhk_df.price_per_sqft.std(),
                'count': bhk_df.shape[0]
            }
        for bhk, bhk_df in location_df.groupby('bhk'):
            stats = bhk_stats.get(bhk - 1)
            if stats and stats['count'] > 5:
                exclude_indices = np.append(
                    exclude_indices,
                    bhk_df[bhk_df.price_per_sqft < stats['mean']].index.values
                )
    return df.drop(exclude_indices, axis='index')


def build():
    if not DATA_PATH.exists():
        raise SystemExit(f"Dataset not found at {DATA_PATH}")
    ARTIFACT_DIR.mkdir(exist_ok=True)

    log(f"Loading dataset: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)

    # Basic cleanup
    df = df.drop(['area_type', 'society', 'balcony', 'availability'], axis='columns')
    df = df.dropna()

    # bhk from size
    df['bhk'] = df['size'].apply(lambda x: int(str(x).split(' ')[0]))

    # total_sqft numeric
    df['total_sqft'] = df['total_sqft'].apply(convert_sqft_to_num)
    df = df.dropna(subset=['total_sqft'])

    # filter unrealistic bhk per sqft
    df = df[~(df.total_sqft / df.bhk < 300)]

    # normalize location strings
    df.location = df.location.apply(lambda x: x.strip())
    location_counts = df.location.value_counts()
    rare_locs = location_counts[location_counts <= 10].index
    df.location = df.location.apply(lambda x: 'other' if x in rare_locs else x)

    # price per sqft
    df['price_per_sqft'] = df['price'] * 100000 / df['total_sqft']

    # remove pps outliers & bhk outliers
    df = remove_pps_outliers(df)
    df = remove_bhk_outliers(df)

    # bathroom rule
    df = df[df.bath <= df.bhk + 2]

    # final selection
    df_model = df.drop(['size', 'price_per_sqft'], axis='columns')

    # one-hot encode locations
    dummies = pd.get_dummies(df_model.location)
    df_model = pd.concat([df_model.drop('location', axis='columns'), dummies.drop(columns=['other'], errors='ignore')], axis=1)

    # Feature matrix and target
    X = df_model.drop('price', axis='columns')
    y = df_model.price

    # Ensure numeric dtype
    X = X.astype(float)

    log(f"Shape after encoding: X={X.shape} y={y.shape}")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    log(f"LinearRegression R^2 on holdout: {score:.4f}")

    # Prepare columns list: maintain order as in X columns
    data_columns = list(X.columns)

    # Lower-case for location columns only (keep numeric names consistent)
    normalized_columns = []
    for c in data_columns:
        if c.lower() in ('total_sqft', 'bath', 'bhk'):
            normalized_columns.append(c.lower())
        else:
            normalized_columns.append(c.lower())

    log(f"Total feature columns: {len(normalized_columns)}")

    # Save artifacts
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    with open(COLUMNS_JSON, 'w') as f:
        json.dump({'data_columns': normalized_columns}, f, indent=2)

    log(f"Artifacts written: {MODEL_PATH.name}, {COLUMNS_JSON.name}")


if __name__ == '__main__':
    build()
