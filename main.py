from flask import Flask
from flask import request
from pony.orm import *
from datetime import datetime
import os
import psycopg2
import urlparse

app = Flask(__name__)
db = Database()

class SensorData(db.Entity):
    date = Required(datetime)
    name = Required(str)
    dataType = Required(str)
    data = Required(float)

db.bind('postgres', user='gqwvmfcuafjnyo', password='0c351d7638150b486456007a92105b755138cf549acdc2ca154f873126e86915', host='ec2-54-75-231-195.eu-west-1.compute.amazonaws.com', database='d2gt8gooa94mge', port='5432')
db.generate_mapping(create_tables=True)

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/post_sensor_data', methods=['GET'])
def post_sensor_data():
    #urlparse.uses_netloc.append("postgres")
    #url = urlparse.urlparse(os.environ["DATABASE_URL"])

    #print url.path[1:]
    #print url.username
    #print url.password
    #print url.hostname
    #print url.port
    received_args = request.args
    print received_args['data_type']
    print received_args['name']
    print received_args['data']
    with db_session:
        sd = SensorData(name=received_args['name'], dataType=received_args['data_type'], data=float(received_args['data']), date=datetime.now())
        commit()
    return "OK"
    #print request.form['data_type']
    #print request.form['data']

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("PORT"))
