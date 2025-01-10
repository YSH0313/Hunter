# -*- coding: utf-8 -*-
# @Author: yuanshaohang
# @Date: 2025/1/3 16:12
# @Version: 1.0.0
# @Description: ''
import re
import aiomysql

from hunterx.utils.log import LogCaptor
from hunterx.utils.single_tool import deal_re
from hunterx.utils.reload_settings import SettingsManager


def lazy_init_decorator(func):
    def wrapper(*args, **kwargs):
        # 检查是否已初始化
        if not Mysqldb._initialized:  # 直接检查 MyClass 类的初始化状态
            Mysqldb._lazy_init()  # 执行延迟初始化
        return func(*args, **kwargs)
    return wrapper


class Mysqldb:
    condition_re = re.compile('(.*?)\\(')

    params_re = re.compile('\\((.*?)\\)')

    logger = None

    _initialized = False  # 类级别的初始化标志

    @classmethod
    def _lazy_init(self):
        self.logger = LogCaptor().get_logger()
        Mysqldb._initialized = True

    @classmethod
    def __getattribute__(cls, name):
        if not hasattr(cls, "_initialized") or not cls._initialized:
            cls._lazy_init(cls)  # 类级别的延迟初始化
        return super().__getattribute__(name)

    @staticmethod
    def get_config():
        settings = SettingsManager().get_settings()

        __Mysql = settings.Mysql

        __IS_INSERT = settings.IS_INSERT

        return __Mysql, __IS_INSERT

    @staticmethod
    async def create_pool():
        __Mysql = Mysqldb.get_config()[0]
        # 创建数据库连接池
        pool = await aiomysql.create_pool(
            host=__Mysql.MYSQL_HOST,
            port=__Mysql.PORT,
            user=__Mysql.MYSQL_USER,
            password=__Mysql.MYSQL_PASSWORD,
            db=__Mysql.MYSQL_DBNAME,
            minsize=2,  # 最小连接数
            maxsize=10,  # 最大连接数
            autocommit=True,  # 自动提交
            charset='utf8mb4',
            use_unicode=True,
            cursorclass=aiomysql.DictCursor
        )
        return pool

    @staticmethod
    @lazy_init_decorator
    async def execute(query, parameters=None, many=False):
        __IS_INSERT = Mysqldb.get_config()[1]
        if __IS_INSERT:
            pool = await Mysqldb.create_pool()
            try:
                async with pool.acquire() as conn:  # 从连接池中获取连接
                    async with conn.cursor() as cursor:
                        if many:
                            await cursor.executemany(query, parameters)
                        else:
                            if 'SELECT' in query:
                                await cursor.execute(query)
                                results = await cursor.fetchall()
                                return results
                            else:
                                await cursor.execute(query, parameters)
            except Exception as e:
                Mysqldb.logger.error(e, exc_info=True)
            finally:
                pool.close()
                await pool.wait_closed()
        else:
            Mysqldb.logger.warning(
                'The current configuration does not allow the use of MySQL connection. Please check the parameters of IS_INSERT'
            )

    @staticmethod
    @lazy_init_decorator
    async def insert(table, data, if_update=False, is_info=True):
        columns = ', '.join([f"`{i}`" for i in data.keys()])
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT IGNORE INTO `{table}` ({columns}) VALUES ({placeholders});"
        sql = query % tuple([f"'{i}'" if i else i for i in data.values()])
        if if_update:
            update = ', '.join([f"`{key}` = %s" for key in data.keys()])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update};"
            sql = query % tuple([f"'{i}'" if i else i for i in data.values()] * 2)
        if is_info:
            Mysqldb.logger.info(f'{sql};')
            Mysqldb.logger.info('===========================================================')
        return await Mysqldb.execute(query, tuple(data.values()))

    @staticmethod
    @lazy_init_decorator
    async def update(table, set_data, where=None):
        set_pairs = [f"`{column}`=%s" for column in set_data.keys()]
        query = f"UPDATE `{table}` SET {', '.join(set_pairs)}"
        parameters = tuple(set_data.values())
        if where:
            query += f" WHERE {where}"
        sql = query % tuple([f"'{i}'" if i else i for i in parameters])
        Mysqldb.logger.info(f'{sql};')
        Mysqldb.logger.info('===========================================================')
        return await Mysqldb.execute(query, parameters)

    @staticmethod
    @lazy_init_decorator
    async def delete(table, where=None):
        query = f"DELETE FROM `{table}`"
        if where:
            query += f" WHERE {where}"
        Mysqldb.logger.info(f'{query};')
        Mysqldb.logger.info('===========================================================')
        return await Mysqldb.execute(query)

    @staticmethod
    async def trucate(table):
        sql = f"""TRUNCATE `{table}`;"""
        return await Mysqldb.execute(sql)

    @staticmethod
    async def get_condition(columns):
        condition_map = {'count': 'count', 'max': 'max', 'min': 'min', 'sum': 'sum', 'avg': 'avg',
                         'distinct': 'distinct'}
        condition = ''
        if isinstance(columns, list):
            columns = ', '.join([f"`{i}`" for i in columns])
        elif isinstance(columns, str) and columns != '*':
            condition = deal_re(Mysqldb.condition_re.search(columns))
            condition_exis = True if [True for i in condition_map.keys() if i.upper() in columns.upper()] else False
            if not condition_exis:
                columns = ', '.join(f'`{i.strip(" ")}`' for i in columns.split(','))
        return condition_map, condition, columns

    @staticmethod
    @lazy_init_decorator
    async def select(table, columns='*', where=None, order_by=None, limit=None, offset=None):
        condition_map, condition, columns = await Mysqldb.get_condition(columns)
        query = f"SELECT {columns} FROM `{table}`"
        if where:
            query += f" WHERE {where}"
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"
        if offset:
            query += f" OFFSET {offset}"
        Mysqldb.logger.info(f'查询字段：{query};')
        Mysqldb.logger.info('===========================================================')
        results = await Mysqldb.execute(query)
        return results

    @staticmethod
    def judge_er(str_data):
        if str_data.isupper():
            return True
        else:
            return False
