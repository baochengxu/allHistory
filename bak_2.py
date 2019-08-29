import pymongo
import re
import requests
import config

import threading

sem = threading.BoundedSemaphore(10)


def get_mongo(collection_name):
    client = pymongo.MongoClient(config.MONGO_URL)
    mongodb = client['allHistory']
    collection = mongodb[collection_name]
    return collection


import redis

proxy_redis = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)


def get_proxy():
    while True:
        proxy = proxy_redis.get(proxy_redis.randomkey())
        ip = str(proxy)
        if "{" in ip:
            continue
        elif "}" in ip:
            continue
        else:
            break
    ip = ip[2:]
    ip = ip.replace(r"\r", "")
    ip = ip.replace(r"\\", "")
    ip = ip.replace("'", "")
    return {"http": ip, "https": ip}


class Crawler(object):
    def __init__(self):
        self.data_mongo = get_mongo("data_blocks")
        self.data_mongo.create_index("id", unique=True)
        self.id_mongo = get_mongo("ids")
        self.id_mongo.create_index("id", unique=True)
        self.save_to_mongo(self.id_mongo, {"id": "582c01ae05c3fb6176030572", "tag": 0})
        self.base_url = "https://www.allhistory.com/api/item/relation/cn/"
        self.headers = {
            "ax": "7dfe836785eac61a6fe;d4fa8c8b559e6c2b0b95cf51ae26e82bbb562ea8;2bac21c99c;dbacbd0455c022fe7cb7989d34805e2506f6e7d6;1566293128760;2;6f8e936785eac61fc18;bdd035f8a3582e2cc09d7ff5309243278306e2a3e11882a67663c9ddcdac2aa2dd93045a271ff8fe",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
        }

    def save_to_mongo(self, mongo, data):
        try:
            mongo.insert_one(data)
        except Exception as e:
            pass

    def clear(self, zifuchuan):
        zifuchuan = re.sub("<([\s\S]+?)>", "", zifuchuan)
        zifuchuan = zifuchuan.replace("&rdquo;", "")
        zifuchuan = zifuchuan.replace("&ldquo;", "")

        return zifuchuan

    def parse(self, id_block):
        pass
    def get_data(self):
        while True:
            ids = self.id_mongo.find({"tag": 0})
            ids_count = self.id_mongo.count_documents({"tag": 0})
            number = 0
            if ids_count < 1:
                break
            for id in ids:
                number += 1
                print("%s_%s" % (ids_count, number))
                try:
                    # page = requests.get(self.base_url + id["id"], timeout=3, headers=self.headers,
                    # proxies=get_proxy()).json()
                    proxy = get_proxy()
                    url = self.base_url + id["id"]
                    page = requests.get(url, timeout=3, headers=self.headers, proxies=proxy)
                    page = page.json()
                    relations = page["data"]["relationList"]
                    for relation in relations:
                        self.save_to_mongo(self.id_mongo, {"id": relation["id"], "tag": 0})
                    self.save_to_mongo(self.data_mongo, page["data"])
                    self.id_mongo.update_one({"_id": id["_id"]}, {"$set": {"tag": 1}})
                except Exception as e:
                    print(e)
                    try:
                        print(page.text)
                    except Exception as e:
                        pass
                    continue


temp = Crawler()
temp.get_data()
