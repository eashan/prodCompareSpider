from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

engine = create_engine("mysql://root:abc123@localhost/prodcompare?charset=utf8")

Base = declarative_base()



# association_table= Table('productStore',Base.metadata,
#                 Column("product_id",String(200),ForeignKey("products.id")),
#                 Column("store_url",String(200),ForeignKey("store.id"))
#                 )
class Product(Base):
    __tablename__ = "products"

    id = Column(String(1000), primary_key = True)
    product_name = Column(String(2000))
    product_category = Column(String(2000))
    product_url = Column(String(2000))
    product_specs = Column(String(2000))
    stores = relationship("ProductStore", back_populates="product")
    def __repr__(self):
        return "<Product(Id='%s', productName='%s', productCategory='%s')>" % (
                             self.id, self.product_name, self.product_category)

class Store(Base):
    __tablename__ = "store"

    id = Column(String(1000), primary_key = True)
    store_product_id = Column(String(2000),nullable= True)
    store_price = Column(Integer)
    product_shipping = Column(String(2000))
    product_delivery = Column(String(2000))

    product = relationship("ProductStore", back_populates="store")
    def __repr__(self):
        return "<Store(StoreUrl='%s', StorePrice='%s')>" % (
                             self.id, self.store_price)

class ProductStore(Base):
    __tablename__ = "productstore"
    product_id = Column(String(1000),ForeignKey("products.id"),primary_key=True)
    store_id = Column(String(1000), ForeignKey("store.id"),primary_key = True)
    store = relationship("Store", back_populates="product")
    product = relationship("Product", back_populates="stores")

Base.metadata.create_all(engine)
