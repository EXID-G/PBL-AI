import docker
client = docker.from_env()

args = client.read_command_line_args()

# ./as1.py create 8 ubuntu
if args[1] == 'create':
    num = int(args[2])
    img = args[3]

    for i in range(num):
        tmp = 'c' + str(i)
        try:
            tmp = client.containers.create(img, 'sh', tty=True, name=tmp)
        except:
            print('Failed creation: ', tmp)


# ./as1.py list 
# to list the containers
if args[1] == 'list':
    client.containers.list()


# ./as1.py start 8
try: 
    client.containers.run()
except:
    print('No images!')

if args[1] == 'start':
    num = int(args[2])
    # img = args[3]
    for i in range(num):
        tmp = 'c' + str(i)
        try:
            client.containers.run(tmp, 'sh')
        except:
            print('Failed running: ', tmp)


# ./as1.py stop 8
if args[1] == 'stop':            
    num = int(args[2])
    # img = args[3]

    for i in range(num):
        tmp = 'c' + str(i)
        try:
            tmp.stop(timeout=0)
        except:
            print('Failed stopped: ', tmp)


# ./as1.py delete
if args[1] == 'delete':
    try:
        client.containers.prune()            
        client.containers.list()
    except:
        print('Failed deleted.')