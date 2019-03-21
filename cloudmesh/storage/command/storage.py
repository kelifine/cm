from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.storage.api.manager import Manager
from cloudmesh.shell.variables import Variables
from pprint import pprint
from cloudmesh.common.console import Console


# noinspection PyBroadException
class StorageCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_storage(self, args, arguments):
        """
        ::

          Usage:
                storage [--storage=SERVICE] put FILENAME SOURCEDIR [DESTDIR]
                storage [--storage=SERVICE] get FILENAME DESTDIR
                storage [--storage=SERVICE] delete FILENAME
                storage [--storage=SERVICE] info FILENAME
                storage [--storage=SERVICE] search FILENAME
                storage [--storage=SERVICE] create dir DIRNAME [DESTDIR]
                storage [--storage=SERVICE] list dir [DIRNAME]
                storage [--storage=SERVICE] delete dir DIRNAME


          This command creates, deletes, and returns information on directories and files in cloud storage services.

          Arguments:
              FILE      a file name
              DESTDIR   destination directory for uploads and downloads
              SOURCEDIR source directory for syncing directories
              DIRNAME name of new folder


          Example:
            set storage=box
            storage put FILENAME SOURCEDIR DESTDIR

            is the same as 

            storage  --storage=box put FILENAME SOURCEDIR DESTDIR


        """

        pprint(arguments)

        m = Manager()

        service = None

        try:
            service = arguments["--storage"]
        except Exception as e:
            try:
                v = Variables()
                service = v['storage']
            except Exception as e:
                service = None

        if service is None:
            Console.error("storage service not defined")


        if arguments.get==True:
            m.get(service, arguments.FILENAME, arguments.DESTDIR)
        elif arguments.put==True:
            if arguments.DESTDIR is not None:
                m.put(service, arguments.FILENAME, arguments.SOURCEDIR, arguments.DESTDIR)
            else:
                m.put(service, arguments.FILENAME, arguments.SOURCEDIR)
        elif arguments.delete==True:
            m.delete(service, arguments.FILENAME)
        elif arguments.info==True:
            m.info(service, arguments.FILENAME)
        elif arguments.search==True:
            m.search(service, arguments.FILENAME)
        elif arguments.create==True and arguments.dir == True:
            if arguments.DESTDIR is not None:
                m.create_dir(service, arguments.DIRNAME, arguments.DESTDIR)
            else:
                m.create_dir(service, arguments.DIRNAME)
        elif arguments.list==True and arguments.dir==True:
            if arguments.DIRNAME is not None:
                m.list_dir(service, arguments.DIRNAME)
            else:
                m.list_dir(service)
        elif arguments.delete==True and arguments.dir==True:
            m.delete_dir(service, arguments.DIRNAME)
        else:
            print("Command not recognized.")
