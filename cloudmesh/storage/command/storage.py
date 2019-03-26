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
                storage [--storage=SERVICE] put SOURCE DESTINATION [--recursive]
                storage [--storage=SERVICE] get SOURCE DESTINATION [--recursive]
                storage [--storage=SERVICE] search DIRECTORY FILENAME [--recursive]
                storage [--storage=SERVICE] create dir DIRECTORY
                storage [--storage=SERVICE] list SOURCE [--recursive]
                storage [--storage=SERVICE] delete SOURCE


          This command creates, deletes, and returns information on directories and files in cloud storage services.

          Arguments:
              FILENAME      a file name
              DESTINATION   destination directory
              SOURCE        source file or directory
              DIRECTORY     name of directory


          Example:
            set storage=box
            storage put SOURCE DESTINATION --recursive

            is the same as 

            storage  --storage=box put SOURCE DESTINATION --recursive


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


        if arguments['get']==True:
            m.get(service, arguments.SOURCE, arguments.DESTINATION, arguments['--recursive'])
        elif arguments.put==True:
            m.put(service, arguments.SOURCE, arguments.DESTINATION, arguments['--recursive'])
        elif arguments.search==True:
            m.search(service, arguments.DIRECTORY, arguments.FILENAME, arguments['--recursive'])
        elif arguments.create==True and arguments.dir == True:
            m.create_dir(service, arguments.DIRECTORY)
        elif arguments.list==True:
            m.list(service, arguments.SOURCE, arguments['--recursive'])
        elif arguments.delete==True:
            m.delete(service, arguments.SOURCE)
        else:
            print("Command not recognized.")
