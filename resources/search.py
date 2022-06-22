from flask import request
from flask_restful import Resource
from mysql.connector.errors import Error
import mysql.connector
from mysql_connection import get_connection

class SearchResource(Resource) :
    def get(self) :
        
        keyword = request.args.get('keyword')

        try :
            connection = get_connection()

            query = '''select m.title, count(r.rating), avg(r.rating)
                    from rating r
                    join movie m
                    on r.movieId = m.id
                    group by r.movieId having m.title like '%{}%';'''.format(keyword)

            # select 문은 dictionary=True 를 해준다.
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, )

            result_list = cursor.fetchall()
            print(result_list) 

            i=0
            for record in result_list :
                result_list[i]['avg(r.rating)'] = float(record['avg(r.rating)'])
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
                "result_list" : result_list }, 200