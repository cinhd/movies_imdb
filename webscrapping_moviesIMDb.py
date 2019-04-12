# import libraries
from IPython.core.display import clear_output
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from time import time
from random import randint
from warnings import warn
from requests import get
import requests
import re

# get url to scrap   
url = ('https://www.imdb.com/search/title?title_type=feature&release_date={year}'
           '&sort=num_votes,desc&start=''&ref_=adv_nxt')

# select linguistic content in American English (en-US)
headers = {'Accept-Language': 'en-US'}

# parse the content of the request with BeautifulSoup
def get_movies(year):
    '''Get list of movies released in <year>.'''
    movies_html = requests.get(url.format(year=year), headers=headers).content
    soup = BeautifulSoup(movies_html, 'html.parser')
    movies = soup.find_all('a', {'href': re.compile('adv_li_tt$')})

    return ['http://www.imdb.com' + m['href'] for m in movies]

def go_to_movie(url):
    '''Get IMDb page of a movie.'''
    movie_html = requests.get(url, headers=headers).content

    return movie_html

def scrap_titlebar(soup):
    '''Get name, rating, genre, year, release date, score and votes of a movie.'''
    name = soup.find('div', {"class": "title_wrapper"})
    name = name.findChildren('h1', recursive=False)[0].text
    genre = soup.find('a', {'href': re.compile('genres')}).text
    certificate= soup.find('div',  class_ ='subtext').text
    certificate = certificate.split('\n')
    score = float(soup.find('span', {'itemprop': 'ratingValue'}).text)
    votes = int(soup.find('span', {'itemprop': 'ratingCount'}).text.replace(',',''))
    released =  soup.find('a', {'href': re.compile('title\/.*tt_ov_inf')}).text.split('\n')[0]
    year = soup.find('span', {'id': 'titleYear'}).find('a').text

    return {'Title': name, 'Genre': genre, 'Certificate':certificate[1], 'Release_Year': year, 'Release_Date': released, 'IMDb_Rating': score, 'IMDb_Votes':votes}

def scrap_summary(soup):
    '''Get director, writer and star of a movie.'''
    director = soup.find('a', {'href': re.compile('tt_ov_dr')}).text
    try:
        star = soup.find('a', {'href': re.compile('tt_ov_st_sm')}).text
    except AttributeError:
        star = 'Not specified' 
    return {'Director': director, 'Star': star}
      
def scrap_details(soup):
    '''Get country, budget, gross, production co. and runtime of a movie.'''
    country = soup.find('a', {'href': re.compile('country_of_origin')}).text
    language = soup.find('a', {'href': re.compile('asc&ref')}).text
    try:
        gross = soup.find('h4', string='Cumulative Worldwide Gross:').parent.contents[2].strip()
        if not '$' in gross:
            gross = '0'
    except AttributeError:
        gross = '0'
    try:
        company = soup.find('a', {'href': re.compile('company\/')}).text
    except AttributeError:
        company = 'Not specified'
    try:
        budget = soup.find('h4', string='Budget:').parent.contents[2].strip()
        if not '$' in budget:
            budget = '0'
    except AttributeError:
        budget = '0'
    try:
        runtime = soup.find_all('time', {'datetime':re.compile('PT')})[1].text
    except IndexError:
        runtime = 0
        runtime= soup.find_all('time', {'datetime':re.compile('PT')})[0].text.split('\n')[0]
            
    gross = float(gross.replace('$','').replace(',',''))
    budget = float(budget.replace('$','').replace(',',''))

    return {'Country': country, 'Budget': budget, 'Gross': gross, 'Production_Co': company, 'Runtime': runtime, 'Language': language}

def write_csv(data):
    '''Write list of dicts to csv.'''
    movies_imdb = pd.DataFrame(data)
    print(movies_imdb.info())
    print(movies_imdb.head())
    movies_imdb.to_csv('titles4.csv', index=False)

def main():
    all_movie_data = []
# For every year in the interval 1980-2020
    years_url = [str(i) for i in range(1980,2020)]
    
    for year in years_url:
        movies = get_movies(year)
#call every container
        for movie_url in movies:
            movie_data = {}
            movie_html = go_to_movie(movie_url)
            soup = BeautifulSoup(movie_html, 'html.parser')
            movie_data.update(scrap_titlebar(soup))
            movie_data.update(scrap_summary(soup))
            movie_data.update(scrap_details(soup))
            all_movie_data.append(movie_data)

# preparing the monitoring of the loop            
        start_time = time()
        requests = 0
            
        # For every year in the interval 1980-2019
        for year_url in years_url:
            print(year, 'done.')
        
                    
            # Make a get request
            url = get('https://www.imdb.com/search/title?title_type=feature&release_date={year}'
           '&sort=num_votes,desc&start=''&ref_=adv_nxt')
            
            # Pause the loop
            sleep(randint(8,15))
            print('--------------------------------------------------------------------------')
    
            # Monitor the requests
            requests += 1
            elapsed_time = time() - start_time
            print('Request:{}; Frequency: {} requests/s'.format(url, requests/elapsed_time))
            clear_output(wait = True)
            
    
            # Throw a warning for non-200 status codes
            if url.status_code != 200:
                warn('Request: {}; Status code: {}'.format(requests, url.status_code))
             
            # Break the loop if the number of requests is greater than expected
            if requests > 72:
                warn('Number of requests was greater than expected.')
                break
            
# write csv calling main function
    write_csv(all_movie_data)

main()