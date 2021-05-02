import logging
from argparse import ArgumentParser, Namespace

import yaml
from influxdb_client import InfluxDBClient

logging.basicConfig(level=logging.INFO)


def instance_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    instance = logging.getLogger(name)
    instance.setLevel(level)
    return instance


def instance_config(path, env) -> dict:
    with open(path, 'r') as cfg:
        return yaml.safe_load(cfg)[env]


def instance_db(config) -> InfluxDBClient:
    return InfluxDBClient(**config)


def args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('--environment', metavar='environment', type=str, choices=['development', 'production'])
    parser.add_argument('--config', metavar='PATH', type=str)
    return parser.parse_args()
