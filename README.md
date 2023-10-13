# ETL_PIPE_PROJECT

이 프로젝트는 API server 에서 데이터를 요청받고

요청한 데이터를 처리, 저장하는 ETL_PIPELINE 에 대한 기록입니다.

Airflow 사용으로 task 를 자동화, 조건에 따른 task 를 결정을 구현하고   

처리된 데이터를 안전하게 RDB(MySQL), MongoDB(NoSQL) 로 이동시키는 PIPELINE 을 구축했습니다.

본 프로젝트에는 사용하지 않은 수치형 데이터에 활용 가능한 vif 계수 측정,

본 프로젝트에 사용한 data stability 를 측정하는 모듈을 추가하고 

orm 으로 db 에 trasaction 하여  데이터의 ACID 를 지키려 노력했습니다.

Kafka 와 Kafdrop 을 이용하여 로그 처리에 이용했고 

kafka 의 경우 cli 로 로깅 기록을 확인할 수 있지만 다소 번거로운 단점을 상쇄하고자

kafdrop 을 추가해 log centre 처럼 운용하여 GUI 로 쉽게 로그를 확인할 수 있도록 했습니다.
 
마지막으로 pytest 를 이용하여 안정적인 작업이 가능하도록 했습니다.

# PPT 
![슬라이드1](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/9862d9cf-7a74-4b3e-a6ea-f44328bfb1f8)
![슬라이드2](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/d706a0f6-d70b-470d-a29f-475cd531eb18)
![슬라이드3](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/43e3ca71-9b72-4acb-a827-fd6184ec9bc1)
![슬라이드4](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/f8821a00-2e77-40c8-936e-058ae8c8a7e4)
![슬라이드5](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/116d3b76-b510-4a38-ad74-6e1c4addbb0c)
![슬라이드6](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/ecf5ee0c-4d24-4f04-92cc-b5f9cf38745c)
![슬라이드7](https://github.com/OwenKimcertified/ETL_PIPE_PROJECT/assets/99598620/3ee58519-e417-4a59-8766-d2c96e67c554)


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

airflow 관련 error
sqlalchemy 관련 rdb 연결 불가 case
- airflow config 에서 sqlalchemy_conn = 관련 주소를 설정

airflow 에 module 추가 설치
- apache-airflow-providers-<provider-name> 로 pip install
- aws provider 를 설치 시 pip install apache-airflow-providers-amazon 

! MySQL Error (HY000) : Can`t connect to local MySQL server through socket 'var/run/mysqld/mysqld.sock'(2)

고전했던 error 이고 확인해본 것들은 3가지

1. MySQL 데몬 실행확인

systemctl stop mysqld

chmod -R 755 /var/lib/mysql

chown -R mysql:mysql /var/lib/mysql

systemctl start mysqld

순서대로 실행

2. my.cnf config 파일 확인

2 번의 case 였고 nano cli 로 내용을 수정

clinet = /var/lib/mysql/mysql.sock

socket = /var/lib/mysql/mysql.sock

3. mysql.sock 경로, 시스템이 찾지 못 함.

심볼릭 링크 생성

ln -s /tmp/mysql.sock /var/lib/mysql/mysql.sock

4. airflow connection 확인

admin 버튼에 hover 시 Connection 이 있는데 그 부분에 추가, 수정을 한다.

구글링을 해본 결과 이 오류는 다양한 이유로 발생하는 것 같은데 다른 사람들은 만나지 않았으면 한다.

orm 은 무엇이고 왜 써야했는가
- 쉽게 말해, orm 은 파이썬 - SQL 간 통역사 역할을 하고 프로그래밍 언어와 db 간 상호작용을 도와줌.
- orm 을 쓰면 객체 지향적이고, 프로그래밍 언어와 db 간 일관성을 유지하게 함.
- 정리하면 객체 지향 이라는 관점과, 관계형 이라는 관점을 통합시키기 위해 사용했음.

aws ec2, rds 를 사용한다면
- rds 주소를 리팩토링
- aws ec2 에 도커 이미지를 옮기고 관련 세팅 후 켜두면 해결

### issue list 
1. 데이터를 저장할 때에는 한 줄씩 루프를 돌아가며 인젝하는 방식밖에 없을까? 
- 데이터의 양이 많다면 분명 문제가 있을 것 같은데 해결 방법을 모르겠다.
- 단순히 배치처리를 하면 되지 않을까 하는 막연한 생각은 가지고 있는데 최선일까?
2. pytest 로 코드 테스팅은 했지만 트러블 슈팅을 못 하고 있다.

- CI 에 도움이 되고 있지만 트러블 슈팅으로 예외 상황을 처리할 수 있도록 하고 싶다.

- TDD 코드에 대해 공부하고 test 를 통과시키는 방식의 코딩스타일로 바꿔야겠다.
3. ELK Stack 도입 준비
프로젝트의 완성도를 위해 로그를 별도의 스택으로 관리 

이벤트 로그, 데이터를 수집하고 kibana 에서 대시보드로 확인할 수 있음

유저의 request 시간과 request 가 out 한 시간을 기록하여 성능 점검 가능

대용량 데이터에 대해서 전체 작업 중 실패한 작업에 대한 추적이 용이해질 것 같음

 
