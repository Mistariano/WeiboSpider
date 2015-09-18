import json
import codecs


class WeiboPipeline(object):
    def __init__(self):
        self.file = codecs.open('items.json', 'wb', encoding='utf-8')

    def process_item(self, item, spider):
        print 'in line'
        line = json.dumps(dict(item)) + '\n'
        self.file.write(line.decode("unicode_escape"))
        print 'out line'
        return item
