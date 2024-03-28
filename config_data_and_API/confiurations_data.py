import paramiko
import time
import schedule
import datetime
import json
from sys import argv
def read_devices_from_file(filename):
    with open(filename, 'r') as file:
        #print(json.load(file))
        devices= json.load(file)
        return devices

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
        return (False, error_message)

def save_config_to_file(device_name, output, success=True, error_message=""):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    status = "Success" if success else "Failure"
    filename = f'{device_name}_config_{timestamp}.txt'
    with open(filename, 'w') as file:
        file.write(output)
        if not success:
            file.writelines("Device  Not responding")
            file.write(f"\n\n{status}: {error_message}")
    print(f'Configuration saved for {device_name} in {filename}')

def run_daily_tasks(config):
    print('CONFIG',config)
    devices = read_devices_from_file('device.json')
    commands = ['terminal length 0', 'show configuration']
    for device in devices:
        output_or_error = connect_ssh(device['hostname'], device['username'], device['password'], commands)
        if output_or_error[0]:
            output = output_or_error
            save_config_to_file(device['hostname'], output)
        else:
            _, error_message = output_or_error
            save_config_to_file(device['hostname'], "", success=False, error_message=error_message)
schedule.every(2).minutes.at(":02").do(run_daily_tasks())
print('schedular part')
while True:
        schedule.run_pending()
        time.sleep(1)
# try:
#     config = {i.split('=')[0]:i.split('=')[1].upper() for i in argv[1].split('#') if i!=''}
#     print('##########',config)
#     run_daily_tasks(config)
#     print('on demand')
# except:
#     #schedule.every(2).hours.do(run_daily_tasks)
    # schedule.every(2).minutes.at(":02").do(run_daily_tasks())
    # print('schedular part')
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)


