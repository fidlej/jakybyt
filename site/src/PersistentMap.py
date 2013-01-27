
import os
import cPickle

import disk

class PersistentMap:
    def __init__(self, path):
        self.path = path
        if os.path.exists(self.path):
            fp = disk.fetchDataFile(self.path)
            self.map = cPickle.load(fp)
            fp.close()
        else:
            self.map = {}
        self.lazySave = False

    def setLazySave(self, lazySave):
        self.lazySave = lazySave

    def __contains__(self, key):
        return key in self.map

    def get(self, key, default=None):
        return self.map.get(key, default)

    def __getitem__(self, key):
        return self.map[key]

    def __setitem__(self, key, value):
        self.map[key] = value
        if not self.lazySave:
            self.save()

    def save(self):
        data = cPickle.dumps(self.map, protocol=2)
        disk.storeAtomicData(self.path, data)

