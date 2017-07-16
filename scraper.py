from lxml import html
import requests
from flask import jsonify, Flask
from app.models import InfoBanjir
from apscheduler.schedulers.blocking import BlockingScheduler
from app import create_app, db
import datetime
import dateutil.parser
from flask_cors import CORS, cross_origin
import pytz
import schedule
import time
import math
from app.models import InfoBanjir


create_app().app_context().push()
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://oozvcockqcajqo:ad7803b617f02c758b5aaadf6d2bccbe9d6d2d6bb7496097f9d203774ab57cfa@ec2-107-20-250-195.compute-1.amazonaws.com:5432/d9nq4chusfe85t'


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
            date_format = "%-d-%-m-%Y"
            time_format = "%H:00"
            last_update = dateutil.parser.parse(last_update)
            tz = pytz.timezone('Asia/Kuala_Lumpur')
            ctime = datetime.datetime.now(tz)
            date = datetime.datetime.strftime(last_update, date_format)
            time = datetime.datetime.strftime(ctime, time_format)
            state = 'Kelantan'
            forecasted = "Null"
            infobanjir = InfoBanjir(station_name, district, river_basin, date, time, water_level, state, forecasted)
            db.session.add(infobanjir)
            db.session.commit()

    forecast()


def getWaterLevel(**kwargs):
    water_level = None
    time = kwargs.get('time', None)
    info_list = InfoBanjir.query.filter_by(**kwargs).all()
    for info_ in info_list:
        if info_.time == time:
            water_level = float(info_.water_level)
    return water_level


def calculate(tualang_level, dabong_level):
    forecasted = 0.895*(math.pow(tualang_level, 0.490348)*math.pow(dabong_level, 0.458358))
    return str(forecasted)


def setForecasted(forecasted, **kwargs):
    with app.app_context():
        db.init_app(app)
        db.create_all()
        node = InfoBanjir.query.filter_by(**kwargs).all()
        for item_ in node:
            item_.forecasted = forecasted
            print("finally>>>", item_.forecasted)
        db.session.commit()


def forecast():
    _tualang = {}
    _dabong = {}
    _kkrai = {}
    time_format = "%H:00"
    date_format = "%-d-%-m-%Y"
    tz = pytz.timezone('Asia/Kuala_Lumpur')
    ctime = datetime.datetime.now(tz)
    time = datetime.datetime.strftime(ctime, time_format)
    date = datetime.datetime.strftime(ctime, date_format)
    _tualang['station_name'] = "Sg.Lebir di Tualang"
    _tualang['time'] = time
    _tualang['date'] = date
    _dabong['station_name'] = "Sg.Galas di Dabong"
    _dabong['time'] = time
    _dabong['date'] = date
    tualang_level = getWaterLevel(**_tualang)
    dabong_level = getWaterLevel(**_dabong)
    print("tualang_level>>>>", tualang_level)
    print("dabong_level>>>>", dabong_level)
    forecasted = calculate(tualang_level, dabong_level)
    print("forecasted>>>", forecasted)
    _kkrai['station_name'] = "Sg.Kelantan di Kuala Krai"
    _kkrai['time'] = time
    _kkrai['date'] = date
    setForecasted(forecasted, **_kkrai)


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
        db.session.commit()

schedule.every(1).hour.do(scrape)
schedule.every(15).minutes.do(pingreq)
#schedule.every().day.at("00:00").do(scrape2)
schedule.every().sunday.at("23:59").do(cleanup)

while True:
    schedule.run_pending()
    time.sleep(1)
