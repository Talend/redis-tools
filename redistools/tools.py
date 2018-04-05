"""
Tools module
"""

import logging
import os
import time

from .redis_instances import RedisInstance


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

    while True:
        new_keys = compare_keys(config['redis_namespace'], redis_instance, redis_target_instance)

        # Do nothing in dry run mode
        if config['dry_run'] != "yes":
            # Start copy keys only if there in new keys to copy
            if len(new_keys) > 0:
                logging.info('New key to add on {0}'.format(redis_target_instance.get_endpoint()))
                keys_detailed = redis_instance.get_keys(new_keys)
                redis_target_instance.set_keys(keys_detailed)
            else:
                logging.info('Every keys are already existing in {}'.format(redis_target_instance.get_endpoint()))

        # Sleep if interval is set or exit
        if config['interval'] > 0:
            time.sleep(config['interval'])
        else:
            break


def monitor():
    """
    Monitor Redis instances
    :return:
    """

    # Initialize configuration
    config = get_config()

    # Initialize source Redis Instance
    redis_instance = RedisInstance(config['redis_endpoint'])

    while True:
        # List keys
        source_keys = redis_instance.list_keys(config['redis_namespace'])
        logging.info('Keys for Redis Source {0}: {1}'.format(redis_instance.get_endpoint(), source_keys))

        # Initialize target Redis
        if config['redis_target_endpoint'] != 'none':
            redis_target_instance = RedisInstance(config['redis_target_endpoint'])
            target_keys = redis_target_instance.list_keys(config['redis_namespace'])
            logging.info('Keys for Redis Target {0}: {1}'.format(redis_target_instance.get_endpoint(), target_keys))

        # Sleep if interval is set or exit
        if config['interval'] > 0:
            time.sleep(config['interval'])
        else:
            break
