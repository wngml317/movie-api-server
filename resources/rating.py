from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
import mysql.connector
from mysql_connection import get_connection


class RatingResouce(Resource) :

    @jwt_required()
    def post(self, movie_id) :

        data = request.get_json()
        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            # 먼저 별점을 준 영화인지 확인
            query = '''select * from rating
            where userId = %s and movieId = %s;
            '''

            record=(user_id, movie_id)

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

            
            if len(result_list) == 1 :
                
                cursor.close()
                connection.close()
                return {"error" : "이미 별점을 주었습니다.."}

            query = '''insert into rating
                    (userId, movieId, rating)
                    values
                    (%s, %s, %s);'''

            record = (user_id, movie_id, data['rating'])

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


class RatingInfoResource(Resource) :
    @jwt_required()
    def put(self, rating_id) :

        data = request.get_json()
        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''update rating set rating=%s
                    where id = %s;'''

            record = (data['rating'], rating_id)

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
