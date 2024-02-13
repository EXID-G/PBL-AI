import docker
import logging

# 配置日志
logging.basicConfig(filename='cluster_manager.log', level=logging.INFO)

class ClusterManager:
    def __init__(self):
        self.client = docker.from_env()
        self.containers = []

    def create_cluster(self, num_containers=8):
        for i in range(num_containers):
            hostname = f"container{i+1}"
            container = self._create_container(hostname)
            self.containers.append({"id": container.id, "hostname": hostname})
            logging.info(f"Container {container.id} created with hostname {hostname}")

    def list_cluster(self):
        for container in self.containers:
            self._print_container_info(container["id"])

    def run_command_in_cluster(self, command):
        for container in self.containers:
            self._execute_command_in_container(container["id"], command)

    def stop_cluster(self):
        for container in self.containers:
            self._stop_container(container["id"])
            logging.info(f"Container {container['id']} stopped")

        self.containers = []

    def delete_all_containers(self):
        for container in self.containers:
            self._delete_container(container["id"])
            logging.info(f"Container {container['id']} deleted")

        self.containers = []

    def _create_container(self, hostname):
        container = self.client.containers.run('your_image', detach=True, hostname=hostname)
        return container

    def _print_container_info(self, container_id):
        container = self.client.containers.get(container_id)
        print(f"Container ID: {container_id}, Hostname: {container.attrs['Config']['Hostname']}")
        logging.info(f"Container {container_id} information printed")

    def _execute_command_in_container(self, container_id, command):
        container = self.client.containers.get(container_id)
        exec_id = container.exec_run(command)
        print(f"Command output for Container {container_id}: {exec_id.output.decode()}")
        logging.info(f"Command '{command}' executed in Container {container_id}")

    def _stop_container(self, container_id):
        container = self.client.containers.get(container_id)
        container.stop()

    def _delete_container(self, container_id):
        container = self.client.containers.get(container_id)
        container.remove()

# Example usage:
cm = ClusterManager()
cm.create_cluster()
cm.list_cluster()
cm.run_command_in_cluster('echo "Hello from the cluster!"')
cm.stop_cluster()
cm.delete_all_containers()
