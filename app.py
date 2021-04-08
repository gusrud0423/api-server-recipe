# from flask import Flask

# from db.db import get_mysql_connection

# app = Flask(__name__) 

#  get_mysql_connection()


# if __name__ == "__main__" :
#     app.run()

#############################################

from flask import Flask
from flask_restful import Api

from db.db import get_mysql_connection

from config.config import Config

app = Flask(__name__) 

# 1. 환경변수 설정
app.config.from_object( Config )

# 2. API 설정
api = Api(app)

# 3. 경로(path)랑 리소스(resource)를 연결한다.
# /recipes
from resources.recipe import RecipeListResource , RecipeResource, RecipePublishResource
from resources.user import UserListResource
                    # 라이브러리 임폴트 하고 나서 
                    # 클래스 먼저 쓰고 경로 
api.add_resource(RecipeListResource, '/recipes') # api 설계를 보고 쓴것 , 모든 레시피를 다가져온다
api.add_resource(RecipeResource, '/recipes/<int:recipe_id>') # 이건 레시피 아이디를 가져오는것
                                    # 경로에 변수처리 recipe.py 에 get 함수에 지정되어있음 self, recipe_id
                                    # 원하는 정보가 다르니 경로가 다르다 
api.add_resource(RecipePublishResource, '/recipes/<int:recipe_id>/publish')


# user
api.add_resource(UserListResource, '/users')
api.add_resource(UserResource, '/users/login')


if __name__ == "__main__" :

    

    app.run(port=5003)