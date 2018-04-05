from setuptools import setup, find_packages

setup(
    name='redis-tools',
    version='0.1.0',
    description='simple python redis tools, mostly used for keys synchronization between 2 redis',
    author='Julien Mailleret',
    install_requires=[
        'redis',
    ],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'redis-sync = redistools.tools:sync',
            'redis-monitor = redistools.tools:monitor',
        ]
    }
)
