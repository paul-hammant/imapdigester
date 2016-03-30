import os
import pickle

class MetaStore(object):

    def __init__(self, path_prefix):
        self.prefix = ".store/" + path_prefix

    def write_to_file(self, file_name, text):
        if not os.path.exists(self.prefix):
            os.makedirs(self.prefix)
        file = open(self.prefix + "/" + file_name + ".html", 'w+')
        file.write(text)
        file.close()

    def store_as_binary(self, name, to_store):
        if not os.path.exists(self.prefix):
            os.makedirs(self.prefix)
        file_io = open(self.prefix + "/" + name + ".p", "wb")
        pickle.dump(to_store, file_io)
        file_io.close()

    def get_from_binary(self, name):
        p_ = self.prefix + "/" + name + ".p"

        if os.path.isfile(p_):
            file_io = open(p_, "rb")
            b = pickle.load(file_io)
            file_io.close()
            return b
        return None
