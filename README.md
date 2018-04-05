# redis-tools
Simple repository of python redis tools, mostly used for keys synchronization between 2 redis.

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

## Usage
### redis-sync
Use `redis-sync` command to compare keys prefixed by a specific namespace between 2 Redis clusters and
copy new keys from source Redis to target Redis.
```
$ docker run -e REDIS_ENDPOINT=172.17.0.1:6379 -e REDIS_TARGET_ENDPOINT=172.17.0.1:6380 -e REDIS_NAMESPACE=ns:sessions:* -e INTERVAL=10 -e DRY_RUN=no redis-tools redis-sync
root 2018-04-05 14:15:59,666 INFO Get redis keys starting by namespace "ns:sessions:*" for redis endpoint "172.17.0.1:6379
root 2018-04-05 14:15:59,668 INFO Get redis keys starting by namespace "ns:sessions:*" for redis endpoint "172.17.0.1:6380
root 2018-04-05 14:15:59,669 INFO No new keys found on 172.17.0.1:6379
root 2018-04-05 14:15:59,669 INFO Every keys are already existing in 172.17.0.1:6380
root 2018-04-05 14:16:09,670 INFO Get redis keys starting by namespace "ns:sessions:*" for redis endpoint "172.17.0.1:6379                                                                                   root 2018-04-05 14:16:09,673 INFO Get redis keys starting by namespace "ns:sessions:*" for redis endpoint "172.17.0.1:6380
root 2018-04-05 14:16:09,674 INFO New keys: {b'ns:sessions:tds5', b'ns:sessions:tds4', b'ns:sessions:tds6', b'ns:sessions:tds8', b'ns:sessions:tds0', b'ns:sessions:tds2', b'ns:sessions:tds7', b'ns:sessions:tds3', b'ns:sessions:tds1', b'ns:sessions:tds9'}
root 2018-04-05 14:16:09,674 INFO New key to add on 172.17.0.1:6380
root 2018-04-05 14:16:09,689 INFO Execute pipeline with 10 tasks
root 2018-04-05 14:16:19,701 INFO Get redis keys starting by namespace "ns:sessions:*" for redis endpoint "172.17.0.1:6379
root 2018-04-05 14:16:19,704 INFO Get redis keys starting by namespace "ns:sessions:*" for redis endpoint "172.17.0.1:6380
root 2018-04-05 14:16:19,705 INFO No new keys found on 172.17.0.1:6379
root 2018-04-05 14:16:19,706 INFO Every keys are already existing in 172.17.0.1:6380
```

### redis-monitor
Use `redis-monitor` command to watch Redis key prefixed by a specific namespace on Redis cluster
(can monitor a second Redis cluster if `REDIS_TARGET_ENDPOINT` is set).
```
$ docker run -e REDIS_ENDPOINT=172.17.0.1:6379 -e REDIS_TARGET_ENDPOINT=172.17.0.1:6380 -e REDIS_NAMESPACE=ns:sessions:* -e INTERVAL=0 redis-tools redis-monitor
root 2018-04-05 14:18:32,533 INFO Get redis keys starting by namespace "ns:sessions:*" for redis endpoint "172.17.0.1:6379
root 2018-04-05 14:18:32,536 INFO Keys for Redis Source 172.17.0.1:6379: {b'ns:sessions:tds3', b'ns:sessions:tds5', b'ns:sessions:tds9', b'ns:sessions:tds6', b'ns:sessions:tds2', b'ns:sessions:tds0', b'ns:sessions:tds1', b'ns:sessions:tds8', b'ns:sessions:tds7', b'ns:sessions:tds4'}
root 2018-04-05 14:18:32,537 INFO Get redis keys starting by namespace "ns:sessions:*" for redis endpoint "172.17.0.1:6380
root 2018-04-05 14:18:32,537 INFO Keys for Redis Target 172.17.0.1:6380: {b'ns:sessions:tds3', b'ns:sessions:tdc9', b'ns:sessions:tdc8', b'ns:sessions:tds5', b'ns:sessions:tds9', b'ns:sessions:tds6', b'ns:sessions:tds2', b'ns:sessions:tds0', b'ns:sessions:tdc2', b'ns:sessions:tdc5', b'ns:sessions:tdc6', b'ns:sessions:tds1', b'ns:sessions:tdc7', b'ns:sessions:tds8', b'ns:sessions:tdc1', b'ns:sessions:tdc4', b'ns:sessions:tdc0', b'ns:sessions:tds7', b'ns:sessions:tds4', b'ns:sessions:tdc3'}
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
