import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt
import numpy as np
import pandas as pd

engine = create_engine("sqlite:///data/hawaii.sqlite")
#create base
Base = automap_base()
# reflect the tables with Base.prepare(), passing in the engine and reflect=True
Base.prepare(engine, reflect=True)
#create classes

Measurement = Base.classes.measurement
Station = Base.classes.station

#run file
#python3 app.py

from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Hello, welcome to the Climate App home page!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start_route>"
        f"/api/v1.0/<start_route>/<end_route>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #create session
    session = Session(engine)
    #last date
    last_date = (session
    .query(Measurement.date)
    .order_by(Measurement.date.desc())
    .first().date)
    #one year ago
    one_year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    #rain for the last year
    rain_past_year = (session
    .query(Measurement.date, func.avg(Measurement.prcp))
    .filter(Measurement.date >= one_year_ago)
    .group_by(Measurement.date).all())
    return jsonify(rain_past_year)

@app.route("/api/v1.0/stations")
def stations():
    #create session
    session = Session(engine)
    #station data
    station_data = (session
    .query(Measurement.station, Station.name, func.count(Measurement.station))
    .group_by(Measurement.station)
    .order_by(func.count(Measurement.station).desc()).all())
    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def temp_obs():
    #create session
    session = Session(engine)
    #station data
    station_data = (session
    .query(Measurement.station, Station.name, func.count(Measurement.station))
    .group_by(Measurement.station)
    .order_by(func.count(Measurement.station).desc()).all())
    #most active stations
    most_active = station_data[0][0]
    #last date calc
    last_date = (session
    .query(Measurement.date)
    .order_by(Measurement.date.desc())
    .first().date)
    #one year ago
    one_year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    #temp observations
    temp_obs = (session
    .query(Measurement.station, Measurement.tobs)
    .filter(Measurement.station == most_active)
    .filter(Measurement.date >= one_year_ago).all())
    return jsonify(temp_obs)

@app.route("/api/v1.0/<start_date>")
@app.route("/api/v1.0/<start_date>/<end_date>")
def end_route(start_date=None, end_date=None):
    #create session
    session = Session(engine)
    #first date if none
    if start_date is None:
        start_date = (session
    .query(Measurement.date)
    .order_by(Measurement.date)
    .first().date)
    #last date if none
    if end_date is None:
        end_date = (session
    .query(Measurement.date)
    .order_by(Measurement.date.desc())
    .first().date)
    #summary statistics
    end_summary = (session
    .query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
    .filter(Measurement.date >= start_date)
    .filter(Measurement.date <= end_date).all())
    return jsonify(end_summary)

if __name__ == "__main__":
    app.run(debug=True)
