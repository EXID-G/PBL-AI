import argparse
import docker
import logging
import json
import concurrent.futures

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
                self._container_info(container["id"])
        except docker.errors.APIError as e:
            print(f"Error listing cluster: {e}")
        return self.containers

    def _container_info(self, id_or_name):
        container = self.client.containers.get(id_or_name)
        print(f"Cluster: {self.cluster_name}, Container ID: {container.id}, Name: {container.name}, Status: {container.status}, Hostname: {container.attrs['Config']['Hostname']}")
        return container

    def list_running_containers(self):
        try:
            running_containers = self.client.containers.list(filters={'status': 'running'})
            print(f"There are {len(running_containers)} running containers in the cluster.")
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

####### processing data parallel
    def distribute_and_process_data_parallel(self,parallel_num, data, container_idorname_list=None):
        try:
            if (parallel_num > len(self.containers)):
                print(f"Error: parallel_num {parallel_num} is greater than the number of containers {len(self.containers)}")
                return
            chunk_size = len(data) // parallel_num

            if(container_idorname_list):
                container_list = [self.client.containers.get(container_idorname) for container_idorname in container_idorname_list]
            data_chunks = [data[i * chunk_size: (i + 1) * chunk_size] for i in range(parallel_num)]

            # 使用 ThreadPoolExecutor 进行并行执行
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # 将每个容器的任务提交到执行器
                futures = [executor.submit(self._process_data_in_container, container, chunk)
                           for container, chunk in zip(self.containers, data_chunks)]

                # 等待所有任务完成
                concurrent.futures.wait(futures)

        except docker.errors.APIError as e:
            print(f"并行分发和处理数据时出错: {e}")

    def _process_data_in_container(self, container, data_chunk):
        try:
            container_id = container["id"]

            # 将数据块写入共享的数据卷
            self._write_data_to_volume(container_id, data_chunk)

            # 在容器中执行处理数据的命令
            self._execute_command_in_container(container_id, "python process_data.py")

        except docker.errors.APIError as e:
            print(f"在容器 {container_id} 中处理数据时出错: {e}")
