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
        f"<img src='../images/Carleton Logo2.png'><br/>"
        f"<h1>Challenge 10 - SQLALCHEMY</h1>"
        f"<p>Available Routes:</p>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"<a href='/api/v1.0/<start>'>/api/v1.0/&#60;start&#62;</a><br/>"
        f"<a href='/api/v1.0/<start>/<end>'>/api/v1.0/&#60;start>\&#60;end&#62;</a><br/>"
        
        
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB - Locally
    session = Session(engine)

    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = most_recent_date[0]

    latest_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")

    # Calculate the date one year from the last date in data set.
    # Use 366 days as 2016 was a Leap year!
    pervious_year= latest_date - dt.timedelta(days=366)

    # Perform a query to retrieve the data and precipitation scores as well as Sort by date

    percipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > pervious_year).order_by(Measurement.date).all()
    
    # Close session
    session.close()

    # Convert to a dictionary
    past_percipitation = []

    for date, prcp in percipitation:
        percipitation_dict = {}
        percipitation_dict["date"] = date
        percipitation_dict["percipitation"] = prcp
        past_percipitation.append(percipitation_dict)

    return jsonify(past_percipitation)
#  
@app.route("/api/v1.0/stations")
def stations():
    
    # Create our session (link) from Python to the DB - Locally
    session = Session(engine)
    stations_info = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

#     """Return a list of passenger data including the name, age, and sex of each passenger"""
#     # Query all passengers
#     results = session.query(Passenger.name, Passenger.age, Passenger.sex).all()

    session.close()
    # Convert to a dictionary
    all_stations = []

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

    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = most_recent_date[0]

    latest_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")

    # Calculate the date one year from the last date in data set.
    # Use 366 days as 2016 was a Leap year!
    pervious_year= latest_date - dt.timedelta(days=366)

    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    pervious_year_temperature = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > pervious_year).filter(Measurement.station == active_stations[0][0]).order_by(Measurement.date).all()

    session.close()

    past_temperatures = []

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
    
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    most_recent_date = most_recent_date[0]
#     
    latest_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")

    # Calculate the date one year from the last date in data set.
    # Use 366 days as 2016 was a Leap year!
    pervious_year= latest_date - dt.timedelta(days=366)

    
    # Perform a query to retrieve the data and precipitation scores as well as Sort by date
    # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.

    # For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

    percipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > pervious_year).order_by(Measurement.date).all()

    tempature_summary = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.station == most_active_station).all()
    print(tempature_summary)
    # Save the query results as a Pandas DataFrame. Explicitly set the column names
    percipitation_df = pd.DataFrame(percipitation,columns=['date', 'prcp'])
    percipitation_df = percipitation_df.rename(columns={'prcp':'percipitation'})

    session.close()

#   use input:
#   email = input("Entre email")
#   return email
    start = f"Sart<br/>"

#     # Convert list of tuples into normal list
#     all_names = list(np.ravel(results))

    #return jsonify(past_temperatures)
    return ({start}),404


@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):

    # Create our session (link) from Python to the DB - Locally
    session = Session(engine)

    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = most_recent_date[0]
#     
    latest_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")

    # Calculate the date one year from the last date in data set.
    # Use 366 days as 2016 was a Leap year!
    pervious_year= latest_date - dt.timedelta(days=366)

    # Perform a query to retrieve the data and precipitation scores as well as Sort by date
    # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.

    # For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.


    percipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > pervious_year).order_by(Measurement.date).all()

    # Save the query results as a Pandas DataFrame. Explicitly set the column names
    percipitation_df = pd.DataFrame(percipitation,columns=['date', 'prcp'])
    percipitation_df = percipitation_df.rename(columns={'prcp':'percipitation'})
    session.close()

#     # Convert list of tuples into normal list
#     all_names = list(np.ravel(results))

    #return jsonify(past_temperatures)
    return(f"Start/end<br/>")


if __name__ == '__main__':
    app.run(debug=True)
