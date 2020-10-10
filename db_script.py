import redis
import sqlite3
from abc import ABCMeta, abstractmethod


class AbstractDatabase(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def load_data(self):
        pass

    @abstractmethod
    def save_data(self, data: dict):
        pass


class SQLiteDatabase(AbstractDatabase):
    def __init__(self):
        AbstractDatabase.__init__(self)
        self.db = sqlite3.connect('db.sqlite3')
        self.cursor = self.db.cursor()
        self._init_tables()

    def _init_tables(self):
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS tables(name CHAR(200))")
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS articles(text CHAR(200), fk_table_number INT)")

    def _insert_article(self, table_number: int, text: str):
        self.cursor.execute(f"INSERT INTO articles(text, fk_table_number) VALUES('{text}', {table_number})")

    def _insert_table(self, table_name: str):
        self.cursor.execute(f"INSERT INTO tables(name) VALUES('{table_name}')")

    def _select_articles_from_table(self, table_number: int):
        return self.cursor.execute(f"SELECT text FROM articles WHERE fk_table_number={table_number}")

    def _select_tables(self):
        return self.cursor.execute(f"SELECT rowid, name FROM tables")

    def _clear_tables(self):
        self.cursor.execute(f"DELETE FROM tables WHERE rowid>0")
        self.cursor.execute(f"DELETE FROM articles WHERE rowid>0")

    def load_data(self) -> dict:
        Dict = dict()
        tables_cursor = self._select_tables()
        tables = []
        for x in tables_cursor:
            tables.append(x)
        del tables_cursor
        for table in tables:
            articles_cursor = self._select_articles_from_table(table[0])
            articles = []
            for x in articles_cursor:
                for y in x:
                    articles.append(y)
            Dict[table[1]] = articles
        return Dict

    def save_data(self, data: dict):
        self._clear_tables()
        counter = 1
        for table in data.keys():
            self._insert_table(table)
            for article in data[table]:
                self._insert_article(counter, article)
            counter += 1
        self.db.commit()


class RedisDatabase(AbstractDatabase):
    def __init__(self):
        AbstractDatabase.__init__(self)
        self.R = redis.Redis()

    def load_data(self) -> dict:
        keys = self.R.keys()
        for x in range(len(keys)):
            keys[x] = keys[x].decode('utf-8')
        Dict = dict()
        for x in keys:
            articles_list = list()
            while self.R.llen(x.encode('utf-8')):
                articles_list.append(self.R.lpop(x.encode('utf-8')).decode('utf-8'))
            Dict[x] = articles_list
        print(Dict)
        return Dict

    def save_data(self, data: dict) -> None:
        for x in self.R.keys():
            self.R.delete(x)
        for x in data.keys():
            for y in data[x]:
                self.R.rpush(x, y)


def DatabasesTest():
    r = RedisDatabase()
    d = r.load_data()
    d1 = {'ping': ['pong']}
    r.save_data(d1)

    for x in r.R.keys():
        print(x)
        for i in range(r.R.llen(x)):
            print(r.R.lindex(x, i))

    d1 = {'ping': ['pong']}
    s = SQLiteDatabase()
    d = s.load_data()
    print(d)
    s.save_data(d1)

if __name__ == '__main__':
    DatabasesTest()
