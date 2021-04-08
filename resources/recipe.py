from flask import request
from flask_restful import Resource
from http import HTTPStatus

from db.db import get_mysql_connection

# JWT 라이브러리
from flask_jwt_extended import jwt_required, get_jwt_identity

# 우리가 이 파일에서 작성하는 클래스는,
# 플라스크 프레임워크에서 , 경로랑 연결시킬 클래스입니다.
# 따라서, 클래스 명 뒤에, Resource 클래스를 상속 받아야 합니다.
# 플라스크 프레임워크의 레퍼런스 사용법에 나와 있습니다.
                        # 상속받다 >> 이프레임 워크에서 정해놓은 규칙대로 하겠다 라는 뜻
class RecipeListResource(Resource) :
    # 이건 로그인 되어있지 않아도 다 볼수 있다 !!
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

                            # 유저 아이디를 레시피 테이블에 추가하고 유저아이디로 유저테이블과 연결
                            #  유저아이디 정보는 토큰에 들어가 있음 
     # 로그인한 유저만 이 API 이용할수있음                  # 포스트맨 헤더에 토큰 있어야 함 
    @jwt_required()   # 자동으로 헤더에 토큰이 있는지 확인, 로그인 되어있는 사람만 레시피 생성하게 하고 !!
    def post(self) :  # 이건 post 메소드 실행하는것  

        # 1.클라이언트가 요청한 request의 포스트맨 body에 있는 json 데이터를 가져오기
        
        # ret = { "name" : "된장찌개", "description" : "된장찌개 끓이는 법", "num_of_servings" : 0,
        # "cook_time" : 40, "directions" : "물을 먼저 붓고, 두부도 넣고, 맛있게 끓여드세요",
        # "is_publish": 0 }
        
        data = request.get_json()
        # 제이슨의 어레이를 우리는 리스트로 받아온다 

        # 2. 필수 항목이 있는지 체크
        if 'name' not in data :
            return {'message': '필수값이 없습니다.' }, HTTPStatus.BAD_REQUEST  # 메세지를 적을지 말지는 개발자 마음
                                                     # 클라이언트가 보낼때 네임이 없었으니 나쁜것이다 그러니 배드뜨게



        # JWT 인증 토큰에서 유저아이디 뽑아온다  # 다시 추가됨 
        user_id = get_jwt_identity()                                             
        
        #  user_id 추가후 포스트맨 레시피 생성하는 api 에서 바디가 {된장찌개~~~} 똑같이 하고 샌드하면 
        # "msg": "Token has expired" 나옴 토큰이 시간이 지나 만료 되었다는 뜻 

        # 3. 데이터베이스 커넥션 연결  >> 여기서 디비는  여기 있는 파일 db에 db.py 를 뜻한다
        connection = get_mysql_connection() 

        # 4. 커서 가져오기
        cursor = connection.cursor(dictionary=True)  # 딕셔너리 형태로 받아오자

        # 5. 쿼리문 만들기
        query = """insert into  recipe ( name, description, num_of_servings, cook_time, directions, is_publish, user_id )
                    values ( %s , %s, %s,%s, %s, %s, %s);"""
        
        param = ( data['name'], data['description'], data['num_of_servings'], data['cook_time'], data['directions'], data['is_publish'], user_id )

        # 6. 쿼리문 실행
        c_result = cursor.execute(query, param)  # 위에 입력한 결과 받기
        print(c_result)                 

        connection.commit()

        # 7. 커서와 커넥션 닫기
        cursor.close()
        connection.close()
        
        # 8. 클라이언트에 reponse 하기  
         #return {}   이렇게 했을 때 포스트맨에서 레시피생성하는 api 창에서 {} 나오면 되고 이거 잘 나오면 
                       # 모든 레시피 가져오는 포스트 맨에서 샌드 했을 때 된장찌개 가 나와야 함 왜냐면 레시피생성api 에서 바디에 추가했기 때문이다 
                        # 워크밴치가서 테이블 확인하면 들어가져 있다 
        return {'err_code' : 0}, HTTPStatus.OK




class RecipeResource(Resource) :
    
    def get(self, recipe_id) :
                # localhost:5000/recipes/1
        # 1. 경로에 붙어있는 값을 가져와야 한다. >> 레시피 테이블의 아이디를 가져와야한다  
        # ex ) http://locallhost:5000/1 여기서 1은 테이블의 한개만 가져와라 니까 1번 아이디를 가져오게됨
        # 위의 get 함수의 파라미터로 지정해준다

             # 레시피의 정보를 가져온다 
        data = request.args
        print(data)

        # 2. DB 커넥션 가져온다
        connection =  get_mysql_connection()

        # 3. 커서 가져오고
        cursor = connection.cursor(dictionary=True)  # 딕셔너리 형태로 받아오자

        # 4. 쿼리문 만들고
        query = """select name, description, num_of_servings, cook_time, directions, is_publish, 
                date_format(created_at, '%Y-%m-%d %H:%i:%S') as created_at,
                date_format(updated_at, '%Y-%m-%d %H:%i:%S') as updated_at
                from recipe where id = %s;"""
                # 이거 시간에 있는 %d , %i, %s 가 입력받는걸로 되어있으면 안되고 자동으로 되어있게 끔 해야 하는데 그방법이다
        
        # query = """select name, description, num_of_servings, cook_time, directions, is_publish, 
        #         date_format(created_at, '%Y-%m-%D %T') as created_at,
        #         date_format(updated_at, '%Y-%m-%D %T') as updated_at
        #         from recipe where id = %s;"""

        param =  ( recipe_id, )  # 콤마 넣어야 튜플로 인정됨

        # 5. 쿼리 실행
        c_result = cursor.execute(query, param)  

        records = cursor.fetchall()   # 위에 쿼리문 실행한 결과를 레코드에 넣어짐 

        # 7. 커서와 커넥션 닫기
        cursor.close()
        connection.close() 


        # 7. 실행 결과를 클라이언트에 보내준다
        # 우리는 한개가 들어있는것을 알지만 반복문 써야 된다 

        if len(records) == 0 :        # 쿼리가 0 이면 아무것도 안가져오는 경우이니 에러 뜨지 않게 예외 처리해줘야 한다 
            return {'message' : '패스로 세팅한 레시피 아이디는 없다.'}, HTTPStatus.BAD_REQUEST

        # result = []
        # for row in records :
        #     row['created_at'] = row['created_at'].isoformat()
        #     row['updated_at'] = row['updated_at'].isoformat()
        #     result.append(row)

        return {'count' : len(records), 'ret': records[0] }




    def put(self, recipe_id) :
        
        #  업데이터 함수 작성  
        # 근데 바로위에 만든 함수와 같이 경로가 똑같은데 요리시간하고 디렉션을 어떻게 가져와서 바꾸지?
        # 포스트맨에 바디를 이용하자 { "cook_time": 60, "directions": "마지막에 물을 두컵 더 부으세요" } 

        # 요리시간과 direction 만 업데이트 할 수 있도록 해주세요.

        # 요리 시간과 direction 은 필수값 입니다.  >> 까지 조건

        # 이건 같은 localhost:5003/recipes/1 이경로에서 업데이트하고 바꾸는 거니까 클래스를 변경할 필요가 없음 위에것이랑 이어지는것 
        data = request.get_json()

        # 두개가 없다면 이렇게 처리하고 
        if 'cook_time' not in data or 'directions' not in data :
            return {'message' :  '파리미터 잘못됬습니다.'}, HTTPStatus.BAD_REQUEST

        # 있다면 이렇게 처리해라
        # 2. DB 커넥션 가져온다
        connection =  get_mysql_connection()

        # 3. 커서 가져오고
        cursor = connection.cursor(dictionary=True)  # 딕셔너리 형태로 받아오자


        # 4. 쿼리문 만들고
        query = """update recipe 
                    set cook_time = %s, directions = %s
                    where id = %s;"""

        param = (data['cook_time'], data['directions'], recipe_id)

        # 5. 쿼리 실행
        c_result = cursor.execute(query, param)  

        connection.commit()   

        # # 7. 커서와 커넥션 닫기
        cursor.close()
        connection.close()   

        return {}, HTTPStatus.OK
        # 포스트맨에서  localhost:5003/recipes/1 로 해놓고 샌드누르고 전체레시피 가져오는 포스트맨 보니 이렇게 업데이트 되었다
        # #[{
        #             "id": 1,
        #             "name": "김치찌개",
        #             "description": "맛있게 만드는 방법",
        #             "num_of_servings": null,
        #             "cook_time": 60,
        #             "directions": "마지막에 물을 두컵 더 부으세요",
        #             "is_publish": null,
        #             "created_at": "2021-04-06T05:30:51",
        #             "updated_at": "2021-04-06T05:30:51"
        #         }
    
    
    def delete(self, recipe_id) :

        connection = get_mysql_connection()

        cursor = connection.cursor()

        query = """delete from recipe where id = %s;"""

        param = (recipe_id, )

        cursor.execute(query, param)

        connection.commit()

        cursor.close()
        connection.close()

        return {}, HTTPStatus.OK
        ## 삭제는 바디에 안쓴다 !!!!!!!!!!!!!! 바디 써서 삭제 할려면 포스트로 해야됨

        # localhost:5003/recipes/1  하니 레시피 삭제 api 에서는  {}  출력되고 
        # 전체 레시피 보여주는 api 에서는  1번 이 지워졌기 때문에 이렇게 출력된다 
        #         {
        #     "count": 2,
        #     "ret": [
        #         {
        #             "id": 2,
        #             "name": "돈까스",
        #             "description": "치즈돈까스 만드는 방법",
        #             "num_of_servings": 0,
        #             "cook_time": 50,
        #             "directions": "고기를 잘 써야한다",
        #             "is_publish": 0,
        #             "created_at": "2021-04-07T00:48:09",
        #             "updated_at": "2021-04-07T00:48:09"
        #         },
        #         {
        #             "id": 3,
        #             "name": "된장찌개",
        #             "description": "된장찌개 끓이는 법",
        #             "num_of_servings": 0,
        #             "cook_time": 40,
        #             "directions": "물을 먼저 붓고, 두부도 넣고, 맛있게 끓여드세요",
        #             "is_publish": 0,
        #             "created_at": "2021-04-07T01:01:56",
        #             "updated_at": "2021-04-07T01:01:56"
        #         }
        #     ]
        # }






class RecipePublishResource(Resource) :

    # is_publis 를 1 로 변경해주는 함수
    def put(self, recipe_id) :

        connection = get_mysql_connection()
        cursor= connection.cursor()
        query =  """update recipe set is_publish = 1 where id = %s;"""
        param = (recipe_id, )
        cursor.execute(query, param)
        connection.commit()
        cursor.close()
        connection.close()
        return {}, HTTPStatus.OK

        
        # is_publish 를 0으로 변경해주는 함수
    def delete(self, recipe_id) :

        connection = get_mysql_connection()
        cursor= connection.cursor()
        query =  """update recipe set is_publish = 0 where id = %s;"""
        param = (recipe_id, )
        cursor.execute(query, param)
        connection.commit()
        cursor.close()
        connection.close()
        return {}, HTTPStatus.OK

        #  위에 실행하면 이렇게 id가 2인 is_publish 가 0으로 바뀌는데 다시 1로 바뀌는것 하고 전체 api 포스트맨에서 보면 1로 변경되어잇다
        # {
        #     "id": 2,
        #     "name": "돈까스",
        #     "description": "치즈돈까스 만드는 방법",
        #     "num_of_servings": 0,
        #     "cook_time": 50,
        #     "directions": "고기를 잘 써야한다",
        #     "is_publish": 0,
        #     "created_at": "2021-04-07T00:48:09",
        #     "updated_at": "2021-04-07T00:48:09"
        # }


        







#  클라이언트가 무슨 행동을 하던 서버에 일단 get 이든 뭐든 요청해서 클라이언트에게 다시 원하는것 api 주소를 주고 클라이언트는 그것으로 화면에 호출하게 된다 