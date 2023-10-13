"""
"""

import pandas as pd
from anomstack.gcp.bigquery import save_df_bigquery
from anomstack.duckdb.duckdb import save_df_duckdb
from anomstack.snowflake.snowflake import save_df_snowflake


def save_df(df, db, table_key, gcp_project_id, if_exists='append') -> pd.DataFrame:
    """
    Save df to db.
    """

    if db=='bigquery':
        df = save_df_bigquery(df, table_key, gcp_project_id, if_exists)
    elif db=='snowflake':
        df = save_df_snowflake(df, table_key)
    elif db=='duckdb':
        df = save_df_duckdb(df, table_key)
    else:
        raise ValueError(f'Unknown db: {db}')

    return df
