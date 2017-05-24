from flask import Flask
from flask import request
from pony.orm import *
from datetime import datetime
import os

app = Flask(__name__)
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("PORT"))
