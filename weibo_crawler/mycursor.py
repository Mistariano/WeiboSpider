import MySQLdb
from MySQLdb.cursors import DictCursor
from threading import Lock
from scrapy.item import DictItem



class BatchInsertCollector():
    def __init__(self, cur, table_name, header=None, threshold=1000000):
        if not isinstance(cur, MyCursor):
            raise TypeError
        self.cur = cur
        self.table_name = table_name
        print 'lyc here'
        print table_name
        if header is None:
            print 'this way'
            self.header = cur.get_header(table_name)
        else:
            print 'that way'
            self.header = header
        print 'I have a header'
        self.sql_header = ''
        self.cur_len = 0
        self.reset_header()
        self.threshold = threshold
        self.values = []
        self.stat_total = 0
        self.mutex = Lock()
        print 'initial finish'

    def __del__(self):
        self.flush()
        self.cur.con.commit()

    def reset_header(self):
        self.sql_header = 'insert into %s (%s) values ' % (self.table_name, ','.join(self.header))
        self.cur_len = len(self.sql_header)

    def flush(self):
        if len(self.values) == 0:
            return
        self.cur.cur.execute(self.sql_header + ','.join(self.values))
        self.cur_len = len(self.sql_header)
        self.cur.con.commit()
        print 'flush called: %d records, total %d records' % (len(self.values), self.stat_total)
        self.values = []

    def append(self, data):
        assert isinstance(data, DictItem)
        self.mutex.acquire()

        def find(val):
            if val not in data.fields:
                return u"''"
            else:
                return u"'%s'" % unicode(data[val])

        cvalues = u','.join(map(find, self.header))
        val1 = u"(%s)" % cvalues
        # print self.cur_len
        if self.cur_len + len(val1) > self.threshold:
            self.flush()
        self.values.append(val1)
        self.cur_len += len(val1) + 1
        self.stat_total += 1
        self.mutex.release()


class MyCursor():
    def __init__(self):
        print 'good here'
        self.con = MySQLdb.Connect(host='127.0.0.1', user='root', db='sinaweibo',port='3306',
                                   cursorclass=DictCursor)
        self.cur = self.con.cursor()

    def __del__(self):
        print 'here?'
        self.cur.close()
        self.con.close()

    def batch_insert(self, table_name, header, data):
        if not isinstance(header, list):
            raise TypeError('mapper is not a dictionary')
        sql = 'insert into %s (%s) values '
        cnames = ','.join(header)
        sql1 = sql % (table_name, cnames)
        for i in data:
            def find(val):
                if val not in i:
                    return "''"
                else:
                    return "'" + str(i[val]) + "'"

            cvalues = ','.join(map(find, header))
            sql1 += "(%s)," % cvalues
        self.cur.execute(sql1[:-1])
        self.con.commit()

    def execute(self, sql, threshold=50000):
        if not isinstance(self.cur, DictCursor):
            print 'Error is here!!!,L101'
            raise Exception()
        self.cur.execute(sql)
        n = 0
        while n < self.cur.rowcount:
            delta = min(threshold, self.cur.rowcount - n)
            for i in self.cur.fetchmany(delta):
                yield i
            n += delta

    @staticmethod
    def get_header(table_name):
        m = MyCursor()
        m.cur.execute('DESC ' + table_name)
        return map(lambda x: x['Field'], m.cur.fetchall())
    # def get_header(table_name):
    #     m = MyCursor()
    #     print 'alive'
    #     m.cur.execute('SELECT * FROM ' + table_name + ' LIMIT 1')
    #     print m.cur.fetchone()
    #     return m.cur.fetchone().keys()

    @staticmethod
    def read(table_name, order=None, threshold=50000):
        m = MyCursor()
        cur = m.cur
        cur.execute('SELECT count(*) AS c FROM ' + table_name)
        cnt = m.cur.fetchone()['c']
        n = 0
        sql = 'SELECT * FROM ' + table_name
        if order is not None:
            sql += ' order by ' + order
        n = 0
        while n < cnt:
            delta = min(threshold, cnt - n)
            cur.execute(sql + ' limit %d, %d' % (n, delta))
            for i in cur.fetchall():
                yield i
            n += delta

    def insert(self, table_name, mapper):
        if not isinstance(mapper, DictItem):
            raise TypeError('mapper is not a dictionary')
        sql = u'insert into %s (%s) values(%s)'
        cnames = u','.join(mapper.fields.keys())
        cvalues = u','.join(map(lambda x: u"'" + unicode(mapper[x]) + u"'", mapper.fields.keys()))
        print 'commit here'
        self.cur.execute(sql % (table_name, cnames, cvalues))
        self.con.commit()

    def update(self, table_name, mapper, where=''):
        if not isinstance(mapper, dict):
            raise TypeError('mapper is not a dictionary')
        if not isinstance(where, str):
            raise TypeError('where is not a string')
        if not isinstance(table_name, str):
            raise TypeError('table_name is not a string')
        values = ''
        cur = self.cur
        for i in mapper:
            values += '%s = %s,' % (i, str(mapper[i]))
        values = values[:-1]
        sql = 'update %s set %s' % (table_name, values)
        if where != '':
            sql += ' where ' + where
        cur.execute(sql)
        self.con.commit()

    def find(self, table_name, where=''):
        sql = 'select count(*) as result from %s where %s'
        self.cur.execute(sql % (table_name, where))
        if self.cur.fetchone()['result'] > 0:
            return True
        return False


def __test():
    m = MyCursor()
    m.insert('test_table', {'name': 'wuyongji', 'times': 3})
    m.insert('test_table', {'name': 'lemon_cn', 'times': 87})
    m.insert('test_table', {'name': 'sdf', 'times': 323})


if __name__ == '__main__':
    __test()