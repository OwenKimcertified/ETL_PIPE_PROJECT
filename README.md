# ETL_PIPE_PROJECT
from api, processing data

ETL PROCESS logging (kafka), nosql 에 저장 (original data) 

kafdrop 을 이용하여 broker 의 관리를 용이하게, log centre 로 활용

data 의 vif 계수와 data 의 stability 를 측정하는 module 추가.
 
dags unit test 추가 (pytest)
# airflow dags 
![123a](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/97d50237-6549-4f89-bffd-debb7ee5dc92)
# airflow dags tree
![234a](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/5ef92e45-e099-41b7-ba70-1b6fed1b5752)
# kafdrop ( log centre )
![567a](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/cab8913c-ba2b-46d8-9d60-c9b05a3d2b0c)
# python kafka streaming 
![888a](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/868b2942-0dbd-443d-a19f-078304ba0ef8)

### error list (clear)
airflow 에서 pandas series serialize 문제 
- airflow 에서 task 간 xcom 시 json serialize 하는데, pandas series 는 json serialize 할 수 없음
- airflow config 에서 enable_xcom_pickling = True 하게되면 serialize 할 때 json 이 아닌 pickle 방식으로 진행해 복잡한 객체도 serialize 가능


