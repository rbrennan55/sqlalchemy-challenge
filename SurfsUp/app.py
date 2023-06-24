# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt


import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<img src='/static/images/Carleton Logo2.png'width='147' height='147'>"
        f"<h1>Challenge 10 - SQLALCHEMY</h1>"
        f"<p>Available Routes:</p>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"<a href='/api/v1.0/<start>'>/api/v1.0/&#60;start&#62;</a><a>  - Format (YYYY-MM-DD)<br/>"
        f"<a href='/api/v1.0/<start>/<end>'>/api/v1.0/&#60;start>/&#60;end&#62;</a><a>  - Format (YYYY-MM-DD)/(YYYY-MM-DD)<br/>"
            
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB - Locally
    session = Session(engine)

    # Find the last date
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = most_recent_date[0]

    # Convert the date to the correct format
    latest_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")

    # Calculate the date one year from the last date in data set.
    # Use 366 days as 2016 was a Leap year!
    pervious_year= latest_date - dt.timedelta(days=366)

    # Perform a query to retrieve the date and precipitation
    percipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > pervious_year).order_by(Measurement.date).all()
    
    # Close session
    session.close()

    
    # Initialize dictionary
    past_percipitation = []

    # Convert data to a dictionary
    for date, prcp in percipitation:
        percipitation_dict = {}
        percipitation_dict["date"] = date
        percipitation_dict["percipitation"] = prcp
        past_percipitation.append(percipitation_dict)

    return jsonify(past_percipitation)
  
@app.route("/api/v1.0/stations")
def stations():
    
    # Create our session (link) from Python to the DB - Locally
    session = Session(engine)

    # Query all the weather station information
    stations_info = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()
    
    # Initialize dictionary
    all_stations = []

    # Convert data to a dictionary
    for station, name, latitude, longitude, elevation, in stations_info:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    
    # Create our session (link) from Python to the DB - Locally
    session = Session(engine)

    # Find the last date
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = most_recent_date[0]

    # Convert the date to the correct format
    latest_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")

    # Calculate the date one year from the last date in data set.
    # Use 366 days as 2016 was a Leap year!
    pervious_year= latest_date - dt.timedelta(days=366)


    # Query for the most action weather stations 
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    
    # Query for the temperatures from the past 12 months from the most action weather stations 
    pervious_year_temperature = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > pervious_year).filter(Measurement.station == active_stations[0][0]).order_by(Measurement.date).all()

    session.close()
    # Initialize dictionary
    past_temperatures = []

    # Convert data to a dictionary
    for date, tobs in pervious_year_temperature:
        past_temperatures_dict = {}
        past_temperatures_dict["date"] = date
        past_temperatures_dict["temperature"] = tobs
        past_temperatures.append(past_temperatures_dict)

    return jsonify(past_temperatures)

@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB - Locally
    session = Session(engine)

    # Find the last date
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    end = most_recent_date[0]
    
    # Query the min, max and average temperatures from the date supplied from URL to the end of the datatable

    tempature_summary = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),\
                                       func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).order_by(Measurement.date).all()
    session.close()

    # Initialize dictionary  
    summary_temperatures = []

    # Convert data to a dictionary
    for mintobs, maxtobs, avgtobs in tempature_summary:
        summary_temperatures_dict = {}
        summary_temperatures_dict["min temperature"] = mintobs
        summary_temperatures_dict["max temperature"] = maxtobs
        summary_temperatures_dict["avg temperature"] = avgtobs
        summary_temperatures.append(summary_temperatures_dict)

    return jsonify(summary_temperatures)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):

    # Create our session (link) from Python to the DB - Locally
    session = Session(engine)

    # Query the min, max and average temperatures from the first date supplied to the end date supplied from URL 
    tempature_range_summary = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),\
                                            func.avg(Measurement.tobs)).filter(Measurement.date.between(start, end)).all()
    
    session.close()
    # Initialize dictionary  
    summary_range_temperatures = []
    
    # Convert data to a dictionary
    for mintobs, maxtobs, avgtobs in tempature_range_summary:
        summary_range_temperatures_dict = {}
        summary_range_temperatures_dict["min temperature"] = mintobs
        summary_range_temperatures_dict["max temperature"] = maxtobs
        summary_range_temperatures_dict["avg temperature"] = avgtobs
        summary_range_temperatures.append(summary_range_temperatures_dict)


    return jsonify(summary_range_temperatures)


if __name__ == '__main__':
    app.run(debug=True)
