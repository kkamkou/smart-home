from sqlalchemy import String, Column, Integer, UniqueConstraint, DateTime, FLOAT

from lib.models import Base


class SensorHistory(Base):
    __tablename__ = "sensor_history"
    __table_args__ = (UniqueConstraint('sensor', 'timestamp', name='_uc_sensor_timestamp'),)

    id = Column(Integer, primary_key=True, autoincrement=True)

    sensor = Column(String(26), nullable=False)

    timestamp = Column(DateTime, nullable=False)

    type = Column(String(30), nullable=False)

    value = Column(FLOAT(precision=2), nullable=False)
