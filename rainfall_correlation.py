import datetime
import pytz

time_format = "%H:00"
date_format = "%-d/%-m/%Y"
tz = pytz.timezone('Asia/Kuala_Lumpur')
ctime = datetime.datetime.now(tz)
time = datetime.datetime.strftime(ctime, time_format)
date = datetime.datetime.strftime(ctime, date_format)

lebir = {
    'input_station': ['Gunung Gagau1', 'Kampung Aring', 'Kampung Laloh', 'Kampung Tualang'],
    'station_var': ['gagau', 'laloh', 'aring', 'tualang'],
    'station_name': "Sg.Lebir di Tualang",
    'formula': "23.2*gagau**0.005584*laloh**0.001087*aring**0.004091*tualang**0.005534",
    'time': time,
    'date': date,
}

kuala_krai = {
    'input_station': ['Dabong', 'Kampung Laloh', 'Kuala Krai'],
    'station_var': ['dabong', 'laloh', 'krai'],
    'station_name': "Sg.Kelantan di Kuala Krai",
    'formula': "16.5*dabong**0.0096*laloh**0.000632*krai**0.012563",
    'time': time,
    'date': date,
}

kusial = {
    'input_station': ['Kuala Krai', ],
    'station_name': "Sg.Kelantan di Kusial",
    'station_var': ['krai'],
    'formula': "8.13*krai**0.03",
    'time': time,
    'date': date,
}


