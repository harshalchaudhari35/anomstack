"""
Some utility functions.
"""

import json
import os

import duckdb
import jinja2
import pandas as pd
import requests
from dagster import get_dagster_logger
from jinja2 import FileSystemLoader


def read_sql_duckdb(sql) -> pd.DataFrame:
    """
    Read data from SQL.
    """

    logger = get_dagster_logger()

    duckdb_path = os.environ.get("ANOMSTACK_DUCKDB_PATH", "tmpdata/anomstack.db")
    logger.info(f"duckdb_path:{duckdb_path}")

    conn = duckdb.connect(duckdb_path)

    logger.debug(f"sql:\n{sql}")
    df = duckdb.query(connection=conn, query=sql).df()
    logger.debug(f"df:\n{df}")

    return df


def save_df_duckdb(df, table_key) -> pd.DataFrame:
    """
    Save df to db.
    """

    logger = get_dagster_logger()

    duckdb_path = os.environ.get("ANOMSTACK_DUCKDB_PATH", "tmpdata/anomstack.db")
    logger.info(f"duckdb_path:{duckdb_path}")
    conn = duckdb.connect(duckdb_path)

    try:
        if "." in table_key:
            schema, _ = table_key.split(".")
            duckdb.query(connection=conn, query=f"CREATE SCHEMA IF NOT EXISTS {schema}")
        duckdb.query(connection=conn, query=f"INSERT INTO {table_key} SELECT * FROM df")
    except:
        duckdb.query(
            connection=conn, query=f"CREATE TABLE {table_key} AS SELECT * FROM df"
        )

    return df
