# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
db_path = r'C:\Users\Owner\DABootcamp\sqlalchemy-challenge\Resources\hawaii.sqlite'
engine = create_engine(f"sqlite:///{db_path}")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

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
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
        f"Temperature stat from the start date: /api/v1.0/start<br/>"
        f"Temperature stat from start to end: /api/v1.0/start_end<br/>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d')
    year_ago_date = dt.date(last_date.year -1, last_date.month, last_date.day)
    year_ago_date 
    query = session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date >= year_ago_date).all()
    session.close()

    precipitation = []
    for date, prcp in query:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    stations = session.query(Measurement.station).distinct().all()
    
    session.close()

    all_stations = list(np.ravel(stations))

    return jsonify(all_stations)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    most_active = session.query(Measurement.station).group_by(Measurement.station).\
    order_by(func.count(Measurement.id).desc()).first()[0]

    temp = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(Measurement.station == most_active).first()
    session.close()

    all_tobs = []
    tobs_dict = {}
    tobs_dict["Min"] = temp[0]
    tobs_dict["Average"] = temp[1]
    tobs_dict["Max"] = temp[2]
    all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def temp(start, end='2017-08-23'):
    

    session = Session(engine)
    query_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    temp_stats = []
    for min_temp, avg_temp, max_temp in query_result:
        temp_dict = {
            "Min": min_temp,
            "Average": avg_temp,
            "Max": max_temp
        }
        temp_stats.append(temp_dict)

    # If the query returned non-null values, return the results,
    # otherwise return an error message
    if temp_stats:
        return jsonify(temp_stats)
    else:
        return jsonify({"error": f"Date {start} not found or not formatted as YYYY-MM-DD."}), 404

@app.route("/api/v1.0/trip/<start>/<end>")
def temp2(start, end='2017-08-23'):
    
    session = Session(engine)
    query_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    temp_range_start_end = []
    for min_temp, avg_temp, max_temp in query_result:
        temp_dict = {
            "Min": min_temp,
            "Average": avg_temp,
            "Max": max_temp
        }
        temp_range_start_end.append(temp_dict)

    # If the query returned non-null values, return the results,
    # otherwise return an error message
    if temp_range_start_end:
        return jsonify(temp_range_start_end)
    else:
        return jsonify({"error": f"Date(s) not found, invalid date range, or dates not formatted correctly."}), 404

if __name__ == '__main__':
    app.run(debug=True)