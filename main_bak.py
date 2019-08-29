import pymongo
import re
import requests
import config

import threading

sem = threading.BoundedSemaphore(1)


def get_mongo(collection_name):
    client = pymongo.MongoClient(config.MONGO_URL)
    mongodb = client['allHistory']
    collection = mongodb[collection_name]
    return collection


import redis

proxy_redis = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)


def get_proxy():
    proxy = proxy_redis.get(proxy_redis.randomkey())
    ip = str(proxy)
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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
        }

    def save_to_mongo(self, mongo, data):
        try:
            mongo.insert_one(data)
        except Exception as e:
            pass

    def clear(self, zifuchuan):
        zifuchuan = re.sub("<([\s\S]+?)>", "", zifuchuan)
        zifuchuan = zifuchuan.replace("&rdquo;","")
        zifuchuan = zifuchuan.replace("&ldquo;","")

        return zifuchuan

    def get_data(self):
        while True:
            ids = self.id_mongo.find({"tag": 0}, no_cursor_timeout = True)
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
                    page = requests.get(self.base_url + id["id"], timeout=3, headers=self.headers).json()
                    data_json = {
                        "id": page["data"]["id"],
                        "name": page["data"]["name"],
                        "summary": self.clear(page["data"]["summary"]),
                        "imageId": page["data"]["imageId"],
                        "imageUrl": page["data"]["imageUrl"],
                    }
                    if "typePaths" in page:
                        data_json["typePaths"] = page["typePaths"]
                    if "birth" in page:
                        data_json["birth"] = page["birth"]
                    if "death" in page:
                        data_json["death"] = page["death"]
                    data_json["relations"] = []
                    relations = page["data"]["relationList"]
                    for relation in relations:
                        data_json["relations"].append(
                            {
                                "id": relation["id"],
                                "name": relation["name"],
                                "direction": relation["relations"]["direction"],
                                "relation": relation["relations"]["relation"],
                                "relationDesc": self.clear(relation["relations"]["relationDesc"]),
                                "relationType": relation["relations"]["relationType"]
                            }
                        )
                        self.save_to_mongo(self.id_mongo, {"id": relation["id"], "tag": 0})
                    self.save_to_mongo(self.data_mongo, data_json)
                    self.id_mongo.update_one({"_id":id["_id"]},{"$set":{"tag":1}})
                except Exception as e:
                    print(e)
                    print(page)
                    continue



temp = Crawler()
temp.get_data()
