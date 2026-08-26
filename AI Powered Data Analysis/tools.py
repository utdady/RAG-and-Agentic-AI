"""CSV analysis + sklearn eval tools for the data-analysis agent."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import pandas as pd
from langchain_core.tools import tool
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"

DATAFRAME_CACHE: dict[str, pd.DataFrame] = {}

SAFE_DF_METHODS = frozenset(
    {"head", "tail", "describe", "info", "columns", "shape", "dtypes"}
)


def _resolve_path(file_name: str) -> Path:
    """Map a basename or path to a CSV under DATA_DIR when possible."""
    p = Path(file_name)
    if p.is_file():
        return p
    candidate = DATA_DIR / Path(file_name).name
    if candidate.is_file():
        return candidate
    return p


def _cache_key(file_name: str) -> str:
    return str(_resolve_path(file_name))


def _load_df(file_name: str) -> pd.DataFrame | str:
    key = _cache_key(file_name)
    if key in DATAFRAME_CACHE:
        return DATAFRAME_CACHE[key]
    path = Path(key)
    if not path.is_file():
        return f"DataFrame '{file_name}' not found in cache or on disk."
    try:
        DATAFRAME_CACHE[key] = pd.read_csv(path)
        return DATAFRAME_CACHE[key]
    except Exception as e:
        return f"Error loading '{file_name}': {e}"


@tool
def list_csv_files() -> list[str] | None:
    """List CSV file names in the project data directory."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(p.name for p in DATA_DIR.glob("*.csv"))
    return files or None


@tool
def preload_datasets(paths: list[str]) -> str:
    """
    Load CSV files into a global cache if not already loaded.
    Prefer basenames from list_csv_files (e.g. classification-dataset.csv).
    """
    loaded: list[str] = []
    cached: list[str] = []
    errors: list[str] = []
    for path in paths:
        key = _cache_key(path)
        if key in DATAFRAME_CACHE:
            cached.append(path)
            continue
        result = _load_df(path)
        if isinstance(result, str):
            errors.append(result)
        else:
            loaded.append(path)
    parts = [f"Loaded datasets: {loaded}", f"Already cached: {cached}"]
    if errors:
        parts.append(f"Errors: {errors}")
    return "\n".join(parts)


@tool
def get_dataset_summaries(dataset_paths: list[str]) -> list[dict[str, Any]]:
    """
    Return column names and dtypes for each CSV path / basename.
    """
    summaries: list[dict[str, Any]] = []
    for path in dataset_paths:
        df_or_err = _load_df(path)
        if isinstance(df_or_err, str):
            summaries.append({"file_name": path, "error": df_or_err})
            continue
        df = df_or_err
        summaries.append(
            {
                "file_name": path,
                "column_names": df.columns.tolist(),
                "data_types": df.dtypes.astype(str).to_dict(),
                "n_rows": int(len(df)),
            }
        )
    return summaries


@tool
def call_dataframe_method(file_name: str, method: str) -> str:
    """
    Run a safe no-arg DataFrame inspection method on a cached/loaded CSV.

    Allowed methods: head, tail, describe, info, columns, shape, dtypes.
    """
    method = (method or "").strip()
    if method not in SAFE_DF_METHODS:
        return (
            f"Method '{method}' not allowed. "
            f"Use one of: {sorted(SAFE_DF_METHODS)}"
        )

    df_or_err = _load_df(file_name)
    if isinstance(df_or_err, str):
        return df_or_err
    df = df_or_err

    if method == "info":
        buf = io.StringIO()
        df.info(buf=buf)
        return buf.getvalue()
    if method == "columns":
        return str(df.columns.tolist())
    if method == "shape":
        return str(df.shape)
    if method == "dtypes":
        return str(df.dtypes.to_dict())

    func = getattr(df, method)
    try:
        return str(func())
    except Exception as e:
        return f"Error calling '{method}' on '{file_name}': {e}"


@tool
def evaluate_classification_dataset(
    file_name: str, target_column: str
) -> dict[str, float | str]:
    """
    Train a RandomForestClassifier (80/20 split) and return accuracy.
    Use for categorical / discrete target columns.
    """
    df_or_err = _load_df(file_name)
    if isinstance(df_or_err, str):
        return {"error": df_or_err}
    df = df_or_err
    if target_column not in df.columns:
        return {
            "error": f"Target column '{target_column}' not found in '{file_name}'."
        }

    X = df.drop(columns=[target_column])
    y = df[target_column]
    # sklearn needs numeric features; drop non-numeric silently for the lab CSVs
    X = X.select_dtypes(include=["number"])
    if X.empty:
        return {"error": "No numeric feature columns after dropping the target."}

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    return {"accuracy": float(accuracy_score(y_test, y_pred))}


@tool
def evaluate_regression_dataset(
    file_name: str, target_column: str
) -> dict[str, float | str]:
    """
    Train a RandomForestRegressor (80/20 split) and return r2_score and MSE.
    Use for continuous numeric target columns.
    """
    df_or_err = _load_df(file_name)
    if isinstance(df_or_err, str):
        return {"error": df_or_err}
    df = df_or_err
    if target_column not in df.columns:
        return {
            "error": f"Target column '{target_column}' not found in '{file_name}'."
        }

    X = df.drop(columns=[target_column])
    y = df[target_column]
    X = X.select_dtypes(include=["number"])
    if X.empty:
        return {"error": "No numeric feature columns after dropping the target."}

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    model = RandomForestRegressor(random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    return {
        "r2_score": float(r2_score(y_test, y_pred)),
        "mean_squared_error": float(mean_squared_error(y_test, y_pred)),
    }


ALL_TOOLS = [
    list_csv_files,
    preload_datasets,
    get_dataset_summaries,
    call_dataframe_method,
    evaluate_classification_dataset,
    evaluate_regression_dataset,
]

SYSTEM_PROMPT = (
    "You are a data science assistant. Use the available tools to analyze CSV "
    "files in the project data folder. Determine whether each dataset is for "
    "classification or regression from its structure (dtypes, target column). "
    "Prefer list_csv_files → get_dataset_summaries / call_dataframe_method, then "
    "evaluate_classification_dataset or evaluate_regression_dataset. "
    "Explain findings clearly and briefly."
)
