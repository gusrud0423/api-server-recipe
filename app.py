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
from resources.recipe import RecipeListResource
                    # 클래스 먼저 쓰고 경로 
api.add_resource(RecipeListResource, '/recipes') # api 설계를 보고 쓴것


if __name__ == "__main__" :
    app.run(port=5003)