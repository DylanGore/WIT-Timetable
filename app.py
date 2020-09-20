import json
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import get_timetable as api

# configuration
DEBUG = True

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


if __name__ == '__main__':
    app.run(host='0.0.0.0')
