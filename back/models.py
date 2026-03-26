from sqlalchemy import BigInteger, Boolean, Column, Double, ForeignKey, SmallInteger, Text, TIMESTAMP, func
from sqlalchemy.orm import relationship
from database import Base


class Driver(Base):
    __tablename__ = "driver"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    email = Column(Text, unique=True, nullable=False)
    name = Column(Text, nullable=False)
    password = Column(Text, nullable=False)
    phone = Column(Text, nullable=False)

    cars = relationship("Car", back_populates="driver_rel")
    drive_requests = relationship("DriveRequest", back_populates="driver_rel")
    shop_requests = relationship("ShopRequest", back_populates="driver_rel")
    other_requests = relationship("OtherRequest", back_populates="driver_rel")
    reviews = relationship("Review", back_populates="driver_rel")


class Disabled(Base):
    __tablename__ = "disabled"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    email = Column(Text, unique=True, nullable=False)
    name = Column(Text, nullable=False)
    password = Column(Text, nullable=False)
    disability = Column(Text, nullable=False)
    phone = Column(Text, nullable=False)

    drive_requests = relationship("DriveRequest", back_populates="disabled_rel")
    shop_requests = relationship("ShopRequest", back_populates="disabled_rel")
    other_requests = relationship("OtherRequest", back_populates="disabled_rel")
    reviews = relationship("Review", back_populates="author_rel")


class Car(Base):
    __tablename__ = "car"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    model = Column(Text, nullable=False)
    color = Column(Text, nullable=False)
    plate = Column(Text, nullable=False)
    driver = Column(BigInteger, ForeignKey("driver.id"), nullable=False)

    driver_rel = relationship("Driver", back_populates="cars")


class DriveRequest(Base):
    __tablename__ = "drive_requests"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    description = Column(Text, nullable=False)
    start_address = Column(Text, nullable=False)
    start_lat = Column(Double, nullable=False)
    start_lon = Column(Double, nullable=False)
    dest_address = Column(Text, nullable=False)
    dest_lat = Column(Double, nullable=False)
    dest_lon = Column(Double, nullable=False)
    is_completed = Column(Boolean, nullable=False)
    is_accepted = Column(Boolean, nullable=True)
    driver = Column(BigInteger, ForeignKey("driver.id"), nullable=True)   # nullable: no driver assigned yet
    disabled = Column(BigInteger, ForeignKey("disabled.id"), nullable=False)

    driver_rel = relationship("Driver", back_populates="drive_requests")
    disabled_rel = relationship("Disabled", back_populates="drive_requests")


class ShopRequest(Base):
    __tablename__ = "shop_requests"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    description = Column(Text, nullable=False)
    start_address = Column(Text, nullable=False)
    start_lat = Column(Double, nullable=False)
    start_lon = Column(Double, nullable=False)
    dest_address = Column(Text, nullable=False)
    dest_lat = Column(Double, nullable=False)
    dest_lon = Column(Double, nullable=False)
    is_completed = Column(Boolean, nullable=False)
    driver = Column(BigInteger, ForeignKey("driver.id"), nullable=True)   # nullable: no driver assigned yet
    disabled = Column(BigInteger, ForeignKey("disabled.id"), nullable=False)

    driver_rel = relationship("Driver", back_populates="shop_requests")
    disabled_rel = relationship("Disabled", back_populates="shop_requests")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    rating = Column(SmallInteger, nullable=False)
    comment = Column(Text, nullable=True)
    driver = Column(BigInteger, ForeignKey("driver.id"), nullable=False)
    author = Column(BigInteger, ForeignKey("disabled.id"), nullable=False)

    driver_rel = relationship("Driver", back_populates="reviews")
    author_rel = relationship("Disabled", back_populates="reviews")

class OtherRequest(Base):
    __tablename__ = "other_requests"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    description = Column(Text, nullable=False)

    dest_address = Column(Text, nullable=False)
    dest_lat = Column(Double, nullable=False)
    dest_lon = Column(Double, nullable=False)

    is_completed = Column(Boolean, nullable=False)
    is_accepted = Column(Boolean, nullable=True)

    driver = Column(BigInteger, ForeignKey("driver.id"), nullable=True)
    disabled = Column(BigInteger, ForeignKey("disabled.id"), nullable=False)

    driver_rel = relationship("Driver", back_populates="other_requests")
    disabled_rel = relationship("Disabled", back_populates="other_requests")