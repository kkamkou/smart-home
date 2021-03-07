from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .sensor_history import SensorHistory
