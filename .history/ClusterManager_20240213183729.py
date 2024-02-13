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
                container.start()

                # log_data = {"event": "create_container", "container_id": container.id, "hostname": hostname}
                # logging.info(json.dumps(log_data))

            print("Containers created successfully.")
        except docker.errors.APIError as e:
            print(f"Error creating cluster: {e}")

    def _create_container(self, hostname,name=None):
        container = self.client.containers.run('tensorflow/tensorflow', command='sh',detach=True,stdin_open=True,tty=True, hostname=hostname, name=name)
        return container

##########* list
    def list_all_containers(self):
        try:
            print(f"There are {len(self.containers)} containers in the cluster.")
            for container in self.containers:
                self._print_container_info(container["id"])
        except docker.errors.APIError as e:
            print(f"Error listing cluster: {e}")

    def _print_container_info(self, id_or_name):
        container = self.client.containers.get(id_or_name)
        print(f"Cluster: {self.cluster_name}, Container ID: {container.id}, Name: {container.name}, Status: {container.status}, Hostname: {container.attrs['Config']['Hostname']}")

    def list_running_containers(self):
        try:
            running_containers = self.client.containers.list(filters={'status': 'running'})
            print(f"There are {len(running_containers)} running containers in the cluster.")
            for container in running_containers:
                self._print_container_info(container.id)
        except docker.errors.APIError as e:
            print(f"Error listing running containers: {e}")

    def list_stopped_containers(self):
        try:
            stopped_containers = self.client.containers.list(all=True, filters={'status': 'paused'})
            print(f"There are {len(stopped_containers)} stopped containers in the cluster.")
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

    def _execute_command_in_container(self, container_id, command):
        container = self.client.containers.get(container_id)

        # 检查容器状态，如果不是运行状态，则尝试启动容器
        if container.status != "running":
            print(f"Container {container_id} is not running. Trying to start it.")
            try:
                container.start()
                print(f"Container {container_id} started successfully.")
            except docker.errors.APIError as e:
                print(f"Error starting container {container_id}: {e}")
                return

        # 确保容器现在处于运行状态后执行命令
        exec_id = container.exec_run(command)
        print(f"Command output for Container {container_id}:\n {exec_id.output.decode()}")


##########* stop
    def stop_all_containers(self):
        try:
            for container in self.containers:
                self._stop_container(container["id"])
                log_data = {"event": "stop_container", "container_id": container['id']}
                logging.info(json.dumps(log_data))

            print("Cluster stopped successfully.")
        except docker.errors.APIError as e:
            print(f"Error stopping cluster: {e}")

        self.containers = []

    def _stop_container(self, container_id):
        container = self.client.containers.get(container_id)
        container.stop()
        print(f"Container {container_id} stopped successfully.")

##########* delete
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

    def _delete_container(self, container_id):
        container = self.client.containers.get(container_id)
        container.remove()
        self.containers = [container for container in self.containers if container["id"] != container_id]
        print(f"Container {container_id} deleted successfully.")


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
        print("\n----------Options----------")
        print("1. Create containers")
        print("2. Get/List containers' info")
        print("3. Run Command in Cluster")
        print("4. Stop Containers")
        print("5. Delete Containers")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        try:
            if choice == '1':
                print("\n----------your choice is \"1. Create containers\"----------")
                num = input("Enter the number of containers to create (default=8): ")
                num = int(num) if num else 8
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
                print("\n----------your choice is \"2. Get/List containers' info\"----------")
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
                        container_idorname = input("Enter the name/id of the container completely: ")
                        cluster_manager._print_container_info(container_idorname)
                        break
                    else:
                        print("Invalid input")
                        continue
            elif choice == '3':
                print("----------Your choice is \"3. Run Command in Cluster\"----------")
                choice3 = input("Enter the command to run in the cluster: ")
                cluster_manager.run_command_in_cluster(choice3)
            elif choice == '4':
                print("----------Your choice is \"4. Stop Containers\"----------")
                while(True):
                    choice4 = input("1. Stop all containers\n2. Stop one designated container\nEnter your choice (1-2): ")
                    if choice4 == '1':
                        cluster_manager.stop_all_containers()
                        break
                    elif choice4 == '2':
                        container_idorname = input("Enter the name/id of the container completely: ")
                        cluster_manager._stop_container(container_idorname)
                        break
                    else:
                        print("Invalid input")
                        continue
            elif choice == '5':
                print("----------Your choice is \"5. Delete Containers\"----------")
                while(True):
                    choice5 = input("1. Delete all containers\n2. Delete one designated container\nEnter your choice (1-2): ")
                    if choice5 == '1':
                        cluster_manager.delete_all_containers()
                        break
                    elif choice5 == '2':
                        container_idorname = input("Enter the name/id of the container completely: ")
                        cluster_manager._delete_container(container_idorname)
                        break
                    else:
                        print("Invalid input")
                        continue
            elif choice == '6':
                choice6 = input("Before exiting, the cluster will stop and delete all containers. Do you want to continue? (y/n): ")
                if choice6 == 'y':
                    cluster_manager.stop_all_containers()
                    cluster_manager.delete_all_containers()
                    print("Exiting Cluster Manager. Goodbye!")
                    break
                else:
                    continue
            else:
                print("Invalid choice. Please enter a number between 1 and 6.")
        except KeyboardInterrupt:
            print("\nOperation aborted by the user.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

