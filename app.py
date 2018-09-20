from flask import Flask
from pyroute2 import IPRoute
from flask import json


app = Flask(__name__)

ip = IPRoute()

@app.route("/iproutes/<string:dest>/<string:port>/<string:gateway>/<int:mtu>/<int:hoplimit>", methods = ['PUT'])
def addRoute(dest, gateway, port, mtu, hoplimit):
    ip.route('add',
             dst = dest + ':' + port,
             gtw = gateway,
             metrics = {'mtu': mtu,
                      'hoplimit': hoplimit})

@app.route("/iproutes/<string:dest>/<string:port>/<string:gateway>/<int:mtu>/<int:hoplimit>", methods = ['DELETE'])
def delRoute(dest, gateway, port, mtu, hoplimit):
    ip.route('del',
             dst = dest + '"' + port,
             gtw = gateway,
             metrics = {
                 'mtu' : mtu,
                 'hoplimit' : hoplimit})

@app.route("/iproutes", methods = ['GET'])
def getRoutes():
    response = app.response_class(
        response = str(ip.get_routes()),
        status = 200,
        mimetype = 'application/raw')
    return response





if __name__ == '__main__':
    app.run(port=5002)
