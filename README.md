# redis-tools
Simple repository of python redis tools, mostly used for keys synchronization between 2 redis.

## Usage
### redis-sync
Use `redis-sync` command to compare keys prefixed by a specific namespace between 2 Redis clusters and
copy new keys from source Redis to target Redis.

### redis-monitor
Use `redis-monitor` command to watch Redis key prefixed by a specific namespace on Redis cluster
(can monitor a second Redis cluster if `REDIS_TARGET_ENDPOINT` is set).

## Installation
Installation can be done using `make`. Read the `Makefile` to get the manual commands.
- Build the Docker image: `make docker`
- Install redis-tools locally: `make install`

## Configuration
Configuration is managed by environment variables:
```
DRY_RUN=yes                      # use "yes" with sync command to only compare keys
INTERVAL=30                      # in seconds, use 0 to run the command only once
LOG_LEVEL=INFO                   # use standard logging levels
REDIS_ENDPOINT=localhost:6379    # use ip:port or fqdn:port
REDIS_NAMESPACE=*                # use "*" to manage all keys
                                 # use "ns:*" to manage only keys prefixed by "ns:" namespace
REDIS_TARGET_ENDPOINT=redis:6379 # use ip:port or fqdn:port
```

## Tests
A docker-compose.yaml is available which run a redis-tools container and 2 redis databases
containers for local tests.
```
docker-compose up
```

To manage the 2 redis databases (test load injection for example), you can run the Docker image
with interactive python:
```
$ docker run -it --network=redistools_default redis-tools python
In [1]: import redis
In [2]: r1 = redis.StrictRedis(host='redis-source')
In [3]: r2 = redis.StrictRedis(host='redis-target')
In [4]: r1.keys()
In [5]: r1.set('ns:foo1', 'bar1')
In [6]: r1.set('ns:foo2', 'bar2')
In [7]: r1.keys()
In [8]: r2.keys()
```
