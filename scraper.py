from lxml import html
import requests
from flask import jsonify, Flask
from app.models import InfoBanjir
from apscheduler.schedulers.blocking import BlockingScheduler
from app import create_app, db
import datetime
import dateutil.parser

sched = BlockingScheduler()
create_app().app_context().push()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://hazasxpfrsxmio:48604166211dca32b6a10afb48c6bb87a8f750265d588a1d4173e25539251efa@ec2-23-23-234-118.compute-1.amazonaws.com:5432/d5832l2rq92ogc'


@sched.scheduled_job('interval', minutes=1)
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
                date_format = "%d-%m-%Y"
                time_format = "%H:%M:%S"
                last_update = dateutil.parser.parse(last_update)
                date = datetime.datetime.strftime(last_update, date_format)
                time = datetime.datetime.strftime(last_update, time_format)
                infobanjir = InfoBanjir(station_name, district, river_basin, date, time, water_level, state)
                db.session.add(infobanjir)
                db.session.commit()
            db.close()


@sched.scheduled_job('cron', day_of_week='mon-sun', hour=0)
def scrape2():
    scrape()


@sched.scheduled_job('cron', day_of_week='sun', hour=23)
def cleanup():
    with app.app_context():
        db.init_app(app)
        db.create_all()
        datas_ = InfoBanjir.get_all()
        for data_ in datas_:
            db.session.delete(data_)
        db.session.commit()
sched.start()
