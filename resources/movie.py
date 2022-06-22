from flask import request
from flask_restful import Resource
from mysql.connector.errors import Error
import mysql.connector
from mysql_connection import get_connection


class MovieListResource(Resource) :

    def get(self) :
        # 1. 클라이언트로부터 데이터를 받아온다.
        # request.args는 딕셔너리이다.
        offset = request.args['offset']
        limit = request.args['limit']
        order = request.args['order']


        # 2. 디비로부터 영화 정보를 가져온다.
        # 리뷰 갯수, 별점 평균 별
        try :
            connection = get_connection()

            query = '''select m.id, m.title, 
                    count(r.movieId) as cnt, ifnull(avg(r.rating), 0) as avg
                    from movie m
                    left join rating r
                    on m.id = r.movieId
                    group by m.id
                    order by {} desc
                    limit {}, {};'''.format(order, offset, limit)


            # select 문은 dictionary=True 를 해준다.
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, )

            result_list = cursor.fetchall()
            print(result_list)

            i=0
            for record in result_list :
                result_list[i]['avg'] = float(record['avg'])
                i = i + 1   

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

class MovieResource(Resource) :

    def get(self, movie_id) :

        # 디비로부터 영화 상세 정보를 가져온다.
        try :
            connection = get_connection()

            query = '''select m.*, 
                    ifnull( avg(r.rating), 0) as avg, 
                    count(r.movieId) as cnt
                    from movie m
                    left join rating r
                    on m.id = r.movieId
                    where m.id = %s
                    group by m.id;'''
            record = (movie_id, )

            # select 문은 dictionary=True 를 해준다.
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, record)

            # select 문은 아래 함수를 이용해서 데이터를 가져온다.
            result_list = cursor.fetchall()
            print(result_list)

            i=0
            for record in result_list :
                result_list[i]['year'] = record['year'].isoformat()
                result_list[i]['avg'] = float(record['avg'])
                i = i + 1  

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()

            return { "error" : str(e) }, 503

        return {'result' : 'success',
                'item' : result_list[0]}, 200