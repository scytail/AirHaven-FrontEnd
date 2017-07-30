from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('sqlite:///usertable.db', echo=True)
Base = declarative_base()


########################################################################
class User(Base):
    """"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password_hash = Column(String)

    # ----------------------------------------------------------------------
    def __init__(self, username, pass_hash):
        """"""
        self.username = username
        self.password_hash = pass_hash


# create tables
Base.metadata.create_all(engine)
