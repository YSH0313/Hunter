# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2023-02-24 18:17:44
# @Version: 1.0.0
# @Description: '数据库及消息队列连接'

class KafkaDb:
    def __init__(self, custom_settings=None, **kwargs):
        super().__init__(custom_settings=custom_settings, **kwargs)
        if custom_settings:
            for varName, value in custom_settings.items():
                s = globals().get(varName)
                if s:
                    globals()[varName] = value

        if kafka_connection:
            self.producer = KafkaProducer(bootstrap_servers=kafka_servers['server'], max_request_size=3145728,
                                          api_version=(0, 10, 2))
        self.pwd = os.getcwd()
        self.spider_path = os.path.join(self.pwd, f'{self.name}.py')

    def key_judge(self, item):
        key_list = ['title', 'url', 'source', 'html']
        if isinstance(item, BiddingItem):
            item = item.dict()
        for k in key_list:
            sgin = item.__contains__(k)
            while not sgin:
                return False
        return True

    def value_judge(self, item):
        key_list = ['title', 'url', 'source', 'html']
        if isinstance(item, BiddingItem):
            item = item.dict()
        for k in key_list:
            sgin = item.get(k, 0)
            while not sgin:
                return k
        return True

    def kafka_producer(self, item):
        key_judge = False
        value_judge = False
        if self.isSubClassOf(item, SingleItem):
            item = item.dict()
            if 'file_url' in item.keys():
                del item['file_url']
        if isinstance(item, BiddingItem) or isinstance(item, dict):
            key_judge = self.key_judge(item)
            value_judge = self.value_judge(item)
        item['pub_time'] = self.date_refix(item.get('pub_time')) if item.get('pub_time') else None
        if (key_judge == True and value_judge == True) or (
                item.get('project_name') and self.spider_sign):
            if self.pages:
                item['monitor'] = True
            if self.online and not self.monitor:
                topic = kafka_servers['topic'] if key_judge and value_judge else 'proposed_tasks_mid'
                self.producer.send(topic, json.dumps(item).encode('utf-8'))
            self.prints(item, is_replace=False, db='kafka', sgin='data_test' if not self.online else '')
            # self.add_url_sha1(item['url']) if not item.get('show_url') else (self.add_url_sha1(item['url']), self.add_url_sha1(item.get('show_url'), sgin='show_'))
            self.right_count += 1
        else:
            debug_info = value_judge
            if (not key_judge and not value_judge) or self.spider_sign:
                debug_info = 'project_name'
            self.miss_filed = debug_info
            self.logger.debug(
                f'\033[5;31;1m{debug_info} \033[5;33;1mfield does not exist, Data validation failed, please check！\033[0m {item}')
            self.error_count += 1
        self.catch_count += 1


class EsDb:
    def __init__(self, custom_settings=None, **kwargs):
        super().__init__(custom_settings=custom_settings, **kwargs)
        if custom_settings:
            for varName, value in custom_settings.items():
                s = globals().get(varName)
                if s:
                    globals()[varName] = value
        if IS_ES:
            self.es = Elasticsearch(hosts=ES_CONFIG['host'], port=ES_CONFIG['port'],
                                    http_auth=(ES_CONFIG['user'], ES_CONFIG['password']), request_timeout=60)


class MongoDBManager:
    def __init__(self, custom_settings=None, **kwargs):
        super().__init__(custom_settings=custom_settings, **kwargs)
        if custom_settings:
            for varName, value in custom_settings.items():
                s = globals().get(varName)
                if s:
                    globals()[varName] = value
        MONGODB_HOST = MONGO_CONFIG['MONGODB_HOST']
        MONGODB_PORT = MONGO_CONFIG['MONGODB_PORT']
        MONGODB_BASE = MONGO_CONFIG['MONGODB_BASE']
        if MONGO_client:
            try:
                self.mongo_client = pymongo.MongoClient(f"mongodb://{MONGODB_HOST}:{MONGODB_PORT}/")
                self.mong_db = self.mongo_client[MONGODB_BASE]
            except (ConnectionFailure, AutoReconnect) as e:
                raise Exception(f"Failed to connect to MongoDB: {e}")

    def insert_data(self, collection_name, data):
        try:
            collection = self.mong_db[collection_name]
            result = collection.insert_one(data)
            return result.inserted_id
        except pymongo.errors.DuplicateKeyError as e:
            raise Exception(f"Failed to insert data: {e}")

    def find_data(self, collection_name, query):
        try:
            collection = self.mong_db[collection_name]
            result = collection.find(query)
            return result
        except Exception as e:
            raise Exception(f"Failed to find data: {e}")

    def find_paginated_data(self, collection_name, page_number, page_size):
        try:
            collection = self.mong_db[collection_name]
            skip_documents = (page_number - 1) * page_size
            result = collection.find().skip(skip_documents).limit(page_size)
            return result
        except Exception as e:
            raise Exception(f"Failed to find data: {e}")

    def update_data(self, collection_name, query, update_data):
        try:
            collection = self.mong_db[collection_name]
            result = collection.update_many(query, {"$set": update_data})
            return result.modified_count
        except Exception as e:
            raise Exception(f"Failed to update data: {e}")

    def delete_data(self, collection_name, query):
        try:
            collection = self.mong_db[collection_name]
            result = collection.delete_many(query)
            return result.deleted_count
        except Exception as e:
            raise Exception(f"Failed to delete data: {e}")
