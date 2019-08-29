import pymongo
import re
import requests
import config
import json
import threading
import js
sem = threading.BoundedSemaphore(100)


def get_mongo(collection_name):
    client = pymongo.MongoClient(config.MONGO_URL)
    mongodb = client['allHistory_new']
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
"""
https://www.allhistory.com/api/search/getSuggestion
{"language":"cn","keyword":"桃花庵主","hasGeo":"false","hasTime":"false"}
"""

class Crawler(object):
    def __init__(self):
        self.baike_data_mongo = get_mongo("baike_data_clean")
        # self.baike_data_mongo.update_many({},{"$set":{"tag":0}})
        self.id_mongo = get_mongo("ids")
        self.id_mongo.create_index("id", unique=True)

        self.url = "https://www.allhistory.com/api/search/getSuggestion"
        self.headers = {
            "content-type": "application/json;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        }

    def save_to_mongo(self, mongo, data):
        try:
            mongo.insert_one(data)
        except Exception as e:
            pass


    def parse(self, data_block):
        try:
            proxy = get_proxy()
            headers = {
                "ax": js.get_ax(data_block["name"]),
                "content-type": "application/json;charset=UTF-8",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        }
            page = requests.post(self.url, data=json.dumps({"language":"cn","keyword":"%s" % data_block["name"],"hasGeo":"false","hasTime":"false"}), timeout=3, headers=headers, proxies=proxy)
            print(page.text)
            page = page.json()
            sugNodes = page["data"]["sugNodes"]
            for sugNode in sugNodes:
                self.save_to_mongo(self.id_mongo,{"id":sugNode["id"],"tag":0})
            self.baike_data_mongo.update_one({"_id":data_block["_id"]},{"$set":{"tag":1}})
        except Exception as e:
            print(e)
            self.baike_data_mongo.update_one({"_id": data_block["_id"]}, {"$inc": {"tag": -1}})
            sem.release()
            return
        sem.release()

    def get_data(self):
        while True:
            self.baike_data_mongo.update_many({"tag":{"$lt":-10}},{"$set":{"tag":1}})
            baike_datas = self.baike_data_mongo.find({"tag": {"$lt":1}})
            baike_datas_count = self.baike_data_mongo.count_documents({"tag": {"$lt":1}})
            number = 0
            if baike_datas_count < 1:
                break
            tsk = []
            for data_block in baike_datas:
                number += 1
                print("%s_%s" % (baike_datas_count, number))
                if number > 5000:
                    break
                sem.acquire()
                t = threading.Thread(target=self.parse, args=(data_block,))
                t.start()
                tsk.append(t)
                # break
            for task in tsk:
                task.join()
            # break


temp = Crawler()
temp.get_data()
