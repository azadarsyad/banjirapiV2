# app/__init__.py
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, Blueprint
from flask import Flask, render_template, redirect, url_for, request, session, flash
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
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
    db.init_app(app)

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
            infobanjir_ = InfoBanjir.get_all()
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
