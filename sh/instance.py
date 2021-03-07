import logging
import sqlite3
from argparse import ArgumentParser, Namespace

import sqlalchemy.engine
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

logging.basicConfig(level=logging.INFO)


def instance_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    instance = logging.getLogger(name)
    instance.setLevel(level)
    return instance


def instance_config(path, env) -> dict:
    with open(path, 'r') as cfg:
        return yaml.safe_load(cfg)[env]


def instance_db_connection(path) -> sqlalchemy.engine.Engine:
    return create_engine(
        'sqlite:///' + path, connect_args={'detect_types': sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES},
        native_datetime=True
    )


def instance_db_session(connection: sqlalchemy.engine.Engine) -> Session:
    return sessionmaker(bind=connection)()


def args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('--environment', metavar='environment', type=str, choices=['development', 'production'])
    parser.add_argument('--config', metavar='PATH', type=str)
    return parser.parse_args()
