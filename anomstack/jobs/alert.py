"""
Generate alert jobs and schedules.
"""

import pandas as pd
from dagster import get_dagster_logger, job, op, ScheduleDefinition, JobDefinition
from anomstack.config import specs
from anomstack.alerts.send import send_alert
from anomstack.sql.render import render_sql
from anomstack.sql.read import read_sql


def build_alert_job(spec) -> JobDefinition:
    """
    Build job definitions for alert jobs.
    """
    
    logger = get_dagster_logger()
    
    metric_batch = spec['metric_batch']
    db = spec['db']
    
    @job(name=f'{metric_batch}_alerts')
    def _job():
        """
        Get data for alerting.
        """

        @op(name=f'{metric_batch}_get_alerts')
        def get_alerts() -> pd.DataFrame:
            """
            Get data for alerting.
            """
            df_alerts = read_sql(render_sql('alert_sql', spec), db)
            return df_alerts

        @op(name=f'{metric_batch}_alerts_op')
        def alert(df_alerts) -> pd.DataFrame:
            """
            Alert on data.
            """
            
            if len(df_alerts) == 0:
                logger.info('no alerts to send')
            else:
                for metric_name in df_alerts['metric_name'].unique():
                    logger.info(f"alerting on {metric_name}")
                    df_alert = df_alerts.query(f"metric_name=='{metric_name}'")
                    metric_timestamp_max = df_alert['metric_timestamp'].max().strftime('%Y-%m-%d %H:%M')
                    alert_title = f"🔥 [{metric_name}] looks anomalous ({metric_timestamp_max}) 🔥"
                    df_alert = send_alert(
                        metric_name=metric_name,
                        title=alert_title,
                        df=df_alert
                    )

            return df_alerts

        alert(get_alerts())

    return _job


# generate jobs
alert_jobs = [build_alert_job(specs[spec]) for spec in specs]

# define schedules
alert_schedules = [
    ScheduleDefinition(
        job=alert_job,
        cron_schedule=specs[alert_job.name.replace('_alerts', '')][
            'alert_cron_schedule'
        ],
    )
    for alert_job in alert_jobs
]
