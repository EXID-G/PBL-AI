import docker
import logging
import json

class ClusterManager:
    def __init__(self, cluster_name):
        self.client = docker.from_env()
        self.containers = []
        self.cluster_name = cluster_name

        # 配置JSON格式的日志，并使用独立的文件名
        logging.basicConfig(filename=f'{cluster_name}_cluster_manager.log', level=logging.INFO, format='%(message)s')

    def create_cluster(self, num_containers=8):
        for i in range(num_containers):
            hostname = f"{self.cluster_name}-container{i+1}"
            container = self._create_container(hostname)
            self.containers.append({"id": container.id, "hostname": hostname})
            log_data = {"event": "create_container", "container_id": container.id, "hostname": hostname}
            logging.info(json.dumps(log_data))

    def list_cluster(self):
        for container in self.containers:
            self._print_container_info(container["id"])

    def run_command_in_cluster(self, command):
        for container in self.containers:
            self._execute_command_in_container(container["id"], command)

    def stop_cluster(self):
        for container in self.containers:
            self._stop_container(container["id"])
            log_data = {"event": "stop_container", "container_id": container['id']}
            logging.info(json.dumps(log_data))

        self.containers = []

    def delete_all_containers(self):
        for container in self.containers:
            self._delete_container(container["id"])
            log_data = {"event": "delete_container", "container_id": container['id']}
            logging.info(json.dumps(log_data))

        self.containers = []

    def _create_container(self, hostname):
        container = self.client.containers.run('your_image', detach=True, hostname=hostname)
        return container

    def _print_container_info(self, container_id):
        container = self.client.containers.get(container_id)
        print(f"Cluster: {self.cluster_name}, Container ID: {container_id}, Hostname: {container.attrs['Config']['Hostname']}")

    def _execute_command_in_container(self, container_id, command):
        container = self.client.containers.get(container_id)
        exec_id = container.exec_run(command)
        print(f"Command output for Container {container_id}: {exec_id.output.decode()}")

    def _stop_container(self, container_id):
        container = self.client.containers.get(container_id)
        container.stop()

    def _delete_container(self, container_id):
        container = self.client.containers.get(container_id)
        container.remove()

# Example usage:
cluster1 = ClusterManager("cluster1")
cluster1.create_cluster()
cluster1.list_cluster()
cluster1.run_command_in_cluster('echo "Hello from Cluster 1!"')
cluster1.stop_cluster()
cluster1.delete_all_containers()

cluster2 = ClusterManager("cluster2")
cluster2.create_cluster()
cluster2.list_cluster()
cluster2.run_command_in_cluster('echo "Hello from Cluster 2!"')
cluster2.stop_cluster()
cluster2.delete_all_containers()
