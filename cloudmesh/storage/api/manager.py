import cloudmesh.storage.provider.gdrive.Provider
import cloudmesh.storage.provider.box.Provider
import cloudmesh.mongo.CmDatabase


class Manager(object):

    def __init__(self):
        print("init {name}".format(name=self.__class__.__name__))
        db = cloudmesh.mongo.CmDatabase.CmDatabase()


    def _provider(self, service):
        provider = None
        if service == "gdrive":
            provider = cloudmesh.storage.provider.gdrive.Provider.Provider()
        elif service == "box":
            provider = cloudmesh.storage.provider.box.Provider.Provider()
        return provider

    def delete(self, service, filename):
        print("delete", service, filename)
        provider = self._provider(service)
        provider.delete(filename)

    def get(self, service, filename, destdir):
        print("get", service, filename, destdir)
        provider = self._provider(service)
        provider.get(filename, destdir)

    def put(self, service, filename, sourcedir, destdir=None):
        print("put", service, filename, sourcedir, destdir)
        provider = self._provider(service)
        provider.put(filename, sourcedir, destdir)

    def info(self, service, filename):
        print("info", service, filename)
        provider = self._provider(service)
        provider.info(filename)

    def search(self, service, filename):
        print("search", service, filename)
        provider = self._provider(service)
        provider.search(filename)

    def create_dir(self, service, dirname, destdir=None):
        print("createdir", service, dirname, destdir)
        provider = self._provider(service)
        provider.createdir(dirname, destdir)

    def list_dir(self, service, dirname=None):
        print("listdir", service, dirname)
        provider = self._provider(service)
        provider.listdir(dirname)

    def delete_dir(self, service, dirname):
        print("deletedir", service, dirname)
        provider = self._provider(service)
        provider.deletedir(dirname)

