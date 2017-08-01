import datetime
import pytz

time_format = "%H:00"
date_format = "%-m/%-d/%Y"
tz = pytz.timezone('Asia/Kuala_Lumpur')
ctime = datetime.datetime.now(tz)
time = datetime.datetime.strftime(ctime, time_format)
date = datetime.datetime.strftime(ctime, date_format)

tualang = {
        'input_station': "Sg.Lebir di Tualang",
        'time': time,
        'date': date,
    }

dabong = {
        'input_station': "Sg.Galas di Dabong",
        'time': time,
        'date': date,
    }

kkrai = {
    'station_name': "Sg.Kelantan di Kuala Krai",
    'formula': "0.895*tualang_level**0.490348*dabong_level**0.458358",
    'time': time,
    'date': date,
}

guillemard = {
    'input_station': "Sg.Kelantan di Kuala Krai",
    'station_name': "Sg.Kelantan di Kusial",
    'formula': "0.395043*kkrai_level**1.163935",
    'time': time,
    'date': date,
}

jeti_kastam = {
    'input_station': "Sg.Kelantan di Kusial",
    'station_name': "Sg.Kelantan di Jeti Kastam",
    'formula': "0.01874*kusial_level**1.969169",
    'time': time,
    'date': date,
}
