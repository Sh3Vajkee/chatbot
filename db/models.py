from sqlalchemy import Column, Integer, BigInteger, String, Text, Boolean

from db.base import Base


class ChatgroupUser(Base):
    __tablename__ = 'chatgroupuser'

    user_id = Column(BigInteger, primary_key=True)
    user_name = Column(String(50))
    checked = Column(Boolean, default=False)
    msg_id = Column(BigInteger)
    warn_count = Column(Integer, default=0)
    ban_count = Column(Integer, default=0)
    join_date = Column(BigInteger)
    leave_date = Column(BigInteger)


class CountMembers(Base):
    __tablename__ = 'countmembers'

    id = Column(String(50), primary_key=True)
    day = Column(Integer)
    month = Column(Integer)
    year = Column(Integer)
    joined = Column(Integer, default=0)
    left = Column(Integer, default=0)
