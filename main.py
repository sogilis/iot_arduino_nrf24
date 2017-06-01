from flask import Flask
from flask import request, render_template
from pony.orm import *
from datetime import datetime, timedelta
from flask_sse import sse
import os

app = Flask(__name__)
app.config["REDIS_URL"] = os.environ["REDIS_URL"]
app.register_blueprint(sse, url_prefix='/stream')
db = Database()

class SensorData(db.Entity):
    date = Required(datetime)
    name = Required(str)
    dataType = Required(str)
    data = Required(float)

db.bind('postgres', user=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], database=os.environ["DB_NAME"], port=os.environ["DB_PORT"])
db.generate_mapping(create_tables=True)

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/send_sse', methods=['GET'])
def send_message():
    received_args = request.args
    status = received_args['status']
    sse.publish({"message": status}, type='greeting')
    print 'message sent' + status
    return "Message sent!"

@app.route("/sensor_list")
def sensor_list():
    with db_session:
        names = select((s.name) for s in SensorData)[:]
    return render_template('sensor_list.html', sensors=names)

@app.route('/post_sensor_data', methods=['GET'])
def post_sensor_data():
    received_args = request.args
    print received_args['data_type']
    print received_args['name']
    print received_args['data']
    with db_session:
        sd = SensorData(name=received_args['name'], dataType=received_args['data_type'], data=float(received_args['data']), date=datetime.now())
        commit()
    return "OK"

@app.route('/get_sensor_data', methods=['GET'])
def get_sensor_data():
    with db_session:
        received_args = request.args
        db_result = select(d for d in SensorData if (d.date >= datetime.now() - timedelta(days=1)
                                                     and d.name == received_args['name'])).order_by(SensorData.date)[:]
        dates = []
        data = []
        for line in db_result:
            dates.append(line.date)
            data.append(line.data)
            print line.date, line.data
    return render_template('graph.html', dates=dates, data=data)

#if __name__ == "__main__":
#    app.run(host="0.0.0.0", port=os.getenv("PORT"))
