from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField, EmailField, DateField, IntegerField, SelectField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Length, Email, ValidationError
import datetime

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput() 

def length_check(form,field):
    if len(field.data) == 0:
        raise ValidationError('Fields should not be null')
    

class AnalyticsByDirectorFilter(Form):
    start_date = DateField('dd/mm/yyyy', format='%Y-%m-%d', default = datetime.datetime.today().date() - datetime.timedelta(days = 5*365))
    end_date = DateField('dd/mm/yyyy', format='%Y-%m-%d', default = datetime.datetime.today())
    choices = [('All','All'),('United States','United States'),('China','China'),
    ('United Kingdom','United Kingdom'), ('France','France'),('Portugal','Portugal'),
    ('Spain','Spain'),('Russia','Russia'),('Mexico','Mexico'),('Canada','Canada'),
    ('Japan','Japan'),('South Korea','South Korea'),
    ('Germany','Germany'),('Others','Others')]
    country = SelectMultipleField('Rators'' residence country',choices = choices, validators=[ DataRequired()])
    smallest_age = IntegerField('Rater''s Age >= :', default = 0)
    largest_age = IntegerField('Rater''s Age <= :', default = 100)
    gender = SelectField('Rater''s Gender',choices=[('All', 'All'), ('Male', 'Male'), ('Female', 'Female')], default = 'All')

class AnalyticsByGenreFilter(Form):
    start_date = DateField('dd/mm/yyyy', format='%Y-%m-%d',default = datetime.datetime.today().date() - datetime.timedelta(days = 5*365))
    end_date = DateField('dd/mm/yyyy', format='%Y-%m-%d', default = datetime.datetime.today())
    choices = [('All','All'),('United States','United States'),('China','China'),
    ('United Kingdom','United Kingdom'), ('France','France'),('Portugal','Portugal'),
    ('Spain','Spain'),('Russia','Russia'),('Mexico','Mexico'),('Canada','Canada'),
    ('Japan','Japan'),('South Korea','South Korea'),
    ('Germany','Germany'),('Others','Others')]
    country = SelectMultipleField('Rators'' residence country',choices = choices, validators=[ DataRequired()])
    smallest_age = IntegerField('Rater''s Age >= :', default = 0)
    largest_age = IntegerField('Rater''s Age <= :', default = 100)
    gender = SelectField('Rater''s Gender',choices=[('All', 'All'), ('Male', 'Male'), ('Female', 'Female')], default = 'All')


class SearchAMovie(Form):
    title = StringField('Enter the movie title',default='')
    director = StringField('Enter the director''s name',default='')
    star = StringField('Enter the star''s name',default='')

class SearchADirector(Form):
    name = StringField('Director Name',default='')

class SearchAStar(Form):
    name = StringField('Star Name',default='')


class AnalyticsByReleaseCountryFilter(Form):
    choices = [('All','All'),('United States','United States'),('China','China'),
    ('United Kingdom','United Kingdom'), ('France','France'),('Portugal','Portugal'),
    ('Spain','Spain'),('Russia','Russia'),('Mexico','Mexico'),('Canada','Canada'),
    ('Japan','Japan'),('South Korea','South Korea'),
    ('Germany','Germany'),('Others','Others')]
    countries = SelectMultipleField(choices = choices,validators=[ DataRequired()])
    start_date = DateField('dd/mm/yyyy', format='%Y-%m-%d',default = datetime.datetime.today().date() - datetime.timedelta(days = 5*365))
    end_date = DateField('dd/mm/yyyy', format='%Y-%m-%d',default = datetime.datetime.today().date())