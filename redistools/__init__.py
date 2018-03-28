"""
Redistools package
"""

import logging
import os
import time
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


def get_config():
    """
    Get configuration from environment variables
    """

    config = {'dry_run': os.getenv('DRY_RUN', "yes"),
              'interval': int(os.getenv('INTERVAL', '30')),
              'redis_endpoint': os.getenv('REDIS_ENDPOINT', 'localhost:6379'),
              'redis_namespace': os.getenv('REDIS_NAMESPACE', '*'),
              'redis_target_endpoint': os.getenv('REDIS_TARGET_ENDPOINT', 'none')}

    # Get configuration from environment variables

    # Logging configuration
    log_level = os.getenv('LOG_LEVEL', 'INFO')

    logging.basicConfig(
        format='%(name)s %(asctime)s %(levelname)s %(message)s',
        level=log_level
    )

    return config


def compare_keys(namespace, redis_instance, redis_target_instance):
    """
    Compare Redis keys between source and target Redis instances
    """

    # Get keys for both Redis
    source_keys = redis_instance.list_keys(namespace)
    target_keys = redis_target_instance.list_keys(namespace)

    # Get keys present only in source Redis
    new_keys = source_keys.difference(target_keys)

    if len(new_keys) > 0:
        logging.debug('New keys: {0}'.format(new_keys))
    else:
        logging.debug('No new keys found on {0}'.format(redis_instance.get_endpoint()))

    return new_keys


def sync():
    """
    Copy new keys from source Redis to target Redis
    """

    # Initialize configuration
    config = get_config()

    # Initialize redis instances
    redis_instance = RedisInstance(config['redis_endpoint'])
    redis_target_instance = RedisInstance(config['redis_target_endpoint'])

    # Enable watch mode to run the same command at regular interval
    watch_mode = True

    while watch_mode:
        new_keys = compare_keys(config['redis_namespace'], redis_instance, redis_target_instance)

        # Sleep if interval is set or exit watch mode
        if config['interval'] > 0:
            time.sleep(config['interval'])
        else:
            watch_mode = False

if __name__ == '__main__':
    sync()
