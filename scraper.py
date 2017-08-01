from lxml import html
import requests
from flask import jsonify, Flask
from apscheduler.schedulers.blocking import BlockingScheduler
from app import create_app, db
import datetime
import dateutil.parser
from flask_cors import CORS, cross_origin
import pytz
import schedule
import time
import math
from app.models import InfoBanjir, Rainfall
from stage_regression import tualang, dabong, kkrai, guillemard, jeti_kastam
import sympy as sy
from rainfall_correlation import lebir, kuala_krai, kusial


create_app().app_context().push()
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://gyxyqniicsazui:7476d139a244b41c2a78f940965f1340cbdcdf54b37709d935143100ba08b53a@ec2-23-23-244-83.compute-1.amazonaws.com:5432/d196ne33tle28f'


def scrape():
    pageurl = 'http://publicinfobanjir.water.gov.my/View/OnlineFloodInfo/PublicWaterLevel.aspx?scode=KEL'
    print("url>>>", pageurl)
    page = requests.get(pageurl)
    tree = html.fromstring(page.content)
    stations = tree.xpath('//span[starts-with(@id, "ContentPlaceHolder1_grdStation_lbl_StationName_")]/text()')
    districts = tree.xpath('//a[starts-with(@id, "ContentPlaceHolder1_grdStation_lbl_District_")]/text()')
    basins = tree.xpath('//span[starts-with(@id, "ContentPlaceHolder1_grdStation_lbl_basin_")]/text()')
    last_updates = tree.xpath('//span[starts-with(@id, "ContentPlaceHolder1_grdStation_lbl_LastUpdate_")]/text()')
    water_levels = tree.xpath('//span[starts-with(@id, "ContentPlaceHolder1_grdStation_DailyRainFall_1_")]/text()')
    with app.app_context():
        db.init_app(app)
        db.create_all()
        for station_name, district, river_basin, last_update, water_level in zip(stations, districts, basins, last_updates, water_levels):
            date_format = "%-m/%-d/%Y"
            time_format = "%H:00"
            last_update = dateutil.parser.parse(last_update)
            tz = pytz.timezone('Asia/Kuala_Lumpur')
            ctime = datetime.datetime.now(tz)
            date = datetime.datetime.strftime(last_update, date_format)
            time = datetime.datetime.strftime(ctime, time_format)
            state = 'Kelantan'
            stage_forecast = "Null"
            rainfall_forecast = "Null"
            infobanjir = InfoBanjir(station_name, district, river_basin, date, time, water_level, state, stage_forecast, rainfall_forecast)
            db.session.add(infobanjir)
            db.session.commit()

    stage_regression()


def rfscrape():
    pageurl = 'http://publicinfobanjir.water.gov.my/View/OnlineFloodInfo/PublicRainFall.aspx?scode=KEL'
    print("url>>>", pageurl)
    page = requests.get(pageurl)
    tree = html.fromstring(page.content)
    stations = tree.xpath('//span[starts-with(@id, "ContentPlaceHolder1_grdStation_lbl_StationName_")]/text()')
    districts = tree.xpath('//a[starts-with(@id, "ContentPlaceHolder1_grdStation_lbl_District_")]/text()')
    rainfalls = tree.xpath('//span[starts-with(@id, "ContentPlaceHolder1_grdStation_Label4_")]/text()')
    with app.app_context():
        db.init_app(app)
        db.create_all()
        for station_name, district, rainfall in zip(stations, districts, rainfalls):
            date_format = "%-m/%-d/%Y"
            time_format = "%H:00"
            tz = pytz.timezone('Asia/Kuala_Lumpur')
            ctime = datetime.datetime.now(tz)
            date = datetime.datetime.strftime(ctime, date_format)
            time = datetime.datetime.strftime(ctime, time_format)
            forecasted = "Null"
            print("station_name>>>", station_name)
            print("district>>>", district)
            print("rainfall>>>", rainfall)
            if rainfall == '-9999':
                rainfall = '0'
            rainfalls = Rainfall(station_name, district, date, time, rainfall, forecasted)
            db.session.add(rainfalls)
            db.session.commit()

    rainfall_correlation()


def getWaterLevel(**kwargs):
    water_level = None
    time = kwargs.get('time', None)
    input_station = kwargs.get('input_station', None)
    info_list = InfoBanjir.query.filter_by(station_name=input_station).all()
    for info_ in info_list:
        if info_.time == time:
            water_level = float(info_.water_level)
    return water_level


def getRainfall(**kwargs):
    rainfalls = {}
    time = kwargs.get('time', None)
    input_stations = kwargs.get('input_station', None)
    station_vars = kwargs.get('station_var', None)
    if isinstance(input_stations, list):
        for station_var in station_vars:
            for station in input_stations:
                info_list = Rainfall.query.filter_by(station_name=station).all()
                for info_ in info_list:
                    if info_.time == time:
                        rainfalls[station_var] = int(info_.rainfall)
    print("rainfalls>>>", rainfalls)
    return rainfalls


def calculate(formula, **kwargs):
    formulaStr = formula
    expr = sy.sympify(formulaStr)
    result = expr.subs(kwargs)
    print("type>>>>", type(result))
    print("result>>>", result)
    return str(round(float(result), 2))


def setForecasted(category, forecasted, **kwargs):
    with app.app_context():
        db.init_app(app)
        db.create_all()
        station_name = kwargs.get('station_name', None)
        node = InfoBanjir.query.filter_by(station_name=station_name).all()
        for item_ in node:
            if category == 'stage':
                item_.stage_forecast = forecasted
            elif category == 'rainfall':
                item_.rainfall_forecast = forecasted
        db.session.commit()


def stage_regression():
    tualang_level = getWaterLevel(**tualang)
    dabong_level = getWaterLevel(**dabong)
    kkrai_level = getWaterLevel(**guillemard)
    kusial_level = getWaterLevel(**jeti_kastam)
    kkrai_forecast = calculate(kkrai['formula'], tualang_level=tualang_level, dabong_level=dabong_level)
    guillemard_forecast = calculate(guillemard['formula'], kkrai_level=kkrai_level)
    jeti_forecast = calculate(jeti_kastam['formula'], kusial_level=kusial_level)
    setForecasted('stage', kkrai_forecast, **kkrai)
    setForecasted('stage', guillemard_forecast, **guillemard)
    setForecasted('stage', jeti_forecast, **jeti_kastam)


def rainfall_correlation():
    lebir_rainfalls = getRainfall(**lebir)
    lebir_forecast = calculate(lebir['formula'], **lebir_rainfalls)
    setForecasted('rainfall', lebir_forecast, **lebir)
    kuala_rainfalls = getRainfall(**kuala_krai)
    kuala_forecast = calculate(kuala_krai['formula'], **kuala_rainfalls)
    setForecasted('rainfall', kuala_forecast, **kuala_krai)
    kusial_rainfalls = getRainfall(**kusial)
    kusial_forecast = calculate(kusial['formula'], **kusial_rainfalls)
    setForecasted('rainfall', kusial_forecast, **kusial)


def scrape2():
    scrape()


def pingreq():
    purl = "http://www.kejutsahur.com/customerlist"
    req = requests.get(purl)
    print("req>>>", req)


def cleanup():
    with app.app_context():
        db.init_app(app)
        db.create_all()
        datas_ = InfoBanjir.get_all()
        for data_ in datas_:
            db.session.delete(data_)
        rainfalls_ = Rainfall.get_all()
        for info_ in rainfalls_:
            db.session.delete(info_)
        db.session.commit()


schedule.every(1).hour.do(scrape)
schedule.every(1).hour.do(rfscrape)
schedule.every(15).minutes.do(pingreq)
#schedule.every().day.at("00:00").do(scrape2)
schedule.every().sunday.at("23:59").do(cleanup)

while True:
    schedule.run_pending()
    time.sleep(1)
