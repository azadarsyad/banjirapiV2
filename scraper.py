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


create_app().app_context().push()
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://hazasxpfrsxmio:48604166211dca32b6a10afb48c6bb87a8f750265d588a1d4173e25539251efa@ec2-23-23-234-118.compute-1.amazonaws.com:5432/d5832l2rq92ogc'


def scrape():
    states = {
       'TRG': 'Terengganu',
       'PLS': 'Perlis',
       'WLH': 'Kuala Lumpur',
       'KDH': 'Kedah',
       'PNG': 'Penang',
       'PRK': 'Perak',
       'SEL': 'Selangor',
       'NSN': 'Negeri Sembilan',
       'PHG': 'Pahang',
       'KEL': 'Kelantan',
       'JHR': 'Johor',
       'MLK': 'Melaka',
       'SRK': 'Sarawak',
       'SAB': 'Sabah',
       'WLP': 'Wilayah Persekutuan Labuan',
    }
    for stateExt, state in states.items():
        pageurl = 'http://publicinfobanjir.water.gov.my/View/OnlineFloodInfo/PublicWaterLevel.aspx?scode='+stateExt
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
                time_format = "%H:%M:%S"
                last_update = dateutil.parser.parse(last_update)
                tz = pytz.timezone('Asia/Kuala_Lumpur')
                cdate = datetime.datetime.now(tz)
                date = datetime.datetime.strftime(last_update, date_format)
                time = datetime.datetime.strftime(cdate, time_format)
                print("time>>>", time)
                infobanjir = InfoBanjir(station_name, district, river_basin, date, time, water_level, state)
                db.session.add(infobanjir)
                db.session.commit()


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
schedule.every().day.at("00:00").do(scrape2)
schedule.every().sunday.at("23:59").do(cleanup)

while True:
    schedule.run_pending()
    time.sleep(1)
#sched = BlockingScheduler()
#sched.add_job(scrape, 'interval', hours=1)
#sched.add_job(scrape2, 'cron', day_of_week='mon-sun', hour=0)
#sched.add_job(cleanup, 'cron', day_of_week='sun', hour=23)
#sched.start()
