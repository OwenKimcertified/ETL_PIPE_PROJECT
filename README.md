# ETL_PIPE_PROJECT

from api, processing data

ETL PROCESS logging (kafka), nosql 에 저장 (original data) 

kafdrop 을 이용하여 broker 의 관리를 용이하게, log centre 로 활용

data 의 vif 계수와 data 의 stability 를 측정하는 module 추가.

조건에 따라 다음 task가 실행되도록 branchoperator 설정.
 
dags unit test 추가. (pytest)

![image](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/6963d958-0fc2-4835-95a9-a643fb64a813)
![image](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/6816079b-cfe4-40c2-8322-6abea730fd8e)
![image](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/c2a14085-75e1-49ab-ba1f-4a51e7796c38)
![image](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/cf63ddcd-aa62-4c73-9b9b-196f52f3c714)
![image](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/54dbca2e-a140-4bbe-8803-967979a1f26e)
![image](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/74ab439a-ebb7-446e-90d6-e319a2243df6)
# airflow dags 
![스크린샷 2023-09-15 03-58-19](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/70992f7e-f841-4927-9e94-88320b30c764)
# airflow dags tree
![스크린샷 2023-09-16 00-50-09](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/ce7a929b-601f-4999-bf48-8dd80bcd5194)
# kafdrop ( log centre )
![567a](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/a264b46f-192f-43ba-8131-25b83cd8726a)
# python kafka streaming 
![888a](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/0242e35d-da4e-4bf7-8b82-6e78bf60795b)

### error, issue list (clear)
airflow 에서 pandas series serialize 문제 
- airflow 에서 task 간 xcom 시 json serialize 하는데, pandas series 는 json serialize 할 수 없음
- airflow config 에서 enable_xcom_pickling = True 하게되면 serialize 할 때 json 이 아닌 pickle 방식으로 진행해 복잡한 객체도 serialize 가능

airflow 에서 mysql 과 연결이 안되는 경우 (sqlalchemy 관련)
- airflow config 에서 sqlalchemy_conn = 관련 주소를 설정

orm 은 무엇이고 왜 써야했는가
- 쉽게 말해, orm 은 파이썬 - SQL 간 통역사 역할을 하고 프로그래밍 언어와 db 간 상호작용을 도와줌.
- orm 을 쓰면 객체 지향적이고, 프로그래밍 언어와 db 간 일관성을 유지하게 함.
- 정리하면 객체 지향 이라는 관점과, 관계형 이라는 관점을 통합시키기 위해 사용했음.
### issue list 
데이터를 저장할 때에는 한 줄씩 루프를 돌아가며 인젝하는 방식밖에 없을까? 
- 데이터의 양이 많다면 분명 문제가 있을 것 같은데 해결 방법을 모르겠다.
