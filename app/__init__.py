# app/__init__.py
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, Blueprint
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_cors import CORS, cross_origin
# initialize sql-alchemy
db = SQLAlchemy()
info = Blueprint('info', __name__)

global results

POSTGRES = {
    'user': 'shads',
    'pw': 'wrongpassword',
    'db': 'infobanjir',
    'host': 'localhost',
    'port': '5432',
}


def create_app():
    from app.models import InfoBanjir
    app = Flask(__name__)
    CORS(app)
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://hazasxpfrsxmio:48604166211dca32b6a10afb48c6bb87a8f750265d588a1d4173e25539251efa@ec2-23-23-234-118.compute-1.amazonaws.com:5432/d5832l2rq92ogc'
    db.init_app(app)

    @app.route('/')
    def home():
        return "Welcome to BanjirAPIv2"

    @app.route('/<string:state>', methods=['GET'])
    def infobanjir(state=None):
        results = None
        querystring = {}
        if bool(request.args):
            querystring = request.args.to_dict(flat=True)
            querystring['state'] = state
            infobanjir_ = InfoBanjir.query.filter_by(**querystring).all()
            results = []
            for info_ in infobanjir_:
                obj = {
                 'state': info_.state,
                 'station_name': info_.station_name,
                 'district': info_.district,
                 'river_basin': info_.river_basin,
                 'date': info_.date,
                 'time': info_.time,
                 'water_level': info_.water_level,
                }
                results.append(obj.copy())
        else:
            querystring['state'] = state
            infobanjir_ = InfoBanjir.query.filter_by(state=state).all()
            results = []
            for info_ in infobanjir_:
                obj = {
                 'state': info_.state,
                 'station_name': info_.station_name,
                 'district': info_.district,
                 'river_basin': info_.river_basin,
                 'date': info_.date,
                 'time': info_.time,
                 'water_level': info_.water_level,
                }
                results.append(obj.copy())
        response = jsonify(results)
        return response
    return app
