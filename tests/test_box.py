import cloudmesh.storage.provider.box.Provider
from pprint import pprint


class TestBox:

    def setup(self):
        self.provider = cloudmesh.storage.provider.box.Provider.Provider()

    def test_01_root(self):
        root = self.provider.client.folder('0').get()
        pprint(root.__dict__)

        assert root.__dict__ is not None

    def test_02_items(self):
        items = self.provider.client.folder('0').get_items()
        files = []
        for item in items:
            files.append(item)
            pprint(item.__dict__)

        assert len(files) > 0










