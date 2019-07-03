import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt


engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        "Available Routes:<br>"
        "/api/v1.0/precipitation<br>"
        "/api/v1.0/stations<br>"
        "/api/v1.0/tobs<br>"
        "/api/v1.0/start<br>"
        "/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(Measurement.date, Measurement.prcp).all()
    
    all_prcp= []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def station():
    results = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    
    info_all = []
    for id, station, name, lat, log, ele in results:
        info = {}
        info["id"] = id
        info["station"] = station
        info["name"] = name
        info["lat"] = lat
        info["log"] = log
        info["ele"] = ele
        info_all.append(info)
    
    return jsonify(info_all)

@app.route("/api/v1.0/tobs")
def tobs():
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago)

    all_tobs = []
    for date, tobs in results:
        temp = {}
        temp[date] = tobs
        all_tobs.append(temp)

    return jsonify(all_tobs)


def calc_temps(start_date, end_date = "2017-08-23"):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()


@app.route("/api/v1.0/<start>")
def temp_start(start):
    tmin, tavg, tmax = calc_temps(start)[0]
    
    result = {
        "TMIN": tmin,
        "TAVG": tavg,
        "TMAX": tmax
    }

    return jsonify(result)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    tmin, tavg, tmax = calc_temps(start, end)[0]
    
    result = {
        "TMIN": tmin,
        "TAVG": tavg,
        "TMAX": tmax
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)