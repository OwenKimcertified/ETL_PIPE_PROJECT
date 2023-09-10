from datetime import datetime
from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
from airflow.models import DagRun
from airflow.operators.bash import BashOperator
from pymongo import MongoClient
import pandas as pd
import json
import os
from pipe_model_ckdata import DataFrameQualityChecker 
from kafka import KafkaProducer
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

API_KEY = 'RGAPI-b76efdb2-b42b-44f8-bec8-1a05043cfcf9'

# Kafka info
brokers = ["localhost:9091", "localhost:9092", "localhost:9093"]
topicname = "ETL_PIPE_LOGGING"

# Airflow-connection Host: https://kr.api.riotgames.com/
arg = {'start_date': datetime(2023, 1, 11)}

# MySQL info
mysql_conn_id = 'local_mysql'
mysql_user = 'owen'
mysql_password = 'root'
mysql_host = 'localhost'
mysql_port = '3306'
mysql_db = 'api_data'

# ORM
Base = declarative_base()

class userinfo(Base):
    __tablename__ = 'api_summoner_info'
    summoner_id = Column(String, primary_key=True)
    summoner_name = Column(String)
    QType = Column(String)

# Airflow info
dag_id = 'etl_datapipeline'
execution_date = datetime.now()
task_id = 'extract_riot_api'
xcom_key = 'return_value'

def _processing_api(**context):
    xcom_value = context['task_instance'].xcom_pull(task_ids='extract_riot_api')
    df = pd.DataFrame(xcom_value)
    df = df[['summonerId', 'summonerName', 'queueType']]
    df.rename(columns={'summonerId': 'summoner_id', 'summonerName': 'summoner_name', 'queueType': 'QType'}, inplace=True)
    print(df.head())
    ti = context['ti']
    ti.xcom_push(key = 'df', value = df)

    dir = '/home/owen/api_data'
    if not os.path.exists(dir):
        os.makedirs(dir)

    file_path = os.path.join(dir, f'{datetime.now().date()}CHALLENGER_LIST.csv')
    df.to_csv(file_path)

    # MySQL connection
    conn_str = f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"
    engine = create_engine(conn_str)
    SA = sessionmaker(bind = engine)
    ss = SA()

    data_insert = df.to_dict(orient='records')
    for data in data_insert:
        user_info = userinfo(**data)
        ss.add(user_info)

    ss.commit()

    # Save original data to MongoDB (NoSQL)
    atlas_addr = "mongodb+srv://owen:root@cluster0.q3959zk.mongodb.net/"
    client = MongoClient(atlas_addr)
    db = client.toy
    collection = db.nosql_api_datas
    df_injection = df.to_dict(orient='records')

    collection.insert_many(df_injection)
    client.close()

def check_cols_vif(**context):
    ti = context['ti']
    df = ti.xcom_pull(task_ids='process_api_data', key='df')
    print(df.head())

    DQ = DataFrameQualityChecker(df)
    vif_value = DQ.calculation_vif('QType')

    text1 = f" vif value : {vif_value}"
    en_text1 = text1.encode('utf-8')
    text2 = f"{datetime.now().date()} success ETL"
    en_text2 = text2.encode('utf-8')
    producer = KafkaProducer(bootstrap_servers=brokers)
    producer.send(topicname, en_text1)
    producer.send(topicname, en_text2)
    producer.flush()
    return print('DONE')

def check_df_info(**context):
    ti = context['ti']
    df = ti.xcom_pull(task_ids='process_api_data', key='df')

    DQ = DataFrameQualityChecker(df)
    check_df = DQ.check_data_quality()

    return check_df

# DAG skeleton
with DAG(dag_id = 'etl_datapipeline',
         schedule_interval = '@daily',
         default_args = arg,
         tags = ['etl_pipe'],
         catchup = False) as dag:

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
        provide_context = True,
        dag = dag
    )

    check_data_stability = PythonOperator(
        task_id = 'check_data_stability',
        python_callable = check_df_info,
        dag = dag
    )

    check_data_vif = PythonOperator(
        task_id = 'check_data_vif',
        python_callable = check_cols_vif,
        dag = dag
    )

api_check >> extract_data >> check_data_stability >> process_api_data 