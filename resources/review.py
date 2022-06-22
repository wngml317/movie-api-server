from flask import request
from flask_restful import Resource
from mysql.connector.errors import Error
import mysql.connector
from mysql_connection import get_connection


class RatingListResource(Resource) :
    def get(self, movie_id) :

        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try :
            connection = get_connection()

            query = '''select m.title, u.name, u.gender, r.rating
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
                "result_list" : result_list }, 200