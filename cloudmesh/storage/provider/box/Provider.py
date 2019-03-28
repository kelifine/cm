from boxsdk import JWTAuth
from boxsdk import Client
from cloudmesh.management.configuration.config import Config
from cloumesh.management.configuration.name import Name
from cloudmesh.common.console import Console
import os
import datetime


def get_id(source, results, type):
    if not any((result.name == source and result.type == type) for result in results):
        return False
    else:
        ind = next((index for (index, result) in enumerate(results) if (result.name == source)), None)
        id = results[ind].id
        return id


class Provider(object):

    def __init__(self):
        print("init {name}".format(name=self.__class__.__name__))
        self.config = Config()
        credentials = self.config.credentials("storage", "box")
        self.sdk = JWTAuth.from_settings_file(credentials['config_path'])
        self.client = Client(self.sdk)

    def put(self, source, destination, recursive=False):
        try:
            destpath = destination.split('/')
            dest = destpath[len(destpath)-1]
            sourcepath = source.strip('/').split('/')
            if os.path.isfile(source):
                filename = sourcepath[len(sourcepath)-1]
                if recursive:
                    Console.error("Invalid option recursive for source type.")
                    return
            uploaded = []
            if dest == ('' or 'All Files'):
                files = [item for item in self.client.folder('0').get_items()]
            else:
                items = self.client.search().query(dest, type='folder')
                folders = [item for item in items]
                folder_id = get_id(dest, folders, 'folder')
                if folder_id:
                    files = [item for item in self.client.folder(folder_id).get_items()]
                else:
                    Console.error("Destination directory not found")
                    return
            if not recursive:
                file_id = get_id(filename, files, 'file')
                if not file_id:
                    file = self.client.folder('0').upload(source)
                    print(file.__dict__)
                    return file.__dict__
                else:
                    file = self.client.file(file_id).update_contents(source)
                    print(file.__dict__)
                    return file.__dict__
            else:
                for s in os.listdir(source):
                    s_id = get_id(s, files)
                    print(id)
                    if not id:
                        file = self.client.folder('0').upload(source+'/'+s)
                        print(file.__dict__)
                        uploaded.append(file)
                    else:
                        file = self.client.file(s_id).update_contents(source+'/'+s)
                        print(file.__dict__)
                        uploaded.append(file)
                return uploaded
        except Exception as e:
            Console.error(e)

    def get(self, source, destination, recursive=False):
        try:
            boxpath = source.split('/')
            target = boxpath[len(boxpath)-1]
            downloads = []
            if recursive:
                if target == ('' or 'All Files'):
                    files = [item for item in self.client.folder('0').get_items()]
                else:
                    results = [item for item in self.client.search().query(target)]
                    folder_id = get_id(target, results, 'folder')
                    if folder_id:
                        files = [item for item in self.client.folder(folder_id).get_items()]
                    else:
                        Console.error("Source directory not found.")
                        return
                for f in files:
                    if f.type == 'file':
                        file = self.client.file(f.id).get()
                        with open(destination + "/" + file.name, 'wb') as f:
                            self.client.file(f.id).download_to(f)
                            downloads.append(file)
                for d in downloads:
                    print(d.__dict__)
                return downloads
            else:
                results = [item for item in self.client.search().query(target)]
                if not any(result.name == target for result in results):
                    Console.error("Source file not found.")
                else:
                    file_id = get_id(target, results, 'file')
                    if file_id:
                        file = self.client.file(file_id).get()
                        with open(destination + "/" + file.name, 'wb') as f:
                            self.client.file(file.id).download_to(f)
                            print(file.__dict__)
                            return file.__dict__
        except Exception as e:
            Console.error(e)

    def search(self, directory, filename, recursive=False):
        try:
            path = directory.split('/')
            if path[len(path)-1] == ('' or 'All Files'):
                id = '0'
            else:
                items = self.client.search().query(path[len(path)-1], type='folder')
                id = get_id(path[len(path)-1], items)
                if not id:
                    Console.error("Directory not found.")
                    return
            if not recursive:
                items = self.client.search().query(filename, type='file', ancestor_folder_ids=id)
                files = []
                for item in items:
                    files.append(item.__dict__)
                    print(item.__dict__)
                if len(files) > 0:
                    return files
                else:
                    Console.error("No files found")
            else:

        except Exception as e:
            Console.error(e)

    def create_dir(self, directory):
        try:
            path = directory.strip('/').split('/')
            if len(path) == 1:
                folder = self.client.folder('0').create_subfolder(path[0])
                print(folder.__dict__)
                return folder.__dict__
            else:
                parent = path[len(path) - 2]
                items = self.client.search().query(parent, type='folder')
                folders = [item for item in items]
                if len(folders) > 0:
                    parent = folders[0].id
                    folder = self.client.folder(parent).create_subfolder(path[len(path)-1])
                    print(folder.__dict__)
                    return folder.__dict__
                else:
                    Console.error("Destination directory not found")
        except Exception as e:
            Console.error(e)

    def list(self, directory, recursive=False):
        try:
            list = []
            path = directory.split('/')
            for i in range(1, len(path)+1):
                if path[len(path)-i] == ('' or 'All Files'):
                    items = self.client.folder('0').get_items()
                    contents = [item for item in items]
                    for c in contents:
                        list.append(c)
                else:
                    items = self.client.search().query(path[len(path)-i], type='folder')
                    folders = [item for item in items]
                    folder_id = get_id(path[len(path)-i], folders)
                    if folder_id:
                        results = self.client.folder(folder_id).get_items()
                        contents = [result for result in results]
                        for c in contents:
                            list.append(c)
                    else:
                        Console.error("Directory " + path[len(path) - i] + " not found.")
                if not recursive and i == 1:
                    for l in list:
                        print(l.__dict__)
                    return list
            for l in list:
                print(l.__dict__)
            return list
        except Exception as e:
            Console.error(e)

    def delete(self, source):
        try:
            path = source.strip('/').split('/')
            print(path)
            name = path[len(path)-1]
            items = self.client.search().query(name)
            results = [item for item in items]
            if not any(result.name == name for result in results):
                Console.error("Source not found")
            else:
                item_ind = next((index for (index, result) in enumerate(results) if (result.name == name)), None)
                item_id = results[item_ind].id
                item_type = results[item_ind].type
                if item_type == 'folder':
                    self.client.folder(item_id).delete()
                elif item_type == 'file':
                    self.client.file(item_id).delete()
        except Exception as e:
            Console.error(e)

    def entries(self):
        return {
            "name": "NAME",
            "created": "TBD",
            "updated": "TBD",
            "cloud": "box",
            "kind": "storage",
            "driver": "box",
            "collection": "box-storage"
        }
