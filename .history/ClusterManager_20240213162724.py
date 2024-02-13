import argparse
import docker
import logging
import json

class ClusterManager:
    def __init__(self, cluster_name):
        self.client = docker.from_env()
        self.containers = []    ## record the hostname of each container
        self.cluster_name = cluster_name

        logging.basicConfig(filename=f'logfile/CM_{cluster_name}.log', level=logging.INFO, format='%(message)s')
        log_data = {"event": "init_cluster_manager", "cluster_name": cluster_name}
        logging.info(json.dumps(log_data))
        print(f"Cluster Manager {self.cluster_name} initialized successfully.")

##########* create
    def create_containers(self, num_containers=8, name_list=None):
        try:
            for i in range(num_containers):
                hostname = f"{self.cluster_name}-container{i+1}"
                container = self._create_container(hostname,name_list[i] if name_list else None)
                self.containers.append({"id": container.id, "name": container.name,"hostname": hostname})

                # log_data = {"event": "create_container", "container_id": container.id, "hostname": hostname}
                # logging.info(json.dumps(log_data))

            print("Containers created successfully.")
        except docker.errors.APIError as e:
            print(f"Error creating cluster: {e}")

    def _create_container(self, hostname,name=None):
        container = self.client.containers.run('tensorflow/tensorflow', detach=True, hostname=hostname, name=name)
        return container

##########* list
    def list_all_containers(self):
        try:
            for container in self.containers:
                self._print_container_info(container["id"])
        except docker.errors.APIError as e:
            print(f"Error listing cluster: {e}")

    def _print_container_info(self, container_id):
        container = self.client.containers.get(container_id)
        print(f"Cluster: {self.cluster_name}, Container ID: {container_id}, Name: {container.name}, Status: {container.status}, Hostname: {container.attrs['Config']['Hostname']}")

    def list_running_containers(self):
        try:
            running_containers = self.client.containers.list(filters={'status': 'running'})
            for container in running_containers:
                self._print_container_info(container.id)
        except docker.errors.APIError as e:
            print(f"Error listing running containers: {e}")

    def list_stopped_containers(self):
        try:
            stopped_containers = self.client.containers.list(all=True, filters={'status': 'exited'})
            for container in stopped_containers:
                self._print_container_info(container.id)
        except docker.errors.APIError as e:
            print(f"Error listing stopped containers: {e}")

##########* run
    def run_command_in_cluster(self, command):
        try:
            for container in self.containers:
                self._execute_command_in_container(container["id"], command)
        except docker.errors.APIError as e:
            print(f"Error running command in cluster: {e}")

##########* stop
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


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Cluster Manager CLI')
    # parser.add_argument('--cluster', required=True, help='Specify the cluster name')
    # args = parser.parse_args()

    print("----------------Welcome to the Cluster Manager CLI!----------------")
    print("This CLI allows you to manage a cluster of containers.")
    print("To get started, please enter the name of the cluster you want to manage.")
    CM_name = input("Enter the name of the cluster: ")
    cluster_manager = ClusterManager(CM_name)

    while True:
        print("\n \----------Options:----------\\")
        print("1. Create containers in the Cluster")
        print("2. Get/List containers' info")
        print("3. Run Command in Cluster")
        print("4. Stop Cluster")
        print("5. Delete All Containers")
        print("6. Clear the log file")
        print("7. Exit")

        choice = input("Enter your choice (1-6): ")

        try:
            if choice == '1':
                num = input("Enter the number of containers to create (default=8): ")
                num = int(num)
                while(True):
                    choice = input("Do you want to designate names of containers? (y/n): ")
                    if choice == 'y':
                        name_list = input("Enter the name list of the cluster (Separated by space): ")
                        name_list = name_list.split()
                        if len(name_list) != int(num):
                            print("The number of names should be equal to the number of containers.")
                            continue
                        cluster_manager.create_containers(num_containers = num, name_list = name_list)
                        break
                    elif choice == "n":
                        cluster_manager.create_containers(num_containers = num)
                        break
                    else:
                        print("Invalid input")
                        continue
            elif choice == '2':
                while(True):
                    choice2 = input("1. List all containers\n2. List running containers\n3. List stopped containers\n4. List one designated container\nEnter your choice (1-4): ")
                    if choice2 == '1':
                        cluster_manager.list_all_containers()
                        break
                    elif choice2 == '2':
                        cluster_manager.list_running_containers()
                        break
                    elif choice2 == '3':
                        cluster_manager.list_stopped_containers()
                        break
                    elif choice2 == '4':
                        container_name = input("Enter the name/id of the container completely: ")
                        cluster_manager.list_one_container(container_name)
                        break
                    else:
                        print("Invalid input")
                        continue
            elif choice == '3':
                cluster_manager.list_all_containers()
            elif choice == '3':
                command = input("Enter the command to run in the cluster: ")
                cluster_manager.run_command_in_cluster(command)
            elif choice == '4':
                cluster_manager.stop_cluster()
            elif choice == '5':
                cluster_manager.delete_all_containers()
            elif choice == '6':
                cluster_manager.delete_all_containers()
                print("Exiting Cluster Manager. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 6.")
        except KeyboardInterrupt:
            print("\nOperation aborted by the user.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

