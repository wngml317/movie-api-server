from flask import request
from flask_restful import Resource
from mysql.connector.errors import Error
import mysql.connector
from mysql_connection import get_connection
from flask_jwt_extended import get_jwt_identity, jwt_required

import pandas as pd
import numpy as np

class MovieRecomResource(Resource) :
    
    @jwt_required()
    def get(self) :
        
        # 1. 클라이언트로부터 데이터를 받아온다.
        user_id = get_jwt_identity()

        # 2. 추천을 위한 상관계수 데이터프레임을 읽어온다.
        df = pd.read_csv('data/movie_correlations.csv', index_col= 'title')
        # print(df)
        
        # 3. 이 유저의 별점 정보를, 디비에서 가져온다.
        try :
            connection = get_connection()

            query = '''select r.userId, r.movieId, r.rating, m.title 
                    from rating r
                    join movie m 
                    on r.movieId = m.id
                    where userId = %s;'''

            record = (user_id, )

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

        # 디비로부터 가져온, 내 별점 정보를
        # 데이터프레임으로 만들어 준다.
        df_my_rating = pd.DataFrame(data=result_list)

        # 추천 영화를 저장할, 빈 데이터프레임을 만든다.
        similar_movie_list = pd.DataFrame()

        for i in range(len(df_my_rating)) :
            similar_movie = df[df_my_rating['title'][i]].dropna().sort_values(ascending=False).to_frame()
            similar_movie.columns = ['Correlations']
            similar_movie['Weight'] = df_my_rating['rating'][i] * similar_movie['Correlations']
            similar_movie_list = similar_movie_list.append(similar_movie)

        # 영화 제목이 중복된 영화가 있을 수 있다.
        # 중복된 영화는 Weight가 가장 큰(max)값으로 해준다.
        similar_movie_list.reset_index(inplace=True)
        
        similar_movie_list = similar_movie_list.groupby('title')['Weight'].max().sort_values(ascending=False)

        # 내가 이미 봐서, 별점을 남긴 영화는 여기서 제외해야 한다.
        
        # print(similar_movie_list)

        similar_movie_list= similar_movie_list.reset_index()

        # 내가 이미 본 영화 제목만 가져온다.
        title_list = df_my_rating['title'].tolist()

        # similar_movie_list 에 내가 본 영화인 title_list를 
        # 제외하고 가져온다.
        print(similar_movie_list)
        print(title_list)

        similar_movie_list['title'].isin(title_list)

        recomm_movie_list = similar_movie_list.loc[~similar_movie_list['title'].isin(title_list), ]

        print(recomm_movie_list.iloc[0 : 20, ])
        # json 형식으로 바꿔서 출력해준다.
        return {"result" : "success",
                "movie_list" : recomm_movie_list.iloc[0:20,].to_dict('records')}


# 실시간 영화 추천
class MovieRecomRealTimeResource(Resource) :

    @jwt_required()
    def get(self) :

        # 1. 클라이언트로부터 데이터를 받아온다.
        user_id = get_jwt_identity()
        
        # 2. 추천을 위한 상관계수를 위해, 데이터베이스에서 
        # 데이터를 먼저 가져온다.
        try :
            connection = get_connection()

            ### 실시간 추천을 위한 상관계수 데이터프레임을 읽어온다.
            query = '''select r.userId, r.movieId, r.rating, m.title
                    from rating r
                    join movie m
                    on r.movieId = m.id;'''

            # select 문은 dictionary=True 를 해준다.
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, )

            result_list = cursor.fetchall()

            df = pd.DataFrame(data=result_list)
            # 피봇 테이블을 한 후, 상관계수를 뽑는다.
            df = df.pivot_table(index='userId', columns='title', values='rating')
            # 영화 별로 50개 이상의 리뷰가 있는 영화만 상관계수 계산
            df = df.corr(min_periods = 50)
            # print(df)

            # 3. 이 유저의 별점 정보를, 디비에서 가져온다.
            query = '''select r.userId, r.movieId, r.rating, m.title 
                    from rating r
                    join movie m 
                    on r.movieId = m.id
                    where userId = %s;'''

            record = (user_id, )

            # select 문은 dictionary=True 를 해준다.
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()
            
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()

            return { "error" : str(e) }, 503
        
        # 디비로부터 가져온, 내 별점 정보를
        # 데이터프레임으로 만들어 준다.
        df_my_rating = pd.DataFrame(data=result_list)
        # print(df_my_rating)

        # 추천 영화를 저장할, 빈 데이터프레임을 만든다.
        similar_movie_list = pd.DataFrame()

        for i in range(len(df_my_rating)) :
            similar_movie = df[df_my_rating['title'][i]].dropna().sort_values(ascending=False).to_frame()
            similar_movie.columns = ['Correlations']
            similar_movie['Weight'] = df_my_rating['rating'][i] * similar_movie['Correlations']
            similar_movie_list = similar_movie_list.append(similar_movie)

        # 영화 제목이 중복된 영화가 있을 수 있다.
        # 중복된 영화는 Weight가 가장 큰(max)값으로 해준다.
        similar_movie_list.reset_index(inplace=True)
        
        similar_movie_list = similar_movie_list.groupby('title')['Weight'].max().sort_values(ascending=False)

        # 내가 이미 봐서, 별점을 남긴 영화는 여기서 제외해야 한다.
        
        # print(similar_movie_list)

        similar_movie_list= similar_movie_list.reset_index()

        # 내가 이미 본 영화 제목만 가져온다.
        title_list = df_my_rating['title'].tolist()

        # similar_movie_list 에 내가 본 영화인 title_list를 
        # 제외하고 가져온다.
        print(similar_movie_list)
        print(title_list)

        similar_movie_list['title'].isin(title_list)

        recomm_movie_list = similar_movie_list.loc[~similar_movie_list['title'].isin(title_list), ]
        
        print(recomm_movie_list.iloc[0 : 20, ])
        # json 형식으로 바꿔서 출력해준다.
        return {"result" : "success",
                "movie_list" : recomm_movie_list.iloc[0:20,].to_dict('records')}