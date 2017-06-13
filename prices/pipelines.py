# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from models import *

Session = sessionmaker(bind=engine)

class PricesPipeline(object):

    # def open_spider(self, spider):
    #     # Open DB here
    #     Session = sessionmaker(bind=engine)
    #     self.session = Session()
    #     pass
    #
    # def close_spider(self, spider):
    #     # Close DB here
        # pass
    def __init__(self):
            Session = sessionmaker(bind=engine)
            self.session = Session()
        # self.file = open('items.jl', 'wb')


    def process_item(self, item, spider):
        self.session = Session()
        print('Product info of {} scrapped'.format(item['name']))
        specs = ""
        for i in item['specs']:
            specs+=item['specs'][i]
            specs+ "\n"
            if(self.session.query(Product).filter(Product.id==item['url']).count()):
                product = self.session.query(Product).filter(Product.id==item['url']).first()
                product.id = item['name']
                product.product_name = item['name']
                product.product_category = item['category']
                product.product_specs = specs
                product_url = item['url']
            else:
                product = Product(id=item['name'],product_name=item['name'],product_category= item['category'], product_specs=specs, product_url=item['url'])

        for i in item['stores']:
            storeData = item['stores'][i]

            if(self.session.query(Store).filter(Store.id==storeData['url']).count()):
                store = self.session.query(Store).filter(Store.id==storeData['url']).first()
                store.id = storeData['url']
                store.store_price = float(storeData['price'].replace(',',''))
                store.product_shipping = storeData['shipping']
                store.product_delivery = storeData['delivery']
            else:
                store = Store(id=storeData['url'],store_price=float(storeData['price'].replace(',','')),product_shipping=storeData['shipping'],product_delivery=storeData['delivery'])

            productStore = ProductStore()
            productStore.store = store
            productStore.product = product
            # product.stores.append(productStore)

            self.session.add(store)
            self.session.add(productStore)

        self.session.add(product)
        self.session.commit()

        # line = json.dumps(dict(item))+ "\n \n \n"
        # self.file.write(line)
        return item
