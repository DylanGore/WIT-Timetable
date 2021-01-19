import json
import pytz
from icalendar import Calendar, Event
import recurring_ical_events
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import get_timetable as api
from datetime import datetime, timedelta

# configuration
DEBUG = True
TZ = pytz.timezone('Europe/Dublin')
FIRST_DAY = datetime(2020, 9, 28, 0, 0, tzinfo=TZ)
LAST_DAY = datetime(2020, 12, 19, 0, 0, tzinfo=TZ)

DAY_OFFSET = {
    'monday': 0,
    'tuesday': 1,
    'wednesday': 2,
    'thursday': 3,
    'friday': 4,
}

# instantiate the app
app = Flask(__name__, static_folder='dist', template_folder='dist')
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


# sanity check route
@app.route('/', methods=['GET'])
def catch_all():
    return render_template('index.html')


@app.route('/get-timetable', methods=['POST'])
def route_get_timetable():
    post_data = json.loads(request.data.decode('utf-8'))

    # department = str(request.data.get('department'))
    # programme = str(request.data.get('programme'))

    # print(department, programme)

    return jsonify({'timetable': api.get_timetable(post_data['department'], post_data['programme'])})


@app.route('/get-calendar', methods=['GET'])
def route_get_calendar():
    department = str(request.args.get('dept'))
    programme = str(request.args.get('prog'))
    groups = str(request.args.get('groups')).split(',')

    print(department, programme, groups)

    timetable = api.get_timetable(department, programme)
    calendar = Calendar()
    calendar.add('prodid', '-//WIT Timetable//mxm.dk//')
    calendar.add('version', '1.0')
    calendar_events = []

    count = 0
    for event in timetable:
        cal_event = Event()
        if any(item in groups for item in event['groups']):
            if event['online']:
                location = f"{event['room']} (Online)"
            else:
                location = event['room']
            count += 1
            start_time = event['time'].split(':')
            event_start = FIRST_DAY + timedelta(hours=int(start_time[0]), minutes=int(start_time[1])) + timedelta(days=DAY_OFFSET[event['day'].lower()])
            cal_event['summary'] = event['name']
            cal_event['location'] = location
            cal_event['dtstart'] = event_start.isoformat()
            cal_event['dtend'] = (event_start + timedelta(hours=int(event['duration']))).isoformat()
            cal_event.add('rrule', {'FREQ': 'WEEKLY', 'BYDAY': event['day'][:2].upper(), 'UNTIL': LAST_DAY})
            calendar.add_component(cal_event)

    file = open('timetable.ics', 'wb')
    file.write(calendar.to_ical())
    file.close()
    # return jsonify({'timetable': api.get_timetable(post_data['department'], post_data['programme'])})
    return jsonify({'timetable': timetable})


def display(cal):
    return str(cal.to_ical()).replace('\r\n', '\n').strip()


if __name__ == '__main__':
    app.run(host='0.0.0.0')
