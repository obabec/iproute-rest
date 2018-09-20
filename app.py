from flask import Flask
from pyroute2 import IPRoute
from flask import json
import jsonpickle

app = Flask(__name__)

ip = IPRoute()


class Interface(object):
    name = ''
    ip = ''
    mask = 0

    def set_ip(self, ip):
        self.ip = ip

    def set_all(self, name, ip, mask):
        self.ip = ip
        self.mask = mask
        self.name = name


class Network(object):
    ipAddress = ""
    mask = 0

    def set_all(self, ipAddress, mask):
        self.ipAddress = ipAddress
        self.mask = mask


class Route(object):
    dest = Network()
    rNetworkInterface = Interface()

    def set_all(self, dest, networkInterface):
        self.dest = dest
        self.rNetworkInterface = networkInterface



@app.route('/iproutes/<string:dest>/<int:mask>/<string:gateway>/<int:mtu>/<int:hoplimit>', methods=['PUT'])
def add_route(dest, gateway, mask, mtu, hoplimit):
    ip.route('add',
             dst=dest + '/' + str(mask),
             gateway=gateway,
             metrics={'mtu': mtu,
                      'hoplimit': hoplimit})
    return app.response_class(status=200)


@app.route('/iproutes/<string:dest>/<int:mask>/<string:gateway>/<int:mtu>/<int:hoplimit>', methods=['DELETE'])
def del_route(dest, gateway, mask, mtu, hoplimit):
    return ip.route('del',
                    dst=dest + '/' + str(mask),
                    gateway=gateway,
                    metrics={'mtu': mtu,
                             'hoplimit': hoplimit})
    return app.response_class(status=200)


@app.route('/iproutes/interfaces', methods=['GET'])
def get_interfaces():
    links = [x['attrs'][0][1] for x in ip.get_links()]
    addresses = [x['attrs'][0][1] for x in ip.get_addr(family=2)]
    masks = [x['prefixlen'] for x in ip.get_addr(family=2)]
    interfaces = []
    for x in range(0, len(addresses)):
        interface = Interface()
        interface.set_all(links[x], addresses[x], masks[x])
        interfaces.append(interface)

    response = app.response_class(
        response=jsonpickle.encode(interfaces, unpicklable=False),
        status=200,
        mimetype='application/json')
    return response


def is_route_default(rts, x):
    if rts[x]['dst_len'] is not 0:
        return False
    return True


def get_default_routes():
    rts = ip.get_default_routes(table=254, family=2)
    routes = []
    for x in range(0, len(rts)):
        route = Route()
        rNetworkInterface = Interface()
        rNetworkInterface.set_all('', rts[x].get_attr('RTA_GATEWAY'), None)
        network = Network()
        network.set_all('default', None)
        route.set_all(network, rNetworkInterface)
        routes.append(route)

    return routes


@app.route('/iproutes', methods=['GET'])
def get_routes():
    rts = ip.get_routes(table=254, family=2)
    routes = []
    for x in range(0, len(rts)):
        route = Route()
        rNetworkInterface = Interface()
        network = Network()

        if is_route_default(rts, x):
            continue
        else:
            if rts[x].get_attr('RTA_PREFSRC') is None:
                rNetworkInterface.set_all('', rts[x].get_attr('RTA_GATEWAY'), None)
            else:
                rNetworkInterface.set_all('', rts[x].get_attr('RTA_PREFSRC'), None)
            network.set_all(rts[x].get_attr('RTA_DST'), rts[x]['dst_len'])
            route.set_all(network, rNetworkInterface)
            routes.append(route)

    routes.extend(get_default_routes())
    response = app.response_class(

        response=jsonpickle.dumps(routes, unpicklable=False),
        status=200,
        mimetype='application/json')
    return response


@app.route('/iproutes/default/<string:gateway>', methods=['PUT'])
def add_default(gateway):
    ip.route(
        'add',
        dst='default',
        gateway=gateway)
    return app.response_class(status=200)


@app.route('/iproutes/default/<string:gateway>', methods=['DELETE'])
def del_default(gateway):
    ip.route(
        'del',
        dst='default',
        gateway=gateway)
    return app.response_class(status=200)


@app.route('/')
def default():
    return app.response_class(status=200)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
