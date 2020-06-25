from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.hooks.S3_hook import S3Hook
from datetime import datetime, timedelta
import boto3

INSERT_HISTORY_SQL=\
"""insert into daily_history 
select current_date as date,
		t3.mac_specs as machine,
		t3.prices as lowest3prices
from (
	select *
	from get_top3('i5', 4, %s)
	union
	select *
	from get_top3('i5', 8, %s)
	union
	select *
	from get_top3('i7', 8, %s)
) t3;"""


# Define DAG
default_args = {
    'owner': 'munkit',
    'start_date': datetime(2020, 6, 9),
    'retry_delay': timedelta(hours=2)
}

# context manager
with DAG(dag_id='ebay_x_dag', 
         default_args=default_args, 
         schedule_interval='16 0 * * *') as dag:

    delete_json_start_task = BashOperator(
        task_id='delete_json_start_task',
        bash_command='rm -f ~/ebay_proj/scraped_json/*'
    )

    launch_spider_task = BashOperator(
        task_id='launch_spider_task',
        bash_command='cd ~/ebay_proj; ./launch_spider.sh "thinkpad x220";./launch_spider.sh "thinkpad x230";./launch_spider.sh "thinkpad x240";'
    )

    upload_to_s3_task = BashOperator(
        task_id='upload_to_s3_task',
        bash_command='cd ~/ebay_proj;python3 s3_upload.py'
    )

    clean_load_db_task = BashOperator(
        task_id='clean_load_db_task',
        bash_command='cd ~/ebay_proj;python3 cleaning.py'
    )

    insert_lowest3_X220_task = PostgresOperator(
        task_id='insert_lowest3_X220_task',
        postgres_conn_id='mypgdb',
        sql=INSERT_HISTORY_SQL,
        parameters=['1']*3
    )

    insert_lowest3_X230_task = PostgresOperator(
        task_id='insert_lowest3_X230_task',
        postgres_conn_id='mypgdb',
        sql=INSERT_HISTORY_SQL,
        parameters=['2']*3
    )

    insert_lowest3_X240_task = PostgresOperator(
        task_id='insert_lowest3_X240_task',
        postgres_conn_id='mypgdb',
        sql=INSERT_HISTORY_SQL,
        parameters=['3']*3
    )

    delete_json_end_task = BashOperator(
        task_id='delete_json_end_task',
        bash_command='rm -f ~/ebay_proj/scraped_json/*'
    )

    # arrows set dependencies between tasks
    delete_json_start_task >> launch_spider_task >> upload_to_s3_task >> \
    clean_load_db_task >> insert_lowest3_X220_task >> \
    insert_lowest3_X230_task >> insert_lowest3_X240_task >> \
    delete_json_end_task

