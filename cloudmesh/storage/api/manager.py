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

    def get(self, service, source, destination, recursive):
        print("get", service, source, destination, recursive)
        provider = self._provider(service)
        provider.get(source, destination, recursive)

    def put(self, service, source, destination, recursive):
        print("put", service, source, destination, recursive)
        provider = self._provider(service)
        provider.put(source, destination, recursive)

    def search(self, service, directory, filename, recursive):
        print("search", service, directory, filename, recursive)
        provider = self._provider(service)
        provider.search(directory, filename, recursive)

    def create_dir(self, service, dirname):
        print("createdir", service, dirname)
        provider = self._provider(service)
        provider.create_dir(dirname)

    def list(self, service, source=None, recursive=False):
        print("list", service, source, recursive)
        provider = self._provider(service)
        provider.list(source, recursive)

    def delete(self, service, source):
        print("deletedir", service, source)
        provider = self._provider(service)
        provider.delete(source)

