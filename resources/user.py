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

        except Error as e:
            print(str(e))
            return {'err_code': 4 }, HTTPStatus.NOT_ACCEPTABLE

        cursor.close()
        connection.close()

        return {} , HTTPStatus.OK
# 이거하고 app.py에서 경로 연결 해야함



# 로그인 API
class UserResource(Resource) :

    def post(self) :

        def post(self) :

            # 1. 클라이언트로 부터 이메일과 비밀번호를 받아온다 (json 데이터 가져오기)
            data =  request.get_json
            if 'email' not in data or 'password' not in data :
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

            query = """select password from user where email = %s;"""
            param = (data['email'], )

            cursor.execute(query, param)
            records = cursor.fetchall()

             
            # 4. 위에서 가져온 디비에 저장되어있는 비밀번호와, 클라이언트로 부터 받은 비밀번호를 암호화 한것과 비교 checkpassword 함수가 있음
            password = data['password']
            hashed =  records[0]['password']
            ret = check_password(password, hashed)
             

            # 5. 같으면 클라이언트에 200 리턴
            if ret is True :
                return {}, HTTPStatus.OK
             

            # 6. 다르면, 에러 리턴 
            else :
                return {'err_code' : 3}, HTTPStatus.BAD_REQUEST


            