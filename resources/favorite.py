from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
import mysql.connector
from mysql_connection import get_connection

class FavoriteResource(Resource) :
    
    @jwt_required()
    def post(self) :
        user_id = get_jwt_identity()
        data = request.get_json()
        try :
            # 1) DB에 연결
            connection = get_connection()

            # 2) 쿼리문 만들기
            query = '''insert into favorite
                    (userId, movieId)
                    values (%s, %s);'''
            record = (user_id, data['movieId'])

            # 3) 커서를 가져온다.
            cursor = connection.cursor()

            # 4) 쿼리문을 커서를 이용하여 실행
            cursor.execute(query, record)

            # 5) 커넥션을 커밋해준다. -> 디비에 영구적으로 반영
            connection.commit()

            # 6) 자원 해제
            cursor.close()
            connection.close()


        except mysql.connector.Error as e :
            print(e)
            cursor.close()

            connection.close()
            return {"error" : str(e), 'error_no' : 3}, 503

        return {"result" : "success"},200


class FavoriteInfoResource(Resource) :

    @jwt_required()
    def delete(self, favorite_id) :

        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''delete from favorite
                    where userId = %s and id = %s'''

            record = (user_id, favorite_id)

            cursor = connection.cursor()

            cursor.execute(query, record)

            connection.commit()

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()

            return { "error" : str(e) }, 503

        return { "result" : "success"}, 200