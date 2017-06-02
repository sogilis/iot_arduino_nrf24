from flask import Flask, request, render_template, redirect, url_for
from pony.orm import *
from datetime import datetime, timedelta
import os
import json

app = Flask(__name__)
db = Database()

class SensorData(db.Entity):
    date = Required(datetime)
    name = Required(str)
    dataType = Required(str)
    data = Required(float)

class OrderData(db.Entity):
    date = Required(datetime)
    nodeId = Required(int)
    orderType = Required(str)
    orderData = Required(int)

db.bind('postgres', user=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], database=os.environ["DB_NAME"], port=os.environ["DB_PORT"])
db.generate_mapping(create_tables=True)

@app.route("/")
def sensor_list():
    with db_session:
        types_list = {}
        names = select((s.name) for s in SensorData)[:]
        for n in names:
            k = select(d.dataType for d in SensorData if d.name == n)[:]
            types_list[n] = k
        print types_list
    return render_template('sensor_list.html', sensors=names, types_list=types_list)

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
    received_args = request.args
    if 'name' in received_args and 'type' in received_args:
        with db_session:
            db_result = select(d for d in SensorData if (d.date >= datetime.now() - timedelta(days=1)
                                                         and d.name == received_args['name']
                                                         and d.dataType == received_args['type'])).order_by(SensorData.date)[:]
            dates = []
            data = []
            for line in db_result:
                dates.append(line.date.isoformat())
                #print 'one : ' + str(line.date)
                #print 'two : ' + str(line.date.isoformat())
                data.append(line.data)
                print line.date, line.data
        return render_template('graph.html', dates=dates, data=data, data_type=received_args['type'])
    else:
        return redirect(url_for('sensor_list'))

@app.route('/get_orders', methods=['GET'])
def get_orders():
    received_args = request.args
    with db_session:
        if 'nodeId' in received_args:
            next_order = select(d for d in OrderData if (d.date >= datetime.now()
                                                         and d.nodeId == received_args['nodeId'])).order_by(OrderData.date).first()
            if next_order:
                res = {}
                res['date'] = int((next_order.date - datetime.now()).total_seconds())
                res['nodeId'] = next_order.nodeId
                res['orderType'] = next_order.orderType
                res['orderData'] = next_order.orderData

                return json.dumps(res)
            else:
                return '{}'
        else:
            db_result = select(d for d in OrderData if (d.date >= datetime.now() - timedelta(days=1))).order_by(OrderData.date)[:]
            res = []
            for line in db_result:
                cur = {}
                cur['date'] = int((line.date - datetime.now()).total_seconds())
                cur['nodeId'] = line.nodeId
                cur['orderType'] = line.orderType
                cur['orderData'] = line.orderData
                res.append(cur)
            return json.dumps(res)

@app.route('/post_order', methods=['GET'])
def post_order():
    received_args = request.args
    if 'nodeId' in received_args and 'orderType' in received_args and 'orderDate' in received_args and 'orderData' in received_args:
        print int(received_args['nodeId'])
        print received_args['orderType']
        print received_args['orderData']
        dateO = datetime.strptime(received_args['orderDate'],'%d/%m/%Y-%H:%M')
        print dateO
        with db_session:
            od = OrderData(nodeId=int(received_args['nodeId']), orderType=received_args['orderType'],
                               orderData=int(received_args['orderData']), date=dateO)
            commit()
        return "OK"
    else:
        return "BAD ARGS"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("PORT"))
