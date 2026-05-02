from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(128), primary_key=True)  # device_id
    nickname = Column(String(32), default="农场主")
    created_at = Column(DateTime, default=datetime.utcnow)
    farm = relationship("Farm", back_populates="user", uselist=False)


class Farm(Base):
    __tablename__ = "farms"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(128), ForeignKey("users.id"))
    name = Column(String(32), default="我的农场")
    total_plots = Column(Integer, default=6)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="farm")
    plots = relationship("FarmPlot", back_populates="farm", order_by="FarmPlot.slot_index")


class FarmPlot(Base):
    __tablename__ = "farm_plots"

    id = Column(String(36), primary_key=True)
    farm_id = Column(String(36), ForeignKey("farms.id"))
    slot_index = Column(Integer, nullable=False)
    stock_code = Column(String(10), nullable=True)
    stock_name = Column(String(20), nullable=True)
    buy_price = Column(Float, nullable=True)    # 种下时的价格，核心基准
    planted_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="empty")  # empty/seed/sprout/seedling/sapling/tree/full_tree
    is_harvestable = Column(Boolean, default=False)
    farm = relationship("Farm", back_populates="plots")


class HarvestRecord(Base):
    __tablename__ = "harvest_records"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(128), ForeignKey("users.id"))
    stock_code = Column(String(10))
    stock_name = Column(String(20))
    buy_price = Column(Float)
    harvest_price = Column(Float)
    total_return_pct = Column(Float)
    planted_at = Column(DateTime)
    harvested_at = Column(DateTime, default=datetime.utcnow)
