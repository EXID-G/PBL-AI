import argparse
import pickle
import docker
import logging
import json
import concurrent.futures

class ClusterManager:
    def __init__(self, cluster_name):
        self.client = docker.from_env()
        self.containers = []    ## record the hostname of each container
        self.cluster_name = cluster_name

        logging.basicConfig(filename=f'logfile/CM_{cluster_name}.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        log_data = {"event": "init_cluster_manager", "cluster_name": cluster_name}
        logging.info(json.dumps(log_data))
        print(f"Cluster Manager (name = {self.cluster_name}) initialized successfully.")

##########* create
    # the programme will allocate hostnames automatically
    def create_containers(self, num_containers=8, name_list=None, volumes=None):
        try:
            for i in range(num_containers):
                hostname = f"{self.cluster_name}-container{i+1}"
                container = self._create_container(hostname = hostname,name = name_list[i] if name_list else None, volumes = volumes)

            print(f"{num_containers} containers created successfully.")
        except docker.errors.APIError as e:
            print(f"Error creating containers: {e}")

    # you can pass hostname by yourself
    def _create_container(self, hostname, name=None, volumes=None):
        container = self.client.containers.run('tensorflow/tensorflow', command='sh',detach=True,stdin_open=True,tty=True, hostname=hostname, name=name, volumes = volumes)
        self.containers.append({"id": container.id, "name": container.name,"hostname": hostname})
        print(f"Containers (id = {container.id}) created successfully.")
        log_data = {"event": "create_container", "container_id": container.id, "hostname": hostname}
        logging.info(json.dumps(log_data))
        return container

##########* list
    def list_all_containers(self):
        try:
            print(f"There are {len(self.containers)} containers in the cluster.")
            for container in self.containers:
                self._container_info(container["id"])
        except docker.errors.APIError as e:
            print(f"Error listing all containers: {e}")
        return self.containers

    def _container_info(self, id_or_name):
        container = self.client.containers.get(id_or_name)
        print(f"Cluster: {self.cluster_name}, Container ID: {container.id}, Name: {container.name}, Status: {container.status}, Hostname: {container.attrs['Config']['Hostname']}")
        return container

    def list_running_containers(self):
        try:
            running_containers = self.client.containers.list(filters={'status': 'running'})
            print(f"\nThere are {len(running_containers)} running containers in the cluster.")
            for container in running_containers:
                self._container_info(container.id)
        except docker.errors.APIError as e:
            print(f"Error listing running containers: {e}")
        return running_containers

    def list_stopped_containers(self):
        try:
            stopped_containers = self.client.containers.list(all=True, filters={'status': 'paused'})
            print(f"There are {len(stopped_containers)} stopped containers in the cluster.")
            for container in stopped_containers:
                self._container_info(container.id)
        except docker.errors.APIError as e:
            print(f"Error listing stopped containers: {e}")
        return stopped_containers

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
            print(f"Container (id = {container_id}) is not running. Trying to start it.")
            try:
                container.start()
                print(f"Container (id = {container_id}) started successfully.")
            except docker.errors.APIError as e:
                print(f"Error starting container {container_id}: {e}")
                return

        # 确保容器现在处于运行状态后执行命令
        exec_id = container.exec_run(command)
        if exec_id.exit_code == 0:
            print(f"Command executed successfully in Container (id  ={container_id}):\n{exec_id.output.decode()}")
        else:
            print(f"Command failed in Container (id  ={container_id}):\n{exec_id.output.decode()}")
        log_data = {
            "event": "run_command_in_container",
            "container_id": container_id,
            "command": command,
            "exit_code": exec_id.exit_code,
            "output": exec_id.output.decode()
        }
        logging.info(json.dumps(log_data))


##########* stop
    def stop_all_containers(self):
        try:
            for container in self.containers:
                self._stop_container(container["id"])

            print("All containers stopped successfully.")
        except docker.errors.APIError as e:
            print(f"Error stopping cluster: {e}")

    def _stop_container(self, container_id):
        container = self.client.containers.get(container_id)
        container.stop()
        print(f"Container (id = {container_id}) stopped successfully.")
        log_data = {"event": "stop_container", "container_id": container_id}
        logging.info(json.dumps(log_data))

##########* delete
    def delete_all_containers(self):
        try:
            for container in self.containers:
                self._delete_container(container["id"])


            print("All containers deleted successfully.")
        except docker.errors.APIError as e:
            print(f"Error deleting containers: {e}")

        self.containers = []

    def _delete_container(self, container_id):
        container = self.client.containers.get(container_id)
        container.remove()
        self.containers = [container for container in self.containers if container["id"] != container_id]
        print(f"Container (id = {container_id}) deleted successfully.")
        log_data = {"event": "delete_container", "container_id": container_id}
        logging.info(json.dumps(log_data))

####### processing data parallel
    def distribute_and_process_data_parallel(self,parallel_num, volume_data_path, process_file_path,container_idorname_list=None):
        try:
            if (parallel_num > len(self.containers)):
                print(f"Error: parallel_num {parallel_num} is greater than the number of containers {len(self.containers)}")
                return
            with open(volume_data_path, 'rb') as file:
                data = pickle.load(file)
            chunk_size = len(data) // parallel_num
            data_chunks_tuple = [(i * chunk_size , (i + 1) * chunk_size) for i in range(parallel_num)]
            # print(data_chunks_tuple)
            if(container_idorname_list):
                container_list = [self.client.containers.get(container_idorname) for container_idorname in container_idorname_list]
            else:
                container_list = [self.client.containers.get(container_idorname["id"]) for container_idorname in self.containers[:parallel_num]]

            # 使用 ThreadPoolExecutor 进行并行执行
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # 将每个容器的任务提交到执行器
                futures = [executor.submit(self._process_data_in_container, container, chunk_index, volume_data_path, process_file_path)
                           for container, chunk_index in zip(container_list, data_chunks_tuple)]

                # 等待所有任务完成
                concurrent.futures.wait(futures)

        except docker.errors.APIError as e:
            print(f"Error distributing and processing data parallel: {e}")

    def _process_data_in_container(self, container, chunk_index, volume_data_path, process_file_path):
        try:
            container_id = container.id

            self._execute_command_in_container(container_id, f"python {process_file_path} {volume_data_path} {chunk_index[0]} {chunk_index[1]}")

        except docker.errors.APIError as e:
            print(f"Error processing data in container {container_id}: {e}")
