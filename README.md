# tinykeyval

Inspired by geohot's [minikeyval](https://github.com/geohot/minikeyvalue) and [SeaweedFS](https://github.com/chrislusf/seaweedfs). 

Python master server with [leveldb](https://github.com/google/leveldb) which has key, values of filename, then a comma separated list of IP's of the volumes where that file is stored.

## Usage
Run the docker containers of volumes:
```bash
docker run --name vol1 -p 33333:80 -d volume
docker run --name vol2 -p 33334:80 -d volume
```

Then run the master:
```bash
docker run --name master -p 8888:8080 -d master ./server.py -rep 2 -db /tmp/db -volumes 192.168.1.30:33333,192.168.1.30:33334
```

When the master server opens it scans all the volumes to add to the leveldb.

Then you can use like so:
```bash
curl -X PUT -d "testVALUE" localhost:8888/testkey

# important to use -L so it follow the redirect to the volume
curl -L localhost:8888/testkey
=> testVALUE
```
