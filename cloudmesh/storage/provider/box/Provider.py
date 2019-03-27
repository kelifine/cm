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

    def get_id(self, source, results):
        if not any(result.name == source for result in results):
            return False
        else:
            ind = next((index for (index, result) in enumerate(results) if (result.name==source)), None)
            id = results[ind].id
            return id

    def put(self, source, destination, recursive=False):
        try:
            destpath = destination.split('/')
            dest = destpath[len(destpath)-1]
            sourcepath= source.strip('/').split('/')
            if os.path.isfile(source):
                filename = sourcepath[len(sourcepath)-1]
                if recursive==True:
                    print("Invalid option recursive for source type.")
                    return
            uploaded = []
            if dest =='':
                files = [item for item in self.client.folder('0').get_items()]
                if recursive==False:
                    id = self.get_id(filename, files)
                    print(id)
                    if id==False:
                        file = self.client.folder('0').upload(source)
                        print(file.__dict__)
                        return file.__dict__
                    else:
                        file = self.client.file(id).update_contents(source)
                        print(file.__dict__)
                        return file.__dict__
                else:
                    for s in os.listdir(source):
                        id = self.get_id(s, files)
                        print(id)
                        if id==False:
                            file = self.client.folder('0').upload(source+'/'+s)
                            print(file.__dict__)
                            uploaded.append(file)
                        else:
                            file = self.client.file(id).update_contents(source+'/'+s)
                            print(file.__dict__)
                            uploaded.append(file)
                    return uploaded
            else:
                items = self.client.search().query(dest, type='folder')
                folders = [item for item in items]
                id = self.get_id(dest, folders)
                if id!=False:
                    results = self.client.folder(id).get_items()
                    if recursive==False:
                        file_id = self.get_id(filename, results)
                        if file_id==False:
                            file = self.client.folder(id).upload_file(source)
                        else:
                            file = self.client.file(file_id).update_contents(source)
                        print(file.__dict__)
                        return file.__dict__
                    else:
                        for s in os.listdir(source):
                            s_id = self.get_id(s, results)
                            if s_id==False:
                                file = self.client.folder(id).upload(source+'/'+s)
                                print(file.__dict__)
                                uploaded.append(file)
                            else:
                                file = self.client.file(s_id).update_contents(source+'/'+s)
                                print(file.__dict__)
                                uploaded.append(file)
                        return uploaded
                else:
                    print("Destination directory not found")
                    return
        except Exception as e:
            print(e)

    def get(self, source, destination, recursive=False):
        try:
            boxpath = source.split('/')
            target = boxpath[len(boxpath)-1]
            downloads=[]
            if target=='' and recursive==True:
                results = self.client.folder('0').get_items()
                contents = [result for result in results]
                for c in contents:
                    if c.type == 'file':
                        file = self.client.file(c.id).get()
                        with open(destination + "/" + file.name, 'wb') as f:
                            self.client.file(c.id).download_to(f)
                            downloads.append(file)
                for d in downloads:
                    print(d.__dict__)
                return downloads
            else:
                items = self.client.search().query(target)
                for item in items:
                    if item.name == target:
                        if (item.type=='folder' and recursive==False) or (item.type=='file' and recursive==True):
                            print("Invalid option for source type.")
                            return
                        elif item.type=='file' and recursive==False:
                            file = self.client.file(item.id).get()
                            with open(destination+"/"+item.name, 'wb') as f:
                                self.client.file(item.id).download_to(f)
                                print(file.__dict__)
                                return file.__dict__
                        elif item.type=='folder' and recursive==True:
                            results = self.client.folder(item.id).get_items()
                            contents = [result for result in results]
                            for c in contents:
                                if c.type=='file':
                                    file = self.client.file(c.id).get()
                                    with open(destination+"/"+file.name, 'wb') as f:
                                        self.client.file(c.id).download_to(f)
                                        print(file.__dict)
                                        downloads.append(file)
                                for d in downloads:
                                    print(d.__dict__)
                                return downloads
                if not any(item.name == target for item in items):
                    print("Source not found")
                    return
        except Exception as e:
            print(e)

    def search(self, directory, filename, recursive=False):
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

    def create_dir(self, directory):
        try:
            path = directory.strip('/').split('/')
            if len(path)==1:
                folder = self.client.folder('0').create_subfolder(path[0])
                print(folder.__dict__)
                return folder.__dict__
            else:
                parent = path[len(path) - 2]
                items = self.client.search().query(parent, type='folder')
                folders = [item for item in items]
                if len(folders)>0:
                    parent = folders[0].id
                    folder = self.client.folder(parent).create_subfolder(path[len(path)-1])
                    print(folder.__dict__)
                    return folder.__dict__
                else:
                    print("Destination directory not found")
        except Exception as e:
            print(e)

    def list(self, directory, recursive=False):
        try:
            list = []
            path = directory.split('/')
            for i in range(1, len(path)+1):
                if path[len(path)-i]=='':
                    items = self.client.folder('0').get_items()
                    contents = [item for item in items]
                    for c in contents:
                        list.append(c)
                else:
                    items = self.client.search().query(path[len(path)-i], type='folder')
                    folders = [item for item in items]
                    folder_id = self.get_id(path[len(path)-i], folders)
                    if folder_id != False:
                        results = self.client.folder(folder_id).get_items()
                        contents = [result for result in results]
                        for c in contents:
                            list.append(c)
                    else:
                        print("Directory " + path[len(path) - i] + " not found.")
                if (recursive==False and i==1):
                    for l in list:
                        print(l.__dict__)
                    return list
            for l in list:
                print(l.__dict__)
            return list
        except Exception as e:
            print(e)

    def delete(self, source):
        try:
            path = source.strip('/').split('/')
            print(path)
            name = path[len(path)-1]
            items = self.client.search().query(name)
            results = [item for item in items]
            if not any(result.name == name for result in results):
                print("Source not found")
            else:
                item_ind = next((index for (index, result) in enumerate(results) if (result.name == name)), None)
                item_id = results[item_ind].id
                item_type = results[item_ind].type
                print(item_id)
                print(item_type)
                if item_type=='folder':
                    self.client.folder(item_id).delete()
                elif item_type=='file':
                    self.client.file(item_id).delete()
        except Exception as e:
            print(e)


