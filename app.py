from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api

from config import Config
from resources.movie import  MovieResource, MovieListResource
from resources.rating import RatingInfoResource, RatingResouce
from resources.review import RatingListResource
from resources.search import SearchResource
from resources.user import UserLoginResource, UserLogoutResource, UserRegisterResource, jwt_blacklist

app = Flask(__name__)

# 환경변수 세팅
app.config.from_object(Config)

# JWT 토큰 라이브러리 만들기
jwt = JWTManager(app)

# 로그아웃 된 토큰이 들어있는 set을 jwt에 알려준다.
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload) :
    jti = jwt_payload['jti']
    return jti in jwt_blacklist

api = Api(app)

api.add_resource(UserRegisterResource, '/users/register')
api.add_resource(UserLoginResource, '/users/login')
api.add_resource(UserLogoutResource, '/users/logout')
api.add_resource(MovieListResource, '/movie')
api.add_resource(MovieResource,'/movie/<int:movie_id>')
api.add_resource(RatingListResource, '/movie/<int:movie_id>/rating')
api.add_resource(SearchResource, '/search')
api.add_resource(RatingResouce, '/ratings/<int:movie_id>')
api.add_resource(RatingInfoResource, '/ratings/<int:rating_id>')


if __name__ == "__main__" :
    app.run()