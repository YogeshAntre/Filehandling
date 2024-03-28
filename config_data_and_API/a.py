import paramiko
import time
import schedule
import datetime
import json
import logging
from sys import argv
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_devices_from_file(filename):
    with open(filename, 'r') as file:
        return json.load(file)
    
def extract_hostname(output):
    match = re.search(r'hostname\s+(\S+)', output)
    if match:
        return match.group(1)
    return None

def connect_ssh(hostname, username, password, commands):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=hostname, username=username, password=password, port=22, allow_agent=False, timeout=60)
        shell = client.invoke_shell()
        for command in commands:
            shell.send(command + '\n')
        time.sleep(2)
        output = shell.recv(65535).decode()
        client.close()
        return output
    except Exception as e:
        error_message = f"Connection error: {str(e)}"
        logger.error(error_message)
        return None,error_message
def save_config_to_file(device_name, output, success=True, error_message=""):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    status = "Success" if success else "Failure"
    filename = f'{device_name}_config_{timestamp}.txt'
    with open(filename, 'w') as file:
        file.write(output)
        if not success:
            file.write("\nDevice not responding\n")
            file.write(f"{status}: {error_message}")
    logger.info(f'Configuration saved for {device_name} in {filename}')

# def run_daily_tasks(devices, commands):
#     for device in devices:
#         output,error_message = connect_ssh(device['hostname'], device['username'], device['password'], commands)
#         if output is not None:
#             hostname = extract_hostname(output[1])  # Assuming the hostname command output is in index 1
#             if hostname:
#                 save_config_to_file(hostname, output[1])
#             else:
#                 save_config_to_file(device['hostname'], output[1])
#         else:
            
#             save_config_to_file(device['hostname'], "", success=False, error_message=error_message)


def run_on_demand(device_name, commands):
    print('$$$$$',device_name)
    #devices = [d for d in read_devices_from_file('device.json') if d['hostname'] == device_name['hostname']] #or d['hostname'] == device_name['hostname1']]
    devices = [d for d in read_devices_from_file('device.json') if d['hostname'] == device_name.get('hostname') or d['hostname'] == device_name.get('hostname1')]

    print('111111111111111111',devices)
    if not devices:
        logger.error(f"No device found with hostname '{device_name}'")
        return
    for device in devices:
        output_or_error = connect_ssh(device['hostname'], device['username'], device['password'], commands)
        if output_or_error[0]:
            output = output_or_error
            save_config_to_file(device['hostname'], output)
        else:
            _, error_message = output_or_error
            save_config_to_file(device['hostname'], "", success=False, error_message=error_message)
    
    

try:
        config = {i.split('=')[0]:i.split('=')[1].upper() for i in argv[1].split('#') if i!=''}
        logger.info('Configuration: %s', config)
        print(config)
        commands = ['sh running-config | include hostname','terminal length 0', 'show configuration']
        run_on_demand(config, commands)

except:
        print('Run Scheduler')
        schedule_frequency = 1
        commands = ['sh running-config | include hostname','terminal length 0', 'show configuration']
        schedule.every(schedule_frequency).minutes.at(":00").do(run_daily_tasks, read_devices_from_file('device.json'), commands)
        while True:
            schedule.run_pending()
            time.sleep(1)



