from flask import request, session, redirect, url_for, render_template, flash

from . models import Models
from . forms import AnalyticsByDirectorFilter, SearchAMovie, SearchADirector, SearchAStar, AnalyticsByReleaseCountryFilter

from src import app

models = Models()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/search_a_movie',methods=['GET', 'POST'])
def search_a_movie():
    try:
        search_a_movie = SearchAMovie(request.form)
        if request.method == 'POST':
            search_a_movie_results = models.searchAMovie(search_a_movie.title.data,
            search_a_movie.director.data,
            search_a_movie.star.data)
            return render_template('search_a_movie_results.html', search_a_movie_results = search_a_movie_results)
        return render_template('search_a_movie.html', search_a_movie=search_a_movie)
    except Exception as e:
        flash(str(e))
        #return redirect(url_for('index'))

@app.route('/search_a_director',methods=['GET', 'POST'])
def search_a_director():
    try:
        search_a_director = SearchADirector(request.form)
        if request.method == 'POST':
            search_a_director_results = models.searchADirector(search_a_director.name.data)
            return render_template('search_a_director_results.html', search_a_director_results = search_a_director_results)
        return render_template('search_a_director.html', search_a_director=search_a_director)
    except Exception as e:
        flash(str(e))
        #return redirect(url_for('index'))


@app.route('/search_a_star',methods=['GET', 'POST'])
def search_a_star():
    try:
        search_a_star = SearchAStar(request.form)
        if request.method == 'POST':
            search_a_star_results = models.searchAStar(search_a_star.name.data)
            return render_template('search_a_star_results.html', search_a_star_results = search_a_star_results)
        return render_template('search_a_star.html', search_a_star = search_a_star)
    except Exception as e:
        flash(str(e))
        #return redirect(url_for('index')


@app.route('/see_analytics')
def see_analyticsd():
    return render_template('see_analytics.html')

@app.route('/analytics_by_director_filter',methods=['GET', 'POST'])
def analytics_by_director_filter():
    try:
        analytics_by_director_filter = AnalyticsByDirectorFilter(request.form)
        if request.method == 'POST':
            top_directors = models.analyticsByDirector(analytics_by_director_filter.start_date.data,
            analytics_by_director_filter.end_date.data,analytics_by_director_filter.country.data,
            analytics_by_director_filter.smallest_age.data,analytics_by_director_filter.largest_age.data,
            analytics_by_director_filter.gender.data)
            return render_template('analytics_by_director.html', top_directors=top_directors)
        return render_template('analytics_by_director_filter.html', analytics_by_director_filter=analytics_by_director_filter)
    except Exception as e:
        flash(str(e))
        return redirect(url_for('index'))


@app.route('/analytics_by_star_filter',methods=['GET', 'POST'])
def analytics_by_star_filter():
    try:
        analytics_by_star_filter = AnalyticsByDirectorFilter(request.form)
        if request.method == 'POST':
            top_stars = models.analyticsByStar(analytics_by_star_filter.start_date.data,
            analytics_by_star_filter.end_date.data,analytics_by_star_filter.country.data,
            analytics_by_star_filter.smallest_age.data,analytics_by_star_filter.largest_age.data,
            analytics_by_star_filter.gender.data)
            return render_template('analytics_by_star.html', top_stars=top_stars)
        return render_template('analytics_by_star_filter.html', analytics_by_star_filter=analytics_by_star_filter)
    except Exception as e:
        flash(str(e))
        return redirect(url_for('index'))

@app.route('/analytics_by_genre_filter',methods=['GET', 'POST'])
def analytics_by_genre_filter():
    try:
        analytics_by_genre_filter = AnalyticsByDirectorFilter(request.form)
        if request.method == 'POST':
            top_genres = models.analyticsByGenre(analytics_by_genre_filter.start_date.data,
            analytics_by_genre_filter.end_date.data,analytics_by_genre_filter.country.data,
            analytics_by_genre_filter.smallest_age.data,analytics_by_genre_filter.largest_age.data,
            analytics_by_genre_filter.gender.data)
            return render_template('analytics_by_genre.html', top_genres=top_genres)
        return render_template('analytics_by_genre_filter.html', analytics_by_genre_filter=analytics_by_genre_filter)
    except Exception as e:
        flash(str(e))
        return redirect(url_for('index'))

@app.route('/analytics_by_release_country_filter',methods=['GET', 'POST'])
def analytics_by_release_country_filter():
    try:
        analytics_by_release_country_filter = AnalyticsByReleaseCountryFilter(request.form)
        if request.method == 'POST':
            analytics_by_release_country_results  = models.analyticsByReleaseCountry(analytics_by_release_country_filter.countries.data,
            analytics_by_release_country_filter.start_date.data,analytics_by_release_country_filter.end_date.data)
            return render_template('analytics_by_release_country.html', analytics_by_release_country_results=analytics_by_release_country_results)
        return render_template('analytics_by_release_country_filter.html', analytics_by_release_country_filter=analytics_by_release_country_filter)
    except Exception as e:
        flash(str(e))
        #return redirect(url_for('index'))

