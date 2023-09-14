# ETL_PIPE_PROJECT PPT 제작 중
from api, processing data

ETL PROCESS logging (kafka), nosql 에 저장 (original data) 

kafdrop 을 이용하여 broker 의 관리를 용이하게, log centre 로 활용

data 의 vif 계수와 data 의 stability 를 측정하는 module 추가.

조건에 따라 다음 task가 실행되도록 branchoperator 설정.
 
dags unit test 추가. (pytest)
# airflow dags 
![스크린샷 2023-09-15 03-58-19](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/70992f7e-f841-4927-9e94-88320b30c764)
# airflow dags tree
![스크린샷 2023-09-15 03-58-35](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/956e08c7-b327-4c6c-bda1-663ab3d7b603)
# kafdrop ( log centre )
![567a](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/a264b46f-192f-43ba-8131-25b83cd8726a)
# python kafka streaming 
![888a](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/0242e35d-da4e-4bf7-8b82-6e78bf60795b)

### error list (clear)
airflow 에서 pandas series serialize 문제 
- airflow 에서 task 간 xcom 시 json serialize 하는데, pandas series 는 json serialize 할 수 없음
- airflow config 에서 enable_xcom_pickling = True 하게되면 serialize 할 때 json 이 아닌 pickle 방식으로 진행해 복잡한 객체도 serialize 가능

airflow 에서 mysql 과 연결이 안되는 경우 (sqlalchemy 관련)
- airflow config 에서 sqlalchemy_conn = 관련 주소를 설정

### issue list 
orm 은 무엇이고 왜 써야했는가
- 쉽게 말해, orm 은 파이썬 - sql 간 통역사 역할을 하고 프로그래밍 언어와 db 간 상호작용을 도와줌.
- orm 을 쓰면 객체 지향적이고, 프로그래밍 언어와 db 간 일관성을 유지하게 함.
- 정리하면 객체 지향 이라는 관점과, 관계형 이라는 관점을 통합시키기 위해 사용했음.
