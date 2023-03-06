from unittest import result
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine=engine, reflect=True)

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
        f"Welcome to the Climate APP!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]<br/>" 
)

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation"""
    # Query all precipitation
    laststr_date = session.query(func.max(Measurement.date)).first()[0]
    last_date = dt.datetime.strptime(laststr_date,"%Y-%m-%d").date()
    previous_year = last_date - dt.timedelta(365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>=previous_year).all()
    
    session.close()
      
# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
    precip_all = []
    for date,prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        precip_all.append(prcp_dict)
    
    return jsonify(precip_all)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Stations"""
    # Query stations
    results = session.query(Station.station).all()

    session.close()

# Convert list 
    all_stat = list(np.ravel(results))

# Return a JSON list of stations from the dataset.  
    return jsonify(all_stat)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all tobs"""
    # Query the dates and temperature observations of the most-active station for the previous year of data
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    active_stations

    session.close()
      
# Return a JSON list of temperature observations for the previous year.
    tobs_all = []
    for date,tobs in active_stations:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_all.append(tobs_dict)
    
    return jsonify(tobs_all)

@app.route("/api/v1.0/<start>")
def start_date():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of the min temp, the avg temp, and the max temp for a specified start date"""
    # For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
    spec_start = session.query(func.min(Measurement.tobs), 
                            func.avg(Measurement.tobs), 
                            func.max(Measurement.tobs)).\
                filter(Measurement.date >= start_date).all()

    session.close()
      
# Return a JSON list 
    start_tobs = []
    for min,avg,max in spec_start:
        starttobs_dict = {}
        starttobs_dict["minimum"] = min
        starttobs_dict["average"] = avg
        starttobs_dict["maximum"] = max
        start_tobs.append(starttobs_dict)
    
    return jsonify(start_tobs)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of the min temp, the avg temp, and the max temp for a specified start date"""
    # For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
    start_end = session.query(func.min(Measurement.tobs), 
                            func.avg(Measurement.tobs), 
                            func.max(Measurement.tobs)).\
                filter(Measurement.date >= start_date).filter(Measurement.date <= end).all()

    session.close()
      
# Return a JSON list 
    start_end = []
    for min,avg,max in start_end:
        startend_tobs = {}
        startend_tobs["minimum"] = min
        startend_tobs["average"] = avg
        startend_tobs["maximum"] = max
        start_end.append(startend_tobs)
    
    return jsonify(start_end)

if __name__ == '__main__':
    app.run(debug=True)






