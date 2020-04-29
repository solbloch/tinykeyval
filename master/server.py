#!/usr/bin/python3

import plyvel
import argparse
import requests as r
import bottle
from bottle import route, get, put, delete, Response
from bottle import request, run, redirect, abort, error


bottle.BaseRequest.MEMFILE_MAX = 2000000000


class Volume:
    def __init__(self,ip):
        self.ip = ip
    def content_json(self):
        req = r.get('http://' + self.ip)

        # If volume server has no data.
        if req.status_code == 404:
            return None
        else:
            return req.json()
    def size(self):
        req = r.get('http://' + self.ip)

        # If volume server has no data.
        if req.status_code == 404:
            return 0
        else:
            return sum([f['size'] for f in req.json()])
    def __lt__(self, other):
        return self.size() < other.size()
    def __repr__(self):
        return '<Volume ip:{0} size:{1}>'.format(self.ip, self.size())

class MasterServer:
    def __init__(self, db, replications, volumes):
        self.db = plyvel.DB(db, create_if_missing=True)
        self.replications = replications
        self.volumes = [Volume(ip) for ip in volumes.split(',')]
        self.fill_db()

        # use implicit bottle.app for routes.
        @route('/')
        def homeroute():
            # keys and vals
            kvs = [key.decode(encoding='UTF-8') + ': ' 
                    + val.decode(encoding='UTF-8') 
                    + '\n' for key,val in self.db]

            return [vol.ip + ': ' + str(vol.size()) + '\n' for vol in self.volumes]

        @error(404)
        def error404(error):
            return '404: ' + error.body

        @error(409)
        def error409(error):
            return '409: ' + error.body

        @get('/:key')
        def get_val(key):
            locations = self.db.get(key.encode('UTF-8'))

            if locations == None:
                abort(404, 'no file')
            else:
                locations = locations.decode(encoding='UTF-8').split(',')
                found_at = ''
                for location in locations:
                    if r.head('http://' + location + '/' + key).status_code == 200:
                        found_at = location
                        break

                redirect('http://' + found_at + '/' + key)

        @put('/:key')
        def put_val(key):
            'put file on n servers with least data.'

            # make sure the key is available, else abort 409
            if self.db.get(key.encode('UTF-8')) != None:
                abort(409, 'key exists')

            volumes = sorted(self.volumes)[:self.replications]

            self.db.put(key.encode('UTF-8'), ','.join([vol.ip for vol in volumes]).encode('UTF-8'))

            for vol in volumes:
                r.put(('http://'+vol.ip +'/'+key).encode('UTF-8'), request.body)


    def fill_db(self):
        'Fill db from volumes.'
        for vol in self.volumes:
            for f in vol.content_json():
                # If the object already exists, add the new location to the list.
                if self.db.get(f['name'].encode('UTF-8')) == None:
                    self.db.put(f['name'].encode('UTF-8'), vol.ip.encode('UTF-8'))
                else:
                    # get current location list, see if new location is already there
                    loc_list = self.db.get(f['name'].encode('UTF-8')).split(b',')
                    if vol.ip.encode('UTF-8') not in loc_list:
                        newvalue = self.db.get(f['name'].encode('UTF-8')) + (',' + vol.ip).encode('UTF-8')
                        self.db.put(f['name'].encode('UTF-8'), newvalue)


if __name__ == '__main__':
    # parse, hostname, port, master / volume
    parser = argparse.ArgumentParser(description='Master server for tinykeyval, needs at least two volume servers.')
    parser.add_argument('-db', help='Database file path.')
    parser.add_argument('-rep', help='How many replications to have. Bounded by volume number.', default=2)
    parser.add_argument('-volumes', help='Comma separated list of volume servers.')

    args = parser.parse_args()

    if len(args.volumes.split(',')) < 2:
        raise ValueError('Need at least two volumes.')

    master = MasterServer(args.db, int(args.rep), args.volumes)

    run(host='0.0.0.0', port=8080, server='bjoern')

