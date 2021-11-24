"""
### This is the first DAG documentation I wrote.
"""

import json
import pathlib
from textwrap import dedent

import airflow
import requests
import requests.exceptions as requests_exceptions
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


default_args = {
    # 'owner': 'airflow',
    # 'depends_on_past': False,
    # 'email': ['airflow@example.com'],
    # 'email_on_failure': False,
    # 'email_on_retry': False,
    # 'retries': 1,
    # 'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}

dag = DAG(dag_id="rocket_pictures",
        start_date= airflow.utils.dates.days_ago(14),
        schedule_interval=None,
        default_args= default_args,
        tags=['oguzhan'])

dag.doc_md = __doc__

launches_path = r"/tmp/launches.json"
images_path = r"/tmp/images"

download_bash_command = """curl -o {{ params.launches_path }} -L 'https://ll.thespacedevs.com/2.0.0/launch/upcoming'"""
download_launch_info = BashOperator(task_id="download_launch_info", bash_command=download_bash_command,
                                    params={"launches_path":launches_path}, dag= dag)

download_launch_info.doc_md = dedent("""\
                                    ### This is task documentation
                                    Yay! """)

def _download_images(launches_path=launches_path, images_path=images_path):
    pathlib.Path(images_path).mkdir(parents=True, exist_ok=True)
    with open(launches_path) as file:
        launches = json.load(file)
        image_urls = [launch["image"] for launch in launches["results"]]
        
        for image_url in image_urls:
            try:
                response = requests.get(image_url)
                image_name = image_url.split("/")[-1]
                write_path = f"{images_path}/{image_name}"
                with open(write_path, "wb") as file:
                    file.write(response.content)
                print(f"Downloaded {image_url} to {write_path}")
            except requests_exceptions.MissingSchema:
                print(f"{image_url} appears to be an invalid URL.")
            except requests_exceptions.ConnectionError:
                print(f"Could not connect to {image_url}.")
    return
    

download_images = PythonOperator(task_id = "download_images", python_callable= 
                                 _download_images,
                                 dag= dag)

download_launch_info >> download_images