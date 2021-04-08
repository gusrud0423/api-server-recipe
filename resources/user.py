# user 생기고 만듬 

from flask import request
from flask_restful import Resource 
from http import HTTPStatus
from db.db import get_mysql_connection

# 비밀번호 암호화 및 체크를 위한 함수 임포트
from utils import hash_password, check_password

# 이메일 체크하는 라이브러리
from email_validator import validate_email, EmailNotValidError

from mysql.connector import Error

# 비번용 라이브러리
from config.config import salt

# 유저인증을 위한 JWT 라이브러리 임포트    
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt

# 로그아웃 기능 구현
from flask_jwt_extended import get_jti
jwt_blocklist = set()  ## 얘가 로그인, 로그아웃 관리한다 




# 회원가입 API 
class UserListResource(Resource) :  
    
    def post(self) :
        
        # 먼저 데이터베이스에서 select * from user; 해보고 테이블 확인하고 
        # 포스트맨에서 회원가입 API 만들고 POST , localhost:5003/users 
        # body 가서 raw, json 형식 쓴후 새로 생성하는거라 
        # 바디에 새로들어갈것이 입력되어있어야 한다  {"username" : "홍길동", "email" : "abc@naver.com", "password" : "1234"} 이렇게 


        data = request.get_json()

        # 0. 데이터가 전부 다 있는지 체크
        if 'username' not in data or 'email' not in data or 'password' not in data :
            return {'err_code' : 1}, HTTPStatus.BAD_REQUEST


        # 1. 이메일 유효한지 체크

        try:
            # Validate.
            valid = validate_email(data['email'])

            
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            print(str(e))
            return {'err_code' : 3} , HTTPStatus.BAD_REQUEST

            # {"username" : "김나나", "email" : "ab+c@naver.com", "password" : "1234"} 이건 DB에 추가가 되는데 
            # @ 가 없어서 형식이 안맞으니 추가가 되지 않아서 err_code : 3 이 뜬다 

        # 2. 비밀번호 길이체크 및 암호화                     
        if len( data['password'] ) < 4 or len(data['password']) > 16 :  
            return {'err_code' : 2}, HTTPStatus.BAD_REQUEST

        password = hash_password(data['password'])

        # 3. 데이터 베이스에 저장 

        ## 실습 . 디비에 데이터 인서트 시, 유니크로 인해서 데이터가 들어가지지 않는 경우를 대비해 코드를 수정하세요
        ##  {"username" : "홍길동", "email" : "qqq@naver.com", "password" : "1234"} 이거 넣으려 하는데 김나나 가
        ## 이미 있어서 유니크로 처리되 데이터가 추가 되지 않으니 코드를 수정하는 것이다 

        ##  근데 이거 넣으면 DB에서 패스워드가 같아야 하는데 그이유?

        try:

            connection = get_mysql_connection()

            cursor = connection.cursor()

            query = """insert into user 
                        (username, email, password)
                        values (%s, %s, %s);"""

            param = (data['username'], data['email'], password)  # 패스워드는 2번에 password 로 암호화 했음 

            cursor.execute(query, param)
            connection.commit()


            # 디비에 데이터를 저장한후 저장된 아이디 값을 받아온다 
            user_id = cursor.getlastrowid()
            print(user_id)
        

        except Error as e:
            print(str(e))
            return {'err_code': 4 }, HTTPStatus.NOT_ACCEPTABLE

        
        cursor.close()
        connection.close()

        # JWT 를 이용해서 인증토큰을 생성해준다
        access_token = create_access_token(identity=user_id)

        return {'token': access_token} , HTTPStatus.OK  # 생성된 토큰은 무조건 클라이언트가 가지고 있어야 한다 
        # 토큰에는 유저 아이디 정보가 들어가있다

# 이거하고 app.py에서 경로 연결 해야함



class UserResource(Resource) :  

    # 로그인 API   
    def post(self) :
        
        # 1. 클라이언트로 부터 이메일과 비밀번호를 받아온다 (json 데이터 가져오기)
        data =  request.get_json() # 포스트맨에 이메일과 비밀번호를 바디에 적었다 그것을 가져온것 

        if 'email' not in data or 'password' not in data :   # 데이터에 이메일과 패스워드가 있는지 
            return {'err_code' : 1}, HTTPStatus.BAD_REQUEST
        

        # 2. 이메일 밸리데이션 체크
        try:
            # Validate.
            valid = validate_email(data['email'])

        
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            print(str(e))
            return {'err_code' : 2} , HTTPStatus.BAD_REQUEST


        # 3. 비밀번호가 맞는지 체크하기 위해서 데이터베이스에서 위의 이메일로 유저 정보를 가져온다 (select)
        connection =  get_mysql_connection()

        cursor = connection.cursor(dictionary= True)

        query = """select id, password from user where email = %s;"""  ## 패스워드만 보고싶으면 이대로 다보고 싶다 하면  * 로
        param = (data['email'], )

        cursor.execute(query, param)
        records = cursor.fetchall()   # 데이터에 이메일이 aaa @들어있는데 거기서 aaaa@새로운 이메일을 찾으려하면 못찾는다 그래서 레코드도 0이다 그거 처리하는것 써야한다 
        # print(records) 모르겠으면 찍어봐 
        
        
        # 3-1. 만약 회원가입이 안된 이메일로 요청했을 때는 , records에 데이터가 없으니까 클라이언트에게 응답한다
        if len(records) == 0 : # 0은 기존 데이터와 일치하는 데이터가 없다
            return {"err_code" : 3}, HTTPStatus.BAD_REQUEST 

            
        # 4. 위에서 가져온 디비에 저장되어있는 비밀번호와, 클라이언트로 부터 받은 비밀번호를 암호화 한것과 비교 checkpassword 함수가 있음
        password = data['password']
        hashed =  records[0]['password']  # 리스트(records)먼저 가서 딕셔너리[password]로 간다 # 디비에서 레코드에 담긴 패스워드를 가져옴 
        ret = check_password(password, hashed)
            

        # 5. 같으면 클라이언트에 200 리턴
        if ret is True :

            user_id = records[0]['id']   # 유저 아이디 생성후 추가 한것 
            access_token =create_access_token(identity= user_id)        # 이것도

            return {}, HTTPStatus.OK
            

        # 6. 다르면, 에러 리턴 
        else :
            return {'err_code' : 4}, HTTPStatus.BAD_REQUEST


        # 우리는 플라스크의 프레임워크 클래스인 리소스의 기능을 상속받아 유저스라는 클래스를 쓸수 있는 것이다 \




    # 내 정보 가져오는 API
    def get(self, user_id) :

        # 1. 데이터 베이스에서 쿼리해서 유저 정보 가져온다
        connection = get_mysql_connection()
        cursor =  connection.cursor(dictionary=True)
        query = """select id, username, email, is_active
                    from user
                    where id = %s;"""
        param = (user_id, )
        cursor.execute(query, param)
        records = cursor.fetchall()
                                                          # commit 는 뭔갈 삭제하거나 바꾸거나 할때만 
        cursor.close()
        connection.close()

        # 2. 유저정보 없으면, 클라이언트에 유저정보 없다고 리턴
        if len(records) == 0 :
            return {'err_code' : 1}, HTTPStatus.BAD_REQUEST

        # 3. 있으면, 해당 유저 정보를 리턴 
        else :
            return {'ret' : records[0]}, HTTPStatus.OK


