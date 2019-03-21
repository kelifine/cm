from boxsdk import JWTAuth
from boxsdk import Client
from cloudmesh.management.configuration.config import Config
import os


class Provider(object):

    def __init__(self):
        print("init {name}".format(name=self.__class__.__name__))
        self.config = Config()
        credentials = self.config.credentials("storage", "box")
        self.sdk = JWTAuth.from_settings_file(credentials['config_path'])
        self.client = Client(self.sdk)

    def put(self, filename, source, dir = None):
        try:
            if dir is None:
                files = [item for item in self.client.folder('0').get_items()]
                if not any(file.name == filename for file in files):
                    file = self.client.folder('0').upload(source+'/'+filename)
                    print(file.__dict__)
                    return file.__dict__
                else:
                    file_ind = next((index for (index, file) in enumerate(files) if file.name == filename), None)
                    file_id = files[file_ind].id
                    file = self.client.file(file_id).update_contents(source+'/'+filename)
                    print(file.__dict__)
                    return file.__dict__
            else:
                items = self.client.search().query(dir, type='folder')
                folders = [item for item in items]
                if len(folders)>0:
                    folder_id = folders[0].id
                    items = self.client.folder(folder_id).get_items()
                    if not any(item.name == filename for item in items):
                        file = self.client.folder(folder_id).upload_file(filename)
                    else:
                        file_ind = next((index for (index, item) in enumerate(items) if item.name == filename), None)
                        file_id = folders[file_ind].id
                        file = self.client.file(file_id).update_contents(filename)
                    print(file.__dict__)
                    return file.__dict__
                else:
                    print("Folder not found")
        except Exception as e:
            print(e)

    def get(self, filename, dir):
        try:
            items = self.client.search().query(filename, type='file')
            for item in items:
                if item.name == filename:
                    file_id = item.id
                    file = self.client.file(file_id).get()
                    with open(dir+"/"+filename, 'wb') as f:
                        self.client.file(file_id).download_to(f)
                    print(file.__dict__)
                    return file.__dict__
            if not any(item.name == filename for item in items):
                print("File not found")
        except Exception as e:
            print(e)

    def delete(self, filename):
        try:
            items = self.client.search().query(filename, type='file')
            files = [item for item in items]
            if any(file.name==filename for file in files):
                file_ind = next((index for (index, file) in enumerate(files) if file.name == filename), None)
                file_id = files[file_ind].id
                self.client.file(file_id).delete()
            else:
                print("File not found")
        except Exception as e:
            print(e)

    def info(self, filename):
        try:
            items = self.client.search().query(filename, type='file')
            files = [item for item in items]
            if any(file.name == filename for file in files):
                file_ind = next((index for (index, file) in enumerate(files) if file.name == filename), None)
                file = self.client.file(files[file_ind].id).get()
                print(file.__dict__)
                return file.__dict__
            else:
                print("File not found")
        except Exception as e:
            print(e)

    def search(self, filename):
        try:
            items = self.client.search().query(filename, type='file')
            files = []
            for item in items:
                files.append(item.__dict__)
                print(item.__dict__)
            if len(files)>0:
                return files
            else:
                print("No files found")
        except Exception as e:
            print(e)

    def create_dir(self, dir, parent=None):
        try:
            if parent is None:
                folder = self.client.folder('0').create_subfolder(dir)
                print(folder.__dict__)
                return folder.__dict__
            else:
                items = self.client.search().query(parent, type='folder')
                folders = [item for item in items]
                if len(folders)>0:
                    parent = folders[0].id
                    folder = self.client.folder(parent).create_subfolder(dir)
                    print(folder.__dict__)
                    return folder.__dict__
                else:
                    print("Destination directory not found")
        except Exception as e:
            print(e)

    def list_dir(self, dir=None):
        try:
            if dir is None:
                items = self.client.folder('0').get_items()
                contents = [item for item in items]
                for c in contents:
                    print(c.__dict__)
                return contents
            else:
                items = self.client.search().query(dir, type='folder')
                folders = [item for item in items]
                for folder in folders:
                    if folder.name == dir:
                        results = self.client.folder(folder.id).get_items()
                        contents = [result for result in results]
                        for c in contents:
                            print(c.__dict__)
                        return contents
        except Exception as e:
            print(e)

    def delete_dir(self, dir):
        try:
            items = self.client.search().query(dir)
            folders = [item for item in items]
            if not any(folder.name == dir for folder in folders):
                print("Folder not found")
            else:
                folder_ind = next((index for (index, folder) in enumerate(folders) if (folder.name == dir and folder.type=='folder')), None)
                folder_id = folders[folder_ind].id
                self.client.folder(folder_id).delete()
        except Exception as e:
            print(e)
