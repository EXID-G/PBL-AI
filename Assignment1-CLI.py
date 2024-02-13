from ClusterManager import ClusterManager

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
                        cluster_manager._container_info(container_idorname)
                        break
                    else:
                        print("Invalid input")
                        continue
            elif choice == '3':
                print("----------Your choice is \"3. Run Command in Cluster\"----------")
                while(True):
                    choice3 = input("1. Run the same command in all containers\n2. Run command in one designated container\nEnter your choice (1-2): ")
                    if choice3 == '1':
                        while(True):
                            command = input("Enter the command to run in the cluster (input \"q\" can quit): ")
                            if command == "q":
                                break
                            cluster_manager.run_command_in_cluster(command)
                        break
                    elif choice3 == '2':
                        container_idorname = input("Enter the name/id of the container completely: ")
                        while(True):
                            command = input(f"Enter the command to run in the container {container_idorname} (input \"q\" can quit): ")
                            if command == "q":
                                break
                            cluster_manager._execute_command_in_container(container_idorname, command)
                        break
                    else:
                        print("Invalid input")
                        continue
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
                cluster_manager.list_running_containers()
                choice6 = input("Before exiting, the cluster will stop and delete all running containers. Do you want to continue? (y/n): ")
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

