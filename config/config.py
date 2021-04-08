

# mysql 접속 정보를, 딕셔너리 형태로 저장한다.
db_config = { 'host' : 'database-1.cyfvtkkh7ho8.us-east-2.rds.amazonaws.com',
                'database' : 'yhDB',
                'user' : 'streamlit',
                'password' : 'yh1234' }
                

                # 이렇게 하면 보안이 높아진다 
# 클래스란 ? 변수(속성)과 함수(액션)로 구성된 것.
# 클래스를 만드는 이유 ? object를 있는 그대로 바라보는 관점.


# 개 
# 개의 속성 : 눈, 코, 입, 귀, 다리, 꼬리
# 개의 함수(액션=행동) : 짖는다, 문다, 꼬리친다

# 플라스크 앱의 설정용 클래스 
class Config : 
    DEBUG = True
    # PORT = 5003 이렇게 해놔도 set FLASK ~~ 안하면 실행이 안됨 그러니
    
    # 셋한다음에는 flask run 으로 실행해야 5003 으로 되고 아니면
  # app.py에 제일마지막 app.run(port=5003)으로 바꾸고 python app.py 해야지 5003으로 바뀐다.
    
    # JWT 용 시크릿 키
    SECRET_KEY = 'yuhyunkyoung_04_23'

  #### user 추가하고 나서
  # 비밀번호 암호화를 위한 salt 설정 => 해킹 방지를 위해서 
salt ="hello_test"