from flask import request
from flask_restful import Resource
from http import HTTPStatus

from db.db import get_mysql_connection

# 우리가 이 파일에서 작성하는 클래스는,
# 플라스크 프레임워크에서 , 경로랑 연결시킬 클래스입니다.
# 따라서, 클래스 명 뒤에, Resource 클래스를 상속 받아야 합니다.
# 플라스크 프레임워크의 레퍼런스 사용법에 나와 있습니다.
                        # 상속받다 >> 이프레임 워크에서 정해놓은 규칙대로 하겠다 라는 뜻
class RecipeListResource(Resource) :
    # get 메소드로 연결시킬 함수 작성.
    def get(self) :    # 이건 get 메소드 실행하기 위해 기본으로 해야하는것
        # recipe 테이블에 저장되어 있는 모든 레시피 정보를 가져오는 함수

        # 1. DB 커넥션을 가져온다
        connection = get_mysql_connection()

        # 2. 커넥션에서 커서를 가져온다
        cursor = connection.cursor(dictionary=True)

        # 3. 쿼리문을 작성한다
        query = """select * from recipe;"""

        # 4. sql 실행
        cursor.execute(query)

        # 5. 데이터를 패치한다.  (위에서 실행한 결과를 레코드에 담는다)
        records = cursor.fetchall()

        print(records)

        # 레코드는 리스트 형태이니 포문 가능  그리고 created_at, updated-at 때문에 오류나니 설정해야함
        ret = [] 
        for row in records :
            row['created_at']= row['created_at'].isoformat()
            row['updated_at'] = row['updated_at'].isoformat()
            ret.append(row)                #>> 이 코드 중요하다 뭐하는건지 알아야 해 

        # # 6. 커서와 커넥션을 닫아준다
        cursor.close()
        connection.close()
        
        
        
        # 7. 클라이언트에 리스판스 한다
        return {'count':len(ret), 'ret' : ret }, HTTPStatus.OK

    def post(self) :  # 이건 post 메소드 실행하는것

        # 1.클라이언트가 요청한 request의 포스트맨 body에 있는 json 데이터를 가져오기
        ret = { "name" : "된장찌개", "description" : "된장찌개 끓이는 법", "num_of_servings" : 0,
        "cook_time" : 40, "directions" : "물을 먼저 붓고, 두부도 넣고, 맛있게 끓여드세요",
        "is_publish": 0 }
        # 2. 필수 항목이 있는지 체크

        # 3. 데이터베이스 커넥션 연결
        connection = get_mysql_connection() 

        # 4. 커서 가져오기
        cursor = connection.cursor(dictionary=True)

        # 5. 쿼리문 만들기
        query = """select * from recipe;"""

        # 6. 쿼리문 실행
        cursor.execute(query)

        # 7. 커서와 커넥션 닫기
        cursor.close()
        connection.close()
        
        # 8. 클라이언트에 reponse 하기  
        return {'count':len(ret), 'ret' : ret }, HTTPStatus.OK
