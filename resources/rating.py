from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
import mysql.connector
from mysql_connection import get_connection


class RatingListResouce(Resource) :

    @jwt_required()
    def post(self) :

        # 1. 클라이언트로부터 데이터를 받아온다.
        # {
        #     "movieId" : "32",
        #     "rating" : "3"
        # }
        data = request.get_json()
        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            # 먼저 별점을 준 영화인지 확인
            query = '''select * from rating
            where userId = %s and movieId = %s;
            '''

            record=(user_id, data['movieId'])
            print(record)

            cursor = connection.cursor(dictionary=True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

            
            if len(result_list) == 1 :
                
                cursor.close()
                connection.close()
                return {"error" : "이미 별점을 주었습니다."}

            # 2. 디비에 insert
            query = '''insert into rating
                    (userId, movieId, rating)
                    values
                    (%s, %s, %s);'''

            record = (user_id, data['movieId'], data['rating'])

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

    @jwt_required()
    def get(self) :

        # 1. 클라이언트로부터 데이터를 받아온다.
        # ?offset=0&limit=25
        offset = request.args['offset']
        limit = request.args['limit']

        user_id = get_jwt_identity()

        # 2. 내 리뷰리스트를 디비에서 가져온다.
        try :
            connection = get_connection()

            query = '''select m.title, r.rating
                    from rating r
                    join movie m 
                    on r.movieId = m.id and r.userId = %s
                    order by r.rating desc
                    limit {}, {};
                    '''.format(offset, limit)

            record=(user_id, )

            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()
            print(result_list)

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()

            return { "error" : str(e) }, 503

        return {"result" : "success",
                "count" : len(result_list),
                "items" : result_list}, 200

class MovieRatingResource(Resource) :
    def get(self, movie_id) :

        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try :
            connection = get_connection()

            query = '''select u.name, u.gender, r.rating
                    from rating r
                    join movie m
                    on r.movieId = m.id
                    join user u
                    on r.userId = u.id
                    where r.movieId = %s
                    limit {}, {};'''.format(offset, limit)

            record = (movie_id, )

            # select 문은 dictionary=True 를 해준다.
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()
            print(result_list) 

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()

            return { "error" : str(e) }, 503

        return { "result" : "success", 
                "count" : len(result_list) ,
                "items" : result_list }, 200

class RatingInfoResource(Resource) :
    
    # 로그인한 유저 별점 수정
    
    @jwt_required()
    def put(self, rating_id) :

        data = request.get_json()
        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''update rating set rating=%s
                    where userId = %s and id = %s;'''

            record = (data['rating'], user_id, rating_id)

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


    # 로그인한 유저 별점 삭제
    @jwt_required()
    def delete(self, rating_id) :

        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''delete from rating
                    where userId = %s and id = %s'''

            record = (user_id, rating_id)

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

