import pymongo
import re
import requests
import config

import threading

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


class Crawler(object):
    def __init__(self):
        self.baike_mongo = get_mongo("baike_data_rough")
        self.baike_mongo.create_index("url",unique=True)
        self.save_to_mongo(self.baike_mongo,{
            "url":"唐寅/22587",
            "name":"唐寅",
            "tag":0,
            "from":""
        })
        self.url_pattern = re.compile('href="/item/([\s\S]+?)"([\s\S]*?)>([\s\S]+?)</a>')
        self.base_url = "https://baike.baidu.com/item/"
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
        zifuchuan = zifuchuan.replace("&rdquo;", "")
        zifuchuan = zifuchuan.replace("&ldquo;", "")

        return zifuchuan

    def parse(self, id_block):
        try:
            proxy = get_proxy()
            url = self.base_url + id_block["url"]
            page = requests.get(url, timeout=3, headers=self.headers, proxies=proxy)
            page.encoding="UTF-8"
            urls = self.url_pattern.findall(page.text)
            if len(urls) > 0:
                for url_block in urls:
                    self.save_to_mongo(self.baike_mongo, {
                        "url": url_block[0],
                        "name": re.sub("<([\s\S]+?)>", "",
                                       url_block[2].split("：", 1)[0] if "：" in url_block[2] else url_block[2]),
                        "tag": 0,
                        "from":url,
                    })

            self.baike_mongo.update_one({"_id":id_block["_id"]},{"$set":{"tag":1}})
        except Exception as e:
            print(e)
            self.baike_mongo.update_one({"_id": id_block["_id"]}, {"$inc": {"tag": -1}})
            sem.release()
            return
        sem.release()

    def get_data(self):
        while True:
            self.baike_mongo.find({"tag":{"$lt":-6}},{"$set":{"tag":1}})
            ids = self.baike_mongo.find({"tag": {"$ne":1}}).batch_size(2100)
            ids_count = self.baike_mongo.count_documents({"tag": {"$ne":1}})
            number = 0
            if ids_count < 1:
                break
            tsk = []
            for id in ids:
                number += 1
                print("%s_%s" % (ids_count, number))
                if number > 2000:
                    break
                sem.acquire()
                t = threading.Thread(target=self.parse, args=(id,))
                t.start()
                tsk.append(t)
            for task in tsk:
                task.join()
    def clean_data(self):
        clean_mongo = get_mongo("baike_data_clean")
        clean_mongo.create_index("name", unique=True)
        rough_data_list = self.baike_mongo.find()
        number = 0
        for rough_data in rough_data_list:
            number += 1
            print(number)

            del rough_data["_id"]
            if "共" in rough_data["name"] and "个义项" in rough_data["name"]:
                continue
            rough_data["tag"] = 0
            self.save_to_mongo(clean_mongo,rough_data)


temp = Crawler()
# temp.get_data()
# temp.clean_data()