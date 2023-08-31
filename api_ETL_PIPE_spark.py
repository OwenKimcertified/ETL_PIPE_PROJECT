from datetime import datetime
from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
from airflow.models import DagRun
from airflow.utils.session import create_session
from airflow.operators.bash import BashOperator
# from pandas import json_normalize 보류
import pandas as pd, json, os
import sqlite3

# orm ts

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

API_KEY = 'RGAPI-abd6f080-d5bd-47cc-a501-253f5851f812'

# airflow-connection Host : https://kr.api.riotgames.com/

arg = {'start_date' : datetime(2023,1,11)}
#------------------ mysql info
# mysql_conn_id = 'mysql'
# mysql_user = 'root'
# mysql_password = 'root'
# mysql_host = 'localhost'
# mysql_port = '3306'
# mysql_db = 'api'
# mysql_hook = MySqlHook(mysql_conn_id = mysql_conn_id)
# conn_address = f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"
#------------------ sqlite
Base = declarative_base()

class userinfo(Base):
    __tablename__ = 'api_data'
    summoner_id = Column(String, primary_key = True)
    summoner_name = Column(String)
    QType = Column(String)


#------------------- airflow info

dag_id = 'etl_datapipeline'
# execution_date_str = '2023-08-05T15:11:18.559982+00:00'
execution_date = datetime.now()
task_id = 'extract_riot_api'
xcom_key = 'return_value'


#------------------- 

def _processing_api(**context):
    # with create_session() as session:
    #     dagrun = session.query(DagRun).filter(
    #         DagRun.dag_id == dag_id,
    #         DagRun.execution_date == execution_date
    #     ).first()

    # if not dagrun:
    #     raise Exception(f"DagRun for DAG '{dag_id}' and execution date '{execution_date}' not found.")
    
    # else:
    #     xcom_value = dagrun.get_task_instance(task_id = task_id).xcom_pull(key = xcom_key)
    #     print(f"XCom Value: {xcom_value}")
    xcom_value = context['task_instance'].xcom_pull(task_ids='extract_riot_api')
    df = pd.DataFrame(xcom_value)
    df = df[['summonerId', 'summonerName', 'queueType']]
    df.rename(columns={'summonerId': 'summoner_id', 'summonerName': 'summoner_name', 'queueType': 'QType'}, inplace=True)
    print(df.head())

    dir = '/home/owen/api_data'  
    if not os.path.exists(dir):
        os.makedirs(dir)    
    
    file_path = os.path.join(dir, f'{datetime.now().date()}CHALLENGER_LIST.csv')
    df.to_csv(file_path)
    
    engine = create_engine('sqlite:///database.db')
    SA = sessionmaker(bind = engine)
    ss = SA()

    data_insert = df.to_dict(orient='records')
    for data in data_insert:
        user_info = userinfo(**data)
        ss.add(user_info)
    
    ss.commit()
   
# dag skeleton
with DAG(dag_id = 'etl_datapipeline',
         schedule_interval = '@daily', # '0 0 * * * *'
         default_args = arg,
         tags = ['etl_pipe'],
         catchup = False) as dag: #catchup -> backfill

# operator
# bash func : bash operator
# python func : python operator
# email send : email operator

    api_check = HttpSensor(
        task_id = 'available_or_not',
        http_conn_id = 'riot_api',
        endpoint = f"lol/league-exp/v4/entries/RANKED_SOLO_5x5/CHALLENGER/I?page=1&api_key={API_KEY}"
    )

    extract_data = SimpleHttpOperator(
        task_id = 'extract_riot_api',
        http_conn_id = 'riot_api',
        endpoint = f"lol/league-exp/v4/entries/RANKED_SOLO_5x5/CHALLENGER/I?page=1&api_key={API_KEY}",
        method = 'GET',
        response_filter = lambda x: json.loads(x.text),
        log_response = True,
    )

    process_api_data = PythonOperator(
        task_id = 'process_api_data',
        python_callable = _processing_api,
        dag = dag
    )

    # store_data = BashOperator(
    #     task_id = 'store_data',
    #     bash_command = 'bash /path/to/your/bash_operator_script.sh'
    # )

api_check >> extract_data >> process_api_data