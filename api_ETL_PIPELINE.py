import os, json, datetime
import pandas as pd
from datetime import datetime as dt
from pymongo import MongoClient
from kafka import KafkaProducer
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from airflow import DAG
from airflow.models import Variable
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.models import DagRun
from pipe_model_ckdata import *

# Constants
API_KEY = 'API_KEY'

brokers = ["localhost:9091", "localhost:9092", "localhost:9093"]
topicname = "ETL_PIPE_LOGGING"
topicname2 = "ETL_PIPE_ERR_LOGGING"

arg = {'start_date': dt(2023, 1, 11)}

mysql_conn_id = 'local_mysql'
mysql_db = 'api_data'

atlas_addr = "mongodb+srv://user:password@clustername.secret.mongodb.net/"

# ORM
Base = declarative_base()

class userinfo(Base):
    __tablename__ = 'api_summoner_info'
    summoner_id = Column(String, primary_key=True)
    summoner_name = Column(String)
    QType = Column(String)

# Airflow info
dag_id = 'etl_datapipeline'

# Functions
def _processing_api(**context):
    xcom_value = context['task_instance'].xcom_pull(task_ids = 'extract_riot_api')
    df = pd.DataFrame(xcom_value)
    df = df[['summonerId', 'summonerName', 'queueType']]
    df.rename(columns = {'summonerId': 'summoner_id', 'summonerName': 'summoner_name', 'queueType': 'QType'}, inplace = True)
    
    ti = context['ti']
    ti.xcom_push(key = 'df', value = df)

    dir = '/home/owen/api_data'
    os.makedirs(dir, exist_ok = True)
    file_path = os.path.join(dir, f'{datetime.datetime.now()}CHALLENGER_LIST.csv')
    df.to_csv(file_path)

    # MySQL connection
    mysql_conn_info = Variable.get("mysql_secret", deserialize_json = True)
    mysql_user = mysql_conn_info['mysql_user']
    mysql_password = mysql_conn_info['mysql_password']
    mysql_host = mysql_conn_info['mysql_host']
    mysql_port = mysql_conn_info['mysql_port']
    conn = f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"
    engine = create_engine(conn)
    SA = sessionmaker(bind = engine)
    sm = SA()

    data_insert = df.to_dict(orient = 'records')
    for data in data_insert:
        user_info = userinfo(**data)
        sm.add(user_info)

    sm.commit()

    # Save original data to MongoDB (NoSQL)
    client = MongoClient(atlas_addr)
    db = client.toy
    collection = db.nosql_api_datas
    df_injection = df.to_dict(orient = 'records')

    collection.insert_many(df_injection)
    client.close()

def check_cols_vif(**context):
    ti = context['ti']
    xcom_value = ti.xcom_pull(task_ids = 'extract_riot_api')
    df = pd.DataFrame(xcom_value)
    df = df[['summonerId', 'summonerName', 'queueType']]
    df.rename(columns = {'summonerId': 'summoner_id', 'summonerName': 'summoner_name', 'queueType': 'QType'}, inplace = True)

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

def check_df_info(**context):
    ti = context['ti']
    xcom_value = ti.xcom_pull(task_ids = 'extract_riot_api')
    df = pd.DataFrame(xcom_value)
    
    DQ = DataFrameQualityChecker(df)
    check_df = DQ.check_data_quality()

    total_rows = len(df)
    missing_values_sum = check_df['Missing_Values'].sum()
    missing_percentage = (missing_values_sum / total_rows) * 100    

    if df is None or missing_percentage >= 20:    
        logging_err()
        return 'stop'
    else:
        return 'continue_'

def logging():
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    text = f"{formatted_datetime}. extract data from api SUCCESS"
    byte_text = text.encode('utf-8')   
    producer = KafkaProducer(bootstrap_servers = brokers) 
    producer.send(topicname, byte_text)
    producer.flush()
    return print(text)

def logging_err():
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    text = f"{formatted_datetime}. too many missing value. pipeline STOP"
    byte_text = text.encode('utf-8')   
    producer = KafkaProducer(bootstrap_servers = brokers) 
    producer.send(topicname2, byte_text)
    producer.flush()
    return print(text)

# DAG skeleton
with DAG(dag_id = dag_id,
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

    check_data_stability = BranchPythonOperator(
        task_id = 'check_data_stability',
        python_callable = check_df_info,
        provide_context = True,
        dag = dag
    )

    check_data_vif = PythonOperator(
        task_id = 'check_data_vif',
        python_callable = check_cols_vif,
        dag = dag
    )

    logging_pipeline = PythonOperator(
        task_id = 'kafka_logging_pipeline',
        python_callable = logging,
        dag = dag
    )

    err_logging_pipeline = PythonOperator(
        task_id = 'kafka_err_logging_pipeline',
        python_callable = logging_err,
        dag = dag
    )    

    stop = DummyOperator(
        task_id = 'stop',
        dag = dag,
    )

    continue_ = DummyOperator(
        task_id = 'continue_',
        dag = dag,
    )
    
    
api_check >> extract_data >> check_data_stability 

check_data_stability >> [stop, continue_]

continue_ >> process_api_data >> logging_pipeline

stop >> err_logging_pipeline
