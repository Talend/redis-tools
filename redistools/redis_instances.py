"""
Redis Instances module
"""

import logging
import re
import redis

# Constants
ip_pattern = '(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])'
hostname_pattern = '(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z\-]*[A-Za-z])'
port_pattern = '([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])'
endpoint_pattern = '^({}|{}):{}$'.format(ip_pattern, hostname_pattern, port_pattern)


class RedisInstance(object):
    """
    Redis instance
    """

    def __init__(self, endpoint):
        """
        Initialize a Redis instance
        """

        # Validate redis endpoint format
        if re.match(endpoint_pattern, endpoint):
            self._endpoint = endpoint
            hostname, port = self._endpoint.split(':')
            self._hostname = hostname
            self._port = port

            logging.debug('Redis hostname: {0}'.format(self._hostname))
            logging.debug('Redis port: {0}'.format(self._port))

            self._redis = redis.StrictRedis(host=hostname, port=port, db=0)

        else:
            logging.info('ERROR: {} is not a valid endpoint (ip:port or fqdn:port)'.format(endpoint))
            exit(1)

    def get_endpoint(self):
        """
        Get Redis endpoint
        """

        logging.debug('Redis endpoint: {0}'.format(self._endpoint))
        return self._endpoint

    def list_keys(self, namespace):
        """
        List Redis keys matching specified namespace
        """

        logging.info('Get redis keys starting by namespace "{0}" for redis endpoint "{1}'.format(
            namespace, self._endpoint))

        # Create iterator to scan all keys matching namespace
        keys_iter = self._redis.scan_iter(match=namespace)

        # Using set type for list of keys will help us to compare list of keys more efficiently
        keys = set()
        for k in keys_iter:
            logging.debug('Add key {0} to list'.format(k))
            keys.add(k)

        logging.debug('Keys: {0}'.format(keys))
        return keys

    def get_keys(self, keys):
        """
        Get Redis keys detail
        """

        keys_detailed = []

        for k in keys:
            # Get key name, value and ttl
            key = {'key': k, 'value': self._redis.get(k), 'ttl': self._redis.ttl(k)}
            logging.debug('Key: {}, Value: {}, TTL: {}'.format(key['key'], key['value'], key['ttl']))
            keys_detailed.append(key)

        logging.debug('Keys: {0}'.format(keys_detailed))
        return keys_detailed

    def set_keys(self, keys):
        """
        Insert Redis keys from list
        """

        # Use pipeline for performance (https://github.com/andymccurdy/redis-py/blob/master/README.rst#pipelines)
        pipe = self._redis.pipeline()

        for k in keys:
            # Get key name, value and ttl
            name, value, ttl = k.values()

            # Add key to pipeline
            logging.debug('Add to pipeline: key: {}, value: {}'.format(name, value))
            pipe.set(name, value)

            # Add expire to pipeline
            if ttl > 0:
                logging.debug('Add to pipeline: key: {}, ttl: {}'.format(name, ttl))
                pipe.expire(name, ttl)

        # Execute pipeline
        if pipe.__len__() > 0:
            logging.info('Execute pipeline with {0} tasks'.format(pipe.__len__()))
            pipe.execute()
        else:
            logging.info('Pipeline empty, nothing to execute')
