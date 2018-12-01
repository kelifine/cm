import pprint
from cm4.vm.Cmaws import Cmaws
from cm4.vm.CmAzure import CmAzure
from cm4.vm.Cmopenstack import Cmopenstack
from cm4.configuration.config import Config
from cm4.cmmongo.mongoDB import MongoDB
from cm4.configuration.name import Name
from cm4.vm.thread import thread
from cm4.configuration.counter import Counter


class Vmprovider (object):

    def __init__(self):
        self.config = Config()

    def get_provider(self, cloud):
        """
        Create the driver based on the 'kind' information.
        This method could deal with AWS, AZURE, and OPENSTACK for CLOUD block of YAML file.
        Only developed for AZURE, AWS, Chameleon, but we haven't test OPENSTACK
        :return: the driver based on the 'kind' information
        """

        os_config = self.config.get('cloud.%s' % cloud)
        if os_config.get('cm').get('kind') == 'azure':
            driver = CmAzure(self.config, cloud).driver
        elif os_config.get('cm').get('kind') == 'aws':
            driver = Cmaws(self.config, cloud).driver
        elif os_config.get('cm').get('kind') == 'openstack':
            driver = Cmopenstack(self.config, cloud).driver
        return driver


class Vm:

    def __init__(self, cloud):
        config = Config()
        self.provider = Vmprovider().get_provider(cloud)

        self.mongo = MongoDB(host=config.get('data.mongo.MONGO_HOST'),
                             username=config.get('data.mongo.MONGO_USERNAME'),
                             password=config.get('data.mongo.MONGO_PASSWORD'),
                             port=config.get('data.mongo.MONGO_PORT'))
        #print(config.get('data.mongo.MONGO_HOST'))


    def start(self, name):
        """
        start the node based on the id
        :param name:
        :return: VM document
        """
        info = self.info(name)
        if info.state != 'running':
            self.provider.ex_start_node(info)
            thread(self, 'test', name, 'running').start()
            document = self.mongo.find_document('cloud', 'name', name)
            return document
        else:
            document = self.mongo.find_document('cloud', 'name', name)
            return document

    def stop(self, name, deallocate=True):
        """
        stop the node based on the ide
        :param name:
        :param deallocate:
        :return: VM document
        """
        info = self.info(name)
        if info.state != 'stopped':
            self.provider.ex_stop_node(info, deallocate)
            thread(self, 'test', name, 'stopped').start()
            document = self.mongo.find_document('cloud', 'name', name)
            return document
        else:
            document = self.mongo.find_document('cloud', 'name', name)
            return document

    def resume(self, name):
        """
        start the node based on id
        :param name:
        """
        return self.start(name)

    def suspend(self, name):
        """
        stop the node based on id
        :param name:
        """
        return self.stop(name, False)

    def destroy(self, name):
        """
        delete the node based on id
        :param name:
        :return: True/False
        """
        result = self.provider.destroy_node(self.info(name))
        self.mongo.delete_document('cloud', 'name', name)
        return result

    def create(self, name):
        """
        create a new node
        :param name: the name for the new node
        :return:
        """
        node = self.provider.create_node(name)
        self.mongo.insert_cloud_document(vars(node))
        return node

    def list(self):
        """
        list existed nodes
        :return: all nodes' information
        """
        result = self.provider.list_nodes()
        return result

    def status(self, name):
        """
        show node information based on id
        :param name:
        :return: all information about one node
        """
        self.info(name).state
        status = self.mongo.find_document('cloud', 'name', name)['state']
        return status

    def info(self, name):
        """
        show node information based on id
        :param name:
        :return: all information about one node
        """
        nodes = self.list()
        for i in nodes:
            if i.name == name:
                document = vars(i)
                if self.mongo.find_document('cloud', 'name', name):
                    self.mongo.update_document('cloud', 'name', name, document)
                else:
                    self.mongo.insert_cloud_document(document)
                return i

    def new_name(self, experiment, group, user):
        """
        TODO: Doc

        TODO: use config defaults by default.

        :param experiment:
        :param group:
        :return:
        """
        counter = Counter()
        count = counter.get()
        name = Name()
        name_format = {'experiment': experiment, 'group': group, 'user': user, 'counter': count}
        name.set_schema('instance')
        counter.incr()
        counter.set()
        return name.get(name_format)

    def get_public_ips(self, name=None):
        """
        Returns all the public ips available if a name is not given.
        If a name is provided, the ip of the vm name would be returned.
        :param name: name of the VM.
        :return: Dictionary of VMs with their public ips
        """
        if name is None:
            filter = {
                "$exists": True,
                "$not": {"$size": 0}
            }
            documents = self.mongo.find('cloud', 'public_ips', filter)
            if documents is not None:
                return None
            else:
                result = {}
                for document in documents:
                    result[document['name']] = document['public_ips']
                return result
        else:
            public_ips = self.mongo.find_document('cloud', 'name', name)['public_ips']
            if not public_ips:
                return None
            else:
                return {name: public_ips}

    def set_public_ip(self, name, public_ip):
        """
        Assign the given public ip to the given VM.
        :param name: name of the VM
        :param public_ip: public ip to be assigned.
        """
        if name is not None and public_ip is not None:
            self.provider.set_public_ip(name, public_ip)

    def remove_public_ip(self, name):
        """
        Deletes the public ip of the given VM.
        :param name: name of the VM
        """
        if name is not None:
            self.provider.remove_public_ip(name)


def process_arguments(arguments):
    """
    Process command line arguments to execute VM actions.
    Called from cm4.command.command
    :param arguments:
    """
    result = None

    if arguments.get("--debug"):
        pp = pprint.PrettyPrinter(indent=4)
        print("vm processing arguments")
        pp.pprint(arguments)

    config = Config()
    default_cloud = config.get("default.cloud")
    default_group = config.get("default.group")
    default_experiment = config.get("default.experiment")
    default_cluster = config.get("default.cluster")

    vm = Vm(default_cloud)

    if arguments.get("list"):
        result = vm.list()

    elif arguments.get("create"):
        # TODO: Reconcile `create` behavior here and in docopts where
        #       create is called with a `VMCOUNT`.

        vm_name = arguments.get("VMNAME")

        if vm_name is None:
            vm_name = vm.new_name(default_experiment, default_group, "user")

        vm.create(vm_name)
        result = f"Created {vm_name}"
    elif arguments.get("start"):
        vm.start(arguments.get("--vms"))
    elif arguments.get("stop"):
        vm.stop(arguments.get("--vms"))
    elif arguments.get("destroy"):
        vm.destroy(arguments.get("--vms"))
    elif arguments.get("status"):
        vm.status(arguments.get("--vms"))
    elif arguments.get("ssh"):
        # TODO
        pass
    elif arguments.get("run"):
        # TODO
        pass
    elif arguments.get("script"):
        # TODO
        pass

    return result
