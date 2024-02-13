import argparse
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
        try:
            for i in range(num_containers):
                hostname = f"{self.cluster_name}-container{i+1}"
                container = self._create_container(hostname)
                self.containers.append({"id": container.id, "hostname": hostname})
                log_data = {"event": "create_container", "container_id": container.id, "hostname": hostname}
                logging.info(json.dumps(log_data))

            print("Cluster created successfully.")
        except docker.errors.APIError as e:
            print(f"Error creating cluster: {e}")

    def list_cluster(self):
        try:
            for container in self.containers:
                self._print_container_info(container["id"])
        except docker.errors.APIError as e:
            print(f"Error listing cluster: {e}")

    def run_command_in_cluster(self, command):
        try:
            for container in self.containers:
                self._execute_command_in_container(container["id"], command)
        except docker.errors.APIError as e:
            print(f"Error running command in cluster: {e}")

    def stop_cluster(self):
        try:
            for container in self.containers:
                self._stop_container(container["id"])
                log_data = {"event": "stop_container", "container_id": container['id']}
                logging.info(json.dumps(log_data))

            print("Cluster stopped successfully.")
        except docker.errors.APIError as e:
            print(f"Error stopping cluster: {e}")

        self.containers = []

    def delete_all_containers(self):
        try:
            for container in self.containers:
                self._delete_container(container["id"])
                log_data = {"event": "delete_container", "container_id": container['id']}
                logging.info(json.dumps(log_data))

            print("All containers deleted successfully.")
        except docker.errors.APIError as e:
            print(f"Error deleting containers: {e}")

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

def main():
    parser = argparse.ArgumentParser(description='Cluster Manager CLI')
    # parser.add_argument('--cluster', required=True, help='Specify the cluster name')

    args = parser.parse_args()
    cluster_manager = ClusterManager(args.cluster)

    while True:
        print("\nOptions:")
        print("1. Create Cluster")
        print("2. List Cluster")
        print("3. Run Command in Cluster")
        print("4. Stop Cluster")
        print("5. Delete All Containers")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        try:
            if choice == '1':
                cluster_manager.create_cluster()
            elif choice == '2':
                cluster_manager.list_cluster()
            elif choice == '3':
                command = input("Enter the command to run in the cluster: ")
                cluster_manager.run_command_in_cluster(command)
            elif choice == '4':
                cluster_manager.stop_cluster()
            elif choice == '5':
                cluster_manager.delete_all_containers()
            elif choice == '6':
                print("Exiting Cluster Manager. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 6.")
        except KeyboardInterrupt:
            print("\nOperation aborted by the user.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
