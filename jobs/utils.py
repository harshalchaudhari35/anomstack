"""
Some utility functions.
"""

from dagster import get_dagster_logger
import pandas as pd
import jinja2
from jinja2 import FileSystemLoader


def render_sql(sql_key, spec) -> str:
    """
    Render SQL from template.
    """
    
    environment = jinja2.Environment(loader=FileSystemLoader('metrics/'))
    sql = environment.from_string(spec[sql_key])
    sql = sql.render(
        table_key=spec.get('table_key'),
        metric_batch=spec.get('metric_batch'),
        train_max_n=spec.get('train_max_n'),
        score_max_n=spec.get('score_max_n'),
        alert_max_n=spec.get('alert_max_n'),
        alert_threshold=spec.get('alert_threshold'),
    )
    
    return sql


def read_sql(sql) -> pd.DataFrame:
    """
    Read data from SQL.
    """
    
    logger = get_dagster_logger()
    logger.info(f'sql:\n{sql}')
    df = pd.read_gbq(query=sql)
    logger.info(f'df:\n{df}')
    
    return df


def save_df(df, table_key, project_id, if_exists) -> pd.DataFrame:
    """
    Save df to db.
    """
    df.to_gbq(
        destination_table=table_key,
        project_id=project_id,
        if_exists=if_exists,
    )
    return df


def send_alert(df) -> pd.DataFrame:
    """
    Send alert.
    """
    
    logger = get_dagster_logger()
    logger.info(f'alerts to send: \n{df}')
    
    return df