from sqlalchemy import create_engine
from sqlalchemy.sql import text
import os


class Models:
    def __init__(self):
        self.engine = create_engine(os.environ.get('DB_URL', 'postgresql://postgres:kelly0426@localhost:5432/simapp'))

    def executeRawSql(self, statement, params={}):
        out = None
        with self.engine.connect() as con:
            out = con.execute(text(statement), params)
        return out

    def searchAMovie(self,title,director,star):
        values = self.executeRawSql("""select * from
(SELECT movies.movie_id, movies.title, movies.genre, movies.release_date, 
        movies.director, movies.star, movies.release_country, movies.language, 
        round(avg(cast(ratings.score as decimal(3,1))),2) as avg_rating,
        count(*) as n_ratingrecords,
		concat(round(100*cast(rank() over (order by avg(cast(ratings.score as decimal(3,1)))) as decimal(4,1))/(select count(*) from movies),2),'%') as higher_ratio
        FROM movies,ratings
		where movies.movie_id = ratings.movie_id
        group by movies.movie_id, movies.title, movies.genre, movies.release_date, movies.director,
         movies.star, movies.release_country, movies.language)a
	where lower(title) like concat('%', lower(cast( :title as varchar)),'%') 
        and lower(director) like concat('%',lower(cast( :director as varchar)),'%')
        and lower(star) like concat('%', lower(cast( :star as varchar)),'%')
        order by avg_rating desc;""",
         {"title":title,"director":director,'star':star}).mappings().all()
        return values

    def searchADirector(self,name):
        values = self.executeRawSql("""
        select * from 
        (select director, director_country, director_gender, director_birth_year,
        max(movie_avg_score) as highest_score,
        min(movie_avg_score) as lowest_score,
        round(avg(movie_avg_score),2) as avg_score,
        concat(cast(rank() over(order by avg(movie_avg_score)) as varchar),'%') as higher_ratio,
        round(stddev(movie_avg_score),2) as std_score,
        count(*) as n_movies
        from (
        select m.movie_id, m.title, m.genre, m.release_date, m.release_country, m.language,
        m.director, m.director_country, m.director_gender, m.director_birth_year, 
        round(avg(cast(r.score as decimal(3,1))),2) as movie_avg_score
        from movies m, ratings r 
	    where m.movie_id = r.movie_id 
        group by m.movie_id, m.title, m.genre, m.release_date, m.release_country, m.language,
        m.director, m.director_country, m.director_gender, m.director_birth_year
	        )a 
	        group by director, director_country, director_gender, director_birth_year 
         order by avg_score desc)b
		where lower(director) like concat('%', lower(:name) ,'%')""",
         {"name":name}).mappings().all()
        return values

    def searchAStar(self,name):
        values = self.executeRawSql("""
        select * from 
        (select star, star_country, star_gender, star_birth_year,
        max(movie_avg_score) as highest_score,
        min(movie_avg_score) as lowest_score,
        round(avg(movie_avg_score),2) as avg_score,
        concat(cast(rank() over(order by avg(movie_avg_score)) as varchar),'%') as higher_ratio,
        round(stddev(movie_avg_score),2) as std_score,
        count(*) as n_movies
        from (
        select m.movie_id, m.title, m.genre, m.release_date, m.release_country, m.language,
        m.star, m.star_country, m.star_gender, m.star_birth_year, 
        round(avg(cast(r.score as decimal(3,1))),2) as movie_avg_score
        from movies m, ratings r 
        where m.movie_id = r.movie_id 
        group by m.movie_id, m.title, m.genre, m.release_date, m.release_country, m.language,
        m.star, m.star_country, m.star_gender, m.star_birth_year
        )a 
        group by star, star_country, star_gender, star_birth_year 
        order by avg_score desc)b
		where lower(star) like concat('%', lower(:name) ,'%')""",
         {"name":name}).mappings().all()
        return values



    def analyticsByDirector(self,start_date,end_date,country,smallest_age,largest_age,gender):
        values = self.executeRawSql("""
        set datestyle to DMY;
        select director, round(avg(movie_rating),2) as director_avg_rating,
        rank() over(order by avg(movie_rating) desc )  as rank
        from (
        select movie_id, title, genre, release_date, director, star, 
			release_country, language, 
         round( avg(cast(score as decimal(3,1))),3) as movie_rating from
        (select m.movie_id, m.title, m.genre, m.release_date, 
         m.director, m.star, m.release_country, m.language,
         r.score, cast(d.date as date) as rating_date,
			date_part('year',age(cast(d.date as date),cast(u.birth_date as date))) as age, u.residence_country, u.gender  
        from movies m, ratings r, users u, dates d 
        where r.movie_id = m.movie_id 
        and r.user_email = u.email 
		and r.date_id = d.date_id
		and (
		 cast( :country as varchar) like concat('%',u.residence_country,'%')
		  or cast( :country as varchar) like '%All%'
		  or (cast( :country as varchar) like '%Others%' and u.residence_country not in
			  ('United States', 'China', 'France','Portugal','Spain',
        'Russia','Mexico','Canada','Japan','South Korea','Germany','United Kingdom')))
			  ) a
		where rating_date >= cast( :start_date as date)
		and rating_date <= cast( :end_date as date)
        and age >= :smallest_age
        and age <= :largest_age
        and (( :gender = 'All' and gender in ('Male','Female'))
		 or ( :gender  = 'Male' and gender='Male')
		 or ( :gender = 'Female' and gender='Female')) 
        group by movie_id, title, genre, release_date, 
        director, star, release_country, language)b
        group by director
        order by director_avg_rating desc;""", {"start_date": start_date, "end_date": end_date, "country":country,
        "smallest_age": smallest_age, "largest_age": largest_age, "gender":gender}).mappings().all()
        return values

    def analyticsByGenre(self,start_date,end_date,country,smallest_age,largest_age,gender):
        values = self.executeRawSql("""
        set datestyle to DMY;
        drop table if exists genre_temp;
        create table genre_temp as select * from(
        select 
        case when sum(case when genre like '%Comedy%' then 1 else 0 end) != 0 then sum(case when genre like '%Comedy%' then movie_rating else 0 end)/sum(case when genre like '%Comedy%' then 1 else 0 end) else 0 end as Comedy,
        case when sum(case when genre like '%Drama%' then 1 else 0 end) != 0 then sum(case when genre like '%Drama%' then movie_rating else 0 end)/sum(case when genre like '%Drama%' then 1 else 0 end) else 0 end as Drama,
        case when sum(case when genre like '%Romance%' then 1 else 0 end) != 0 then sum(case when genre like '%Romance%' then movie_rating else 0 end)/sum(case when genre like '%Romance%' then 1 else 0 end) else 0 end as Romance,
        case when sum(case when genre like '%Adventure%' then 1 else 0 end) != 0 then sum(case when genre like '%Adventure%' then movie_rating else 0 end)/sum(case when genre like '%Adventure%' then 1 else 0 end) else 0 end as Adventure,
        case when sum(case when genre like '%Western%' then 1 else 0 end) != 0 then sum(case when genre like '%Western%' then movie_rating else 0 end)/sum(case when genre like '%Western%' then 1 else 0 end) else 0 end as Western,
        case when sum(case when genre like '%Sci-Fi%' then 1 else 0 end) != 0 then sum(case when genre like '%Sci-Fi%' then movie_rating else 0 end)/sum(case when genre like '%Sci-Fi%' then 1 else 0 end) else 0 end as SciFi,
        case when sum(case when genre like '%IMAX%' then 1 else 0 end) != 0 then sum(case when genre like '%IMAX%' then movie_rating else 0 end)/sum(case when genre like '%IMAX%' then 1 else 0 end) else 0 end as IMAX,
        case when sum(case when genre like '%War%' then 1 else 0 end) != 0 then sum(case when genre like '%War%' then movie_rating else 0 end)/sum(case when genre like '%War%' then 1 else 0 end) else 0 end as War,
        case when sum(case when genre like '%War%' then 1 else 0 end) != 0 then sum(case when genre like '%Crime%' then movie_rating else 0 end)/sum(case when genre like '%Crime%' then 1 else 0 end) else 0 end as Crime,
        case when sum(case when genre like '%Documentary%' then 1 else 0 end) != 0 then sum(case when genre like '%Documentary%' then movie_rating else 0 end)/sum(case when genre like '%Documentary%' then 1 else 0 end) else 0 end as Documentary,
        case when sum(case when genre like '%Horror%' then 1 else 0 end) != 0 then sum(case when genre like '%Horror%' then movie_rating else 0 end)/sum(case when genre like '%Horror%' then 1 else 0 end) else 0 end as Horror,
        case when sum(case when genre like '%Mystery%' then 1 else 0 end) != 0 then sum(case when genre like '%Mystery%' then movie_rating else 0 end)/sum(case when genre like '%Mystery%' then 1 else 0 end) else 0 end as Mystery,
        case when sum(case when genre like '%Animation%' then 1 else 0 end) != 0 then sum(case when genre like '%Animation%' then movie_rating else 0 end)/sum(case when genre like '%Animation%' then 1 else 0 end) else 0 end as Animation,
        case when sum(case when genre like '%Children%' then 1 else 0 end) != 0 then sum(case when genre like '%Children%' then movie_rating else 0 end)/sum(case when genre like '%Children%' then 1 else 0 end) else 0 end as Children,
        case when sum(case when genre like '%Fantasy%' then 1 else 0 end) != 0 then sum(case when genre like '%Fantasy%' then movie_rating else 0 end)/sum(case when genre like '%Fantasy%' then 1 else 0 end) else 0 end as Fantasy,
        case when sum(case when genre like '%Musical%' then 1 else 0 end) != 0 then sum(case when genre like '%Musical%' then movie_rating else 0 end)/sum(case when genre like '%Musical%' then 1 else 0 end) else 0 end as Musical,
        case when sum(case when genre like '%Thriller%' then 1 else 0 end) != 0 then sum(case when genre like '%Thriller%' then movie_rating else 0 end)/sum(case when genre like '%Thriller%' then 1 else 0 end) else 0 end as Thriller,
        case when sum(case when genre like '%Action%' then 1 else 0 end) != 0 then sum(case when genre like '%Action%' then movie_rating else 0 end)/sum(case when genre like '%Action%' then 1 else 0 end) else 0 end as Action,
        case when sum(case when genre like '%Film-Noir%' then 1 else 0 end) != 0 then sum(case when genre like '%Film-Noir%' then movie_rating else 0 end)/sum(case when genre like '%Film-Noir%' then 1 else 0 end) else 0 end as FilmNoir
        from (
        select movie_id, title, genre, release_date, director, star, 
			release_country, language, 
         round( avg(cast(score as decimal(3,1))),3) as movie_rating from
        (select m.movie_id, m.title, m.genre, m.release_date, 
         m.director, m.star, m.release_country, m.language,
         r.score, cast(d.date as date) as rating_date,
			date_part('year',age(cast(d.date as date),cast(u.birth_date as date))) as age, u.residence_country, u.gender  
        from movies m, ratings r, users u, dates d 
        where r.movie_id = m.movie_id 
        and r.user_email = u.email 
		and r.date_id = d.date_id
		and (
		 cast( :country as varchar) like concat('%',u.residence_country,'%')
		  or cast( :country as varchar) like '%All%'
		  or (cast( :country as varchar) like '%Others%' and u.residence_country not in
			  ('United States', 'China', 'France','Portugal','Spain',
       'Russia','Mexico','Canada','Japan','South Korea','Germany','United Kingdom')))
        ) a
		where rating_date >= cast( :start_date as date)
		and rating_date <= cast( :end_date as date)
        and age >= :smallest_age
        and age <= :largest_age
        and (( :gender = 'All' and gender in ('Male','Female'))
		 or ( :gender = 'Male' and gender='Male')
		 or ( :gender = 'Female' and gender='Female')) 
        group by movie_id, title, genre, release_date, 
        director, star, release_country, language)b )t;

        select a.genre, round(a.genre_avg_rating,2) as genre_avg_rating, rank() over(order by genre_avg_rating desc) from(
        select 'comedy' as genre, comedy as genre_avg_rating from genre_temp
        union all
        select 'Romance' as genre, Romance as genre_avg_rating from genre_temp
        union all
        select 'Adventure' as genre, Adventure as genre_avg_rating from genre_temp
        union all
        select 'Western' as genre, Western as genre_avg_rating from genre_temp
        union all
        select 'Sci-Fi' as genre, SciFi as genre_avg_rating from genre_temp
        union all
        select 'IMAX' as IMAX, Romance as genre_avg_rating from genre_temp
        union all
        select 'War' as genre, War as genre_avg_rating from genre_temp
        union all
        select 'Crime' as genre, Crime as genre_avg_rating from genre_temp
        union all
        select 'Documentary' as genre, Documentary as genre_avg_rating from genre_temp
        union all
        select 'Horror' as genre, Horror as genre_avg_rating from genre_temp
        union all
        select 'Mystery' as genre, Mystery as genre_avg_rating from genre_temp
        union all
        select 'Animation' as genre, Animation as genre_avg_rating from genre_temp
        union all
        select 'Children' as genre, Children as genre_avg_rating from genre_temp
        union all
        select 'Fantasy' as genre, Fantasy as genre_avg_rating from genre_temp
        union all
        select 'Musical' as genre, Musical as genre_avg_rating from genre_temp
        union all
        select 'Thriller' as genre, Thriller as genre_avg_rating from genre_temp
        union all
        select 'Action' as genre, Action as genre_avg_rating from genre_temp
        union all
        select 'Film-Noir' as genre, FilmNoir as genre_avg_rating from genre_temp)a
        order by genre_avg_rating desc;""", {"start_date": start_date, "end_date": end_date, "country":country,
        "smallest_age": smallest_age, "largest_age": largest_age, "gender":gender}).mappings().all()
        return values

    def analyticsByStar(self,start_date,end_date,country,smallest_age,largest_age,gender):
        values = self.executeRawSql("""
        set datestyle to DMY;
        select star, round(avg(movie_rating),2) as star_avg_rating,
        rank() over(order by avg(movie_rating) desc )  as rank
        from (
        select movie_id, title, genre, release_date, director, star, 
			release_country, language, 
         round( avg(cast(score as decimal(3,1))),3) as movie_rating from
        (select m.movie_id, m.title, m.genre, m.release_date, 
         m.director, m.star, m.release_country, m.language,
         r.score, cast(d.date as date) as rating_date,
			date_part('year',age(cast(d.date as date),cast(u.birth_date as date))) as age, u.residence_country, u.gender  
        from movies m, ratings r, users u, dates d 
        where r.movie_id = m.movie_id 
        and r.user_email = u.email 
		and r.date_id = d.date_id
		and (
		 cast( :country as varchar) like concat('%',u.residence_country,'%')
		  or cast( :country as varchar) like '%All%'
		  or (cast( :country as varchar) like '%Others%' and u.residence_country not in
			  ('United States', 'China', 'France','Portugal','Spain',
       'Russia','Mexico','Canada','Japan','South Korea','Germany','United Kingdom'))) ) a
		where rating_date >= cast(:start_date as date)
		and rating_date <= cast(:end_date as date)
        and age >= :smallest_age
        and age <= :largest_age
        and ((:gender = 'All' and gender in ('Male','Female'))
		 or (:gender  = 'Male' and gender='Male')
		 or (:gender = 'Female' and gender='Female')) 
        group by movie_id, title, genre, release_date, 
        director, star, release_country, language)b
        group by star
        order by star_avg_rating desc;""", {"start_date": start_date, "end_date": end_date, "country":country,
        "smallest_age": smallest_age, "largest_age": largest_age, "gender":gender}).mappings().all()
        return values


    def analyticsByReleaseCountry(self,countries,start_date,end_date):
        values = self.executeRawSql("""
        set datestyle to MDY;
        select release_country, round(avg(movie_rating),2) as movie_avg_rating,
        count(*) as n_movies from(
        select movie_id, title, genre, release_date, director, star, 
			release_country, language, 
         round( avg(cast(score as decimal(3,1))),3) as movie_rating from
        (select m.movie_id, m.title, m.genre, m.release_date, 
         m.director, m.star, m.release_country, m.language,
         r.score
        from movies m, ratings r 
        where r.movie_id = m.movie_id 
		and cast(m.release_date as date) >= cast(:start_date as date)
		and cast(m.release_date as date) <= cast(:end_date as date) 
		and 
		 ( cast( :countries as varchar) like concat('%',m.release_country,'%')
		  or cast( :countries as varchar) like '%All%'
		  or (cast( :countries as varchar) like '%Others%' and m.release_country not in
			  ('China', 'France','Portugal','Spain',
        'Russia','Mexico','Canada','United States',
             'Japan','South Korea','Germany','United Kingdom')
			 ) ))a
		 group by movie_id, title, genre, release_date, director, star, 
			release_country, language)b
			group by release_country order by release_country; """, {"start_date": start_date, "end_date": end_date, "countries":countries}).mappings().all()
        return values


    def createModels(self):
        self.executeRawSql(
        """CREATE TABLE IF NOT EXISTS student (
            email TEXT PRIMARY KEY
        );
        """)

       

        self.executeRawSql(
        """CREATE TABLE IF NOT EXISTS movies (
            movie_id TEXT PRIMARY KEY,
            title TEXT NOT NULL, 
            genre TEXT NOT NULL, 
            release_date TEXT NOT NULL, 
            release_country TEXT NOT NULL,
            language TEXT NOT NULL,
            director TEXT NOT NULL, 
            director_country TEXT NOT NULL, 
            director_gender TEXT NOT NULL, 
            director_birth_year TEXT NOT NULL, 
            star TEXT NOT NULL, 
            star_country TEXT NOT NULL, 
            star_gender TEXT NOT NULL, 
            star_birth_year TEXT NOT NULL
        );
        """)

        self.executeRawSql(
        """CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL, 
            username TEXT NOT NULL, 
            birth_date TEXT NOT NULL, 
            gender TEXT NOT NULL, 
            residence_country TEXT NOT NULL
        );
        """)

        self.executeRawSql(
            """CREATE TABLE IF NOT EXISTS dates (
                date_id TEXT PRIMARY KEY,
                date TEXT NOT NULL,
                year TEXT NOT NULL,
                month TEXT NOT NULL,
                weekday TEXT NOT NULL,
                day TEXT NOT NULL,
                event TEXT NOT NULL
            );
            """)

        self.executeRawSql(
            """CREATE TABLE IF NOT EXISTS ratings (
                user_email TEXT REFERENCES users(email),
                movie_id TEXT REFERENCES movies(movie_id),
                date_id TEXT REFERENCES dates(date_id),
                score TEXT,
                PRIMARY KEY (user_email, movie_id)
            );
            """)