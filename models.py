from sqlalchemy import Column, String, Date, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Certificate(Base):
    __tablename__ = 'certificates'

    id = Column(Integer, primary_key=True, index=True)
    serial_no = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    course_name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    certificate_no = Column(String, unique=True, nullable=False)
    date_of_certificate = Column(Date, nullable=False)
    photo = Column(String, nullable=True)
    access_by = Column(String, nullable=False)
    website = Column(String, nullable=False)

# Example DATABASE_URL, you should update it to your setup
DATABASE_URL = "sqlite:///certificates.db"

# Initiating the engine
engine = create_engine(DATABASE_URL)
