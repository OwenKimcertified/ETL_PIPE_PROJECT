import pytest
from airflow.models import DagBag
from datetime import datetime
from api_ETL_PIPELINE import dag

def test_dag_loading():
    dagbag = DagBag(include_examples=False)
    assert len(dagbag.dags) == 1, "Number of DAGs is different than expected."

def test_etl_datapipeline():
    dag_id = 'etl_datapipeline'
    assert dag_id in dag.dag_id, f"'{dag_id}' DAG not found."

    # Verify that the DAG was loaded correctly
    assert dag is not None, f"Unable to load '{dag_id}' DAG."

    # Check the tasks included in the DAG
    task_ids = [task.task_id for task in dag.tasks]
    expected_task_ids = ['available_or_not', 'extract_riot_api', 'process_api_data']
    assert all(task_id in task_ids for task_id in expected_task_ids), "Required tasks are missing from the DAG."
