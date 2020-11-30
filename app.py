""" flask_example.py

    Required packages:
    - flask
    - folium

    Usage:

    Start the flask server by running:

        $ python flask_example.py

    And then head to http://127.0.0.1:5000/ in your browser to see the map displayed

"""

from flask import Flask, render_template,url_for, request
from flask_bootstrap import Bootstrap
import folium
import numpy as np
from folium.plugins import HeatMap
from folium.plugins import MarkerCluster

import geopandas
import pandas as pd
import scipy
from scipy import signal

import User_handler
from User_handler import User
from FoliumGenerator import FoliumMapGenerator



app = Flask(__name__)
Bootstrap(app)

testuser = User()
mapGenerator = FoliumMapGenerator()



@app.route('/')
def index():
   return render_template('mainpage.html')


@app.route('/getstarted')
def splashpage():
    name = 'tacos'
    f, df = mapGenerator.pre_loaded(name)
    return render_template('splash.html', map=f._repr_html_(),food='Taco')



@app.route('/fastmap')
def fastmap():
    food = request.args.get('food','tacos')
    f, df = mapGenerator.fastsearch_map(food,testuser)
    return render_template('splash.html', map=f._repr_html_(),food=food)

@app.route('/listfastmap', methods=['GET','POST'])
def otherfastmap():
    food = request.args.get('food','tacos')
    f, df = mapGenerator.fastsearch_map(food,testuser)
    listofresturants = zip(df.index, df.address.values, df.stars_x.values,df.business_id.values)
    return render_template('splash2.html', 
                           map=f._repr_html_(),
                           food=food,
                           rest=listofresturants)

@app.route('/add_ratings', methods=['GET'])
def add_rating():
    busid = request.args.get('busid')
    rating = int(request.args.get('rating'))
    testuser.addreview(busid, rating)
    print(testuser.reviews)
    print(testuser.features)
    return render_template('response.html')


if __name__ == '__main__':
    app.run(debug=False)
