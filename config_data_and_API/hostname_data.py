import paramiko
import time
import schedule
import datetime
import json
import re
import logging
from sys import argv
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_devices_from_file(filename):
    with open(filename, "r") as file:
        devices = json.load(file)
    return devices


def connect_ssh(hostname, username, password, commands, port=22):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=hostname,
            username=username,
            password=password,
            port=port,
            allow_agent=False,
            timeout=60,
        )
        shell = client.invoke_shell()
        outputs = []
        for command in commands:
            shell.send(command + "\n")
            time.sleep(2)
            output = shell.recv(65535).decode()
            outputs.append(output)
        client.close()
        return outputs, None
    except Exception as e:
        error_message = f"Connection error: {str(e)}"
        #logger.error(error_message)
        return None, error_message


def extract_hostname(output):
    match = re.search(r"hostname\s+(\S+)", output)
    if match:
        return match.group(1)
    return None


def save_config_to_file(device_name, output, success=True, error_message=""):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    status = "Success" if success else "Failure"
    filename = f"{device_name}_config_{timestamp}.txt"
    with open(filename, "w") as file:
        file.write(output)
        if not success:
            file.write("Device is not responding\n")
            file.write(f"{status}: {error_message}\n")
    print(f"Configuration saved for {device_name} in {filename}")
    logger.info(f"Configuration saved for {device_name} in {filename}")


def run_daily_tasks(devices, commands):
    # devices = read_devices_from_file('device.json')
    # commands = ['terminal length 0', 'show running-config']
    for device in devices:
        outputs, error_message = connect_ssh(
            device["hostname"], device["username"], device["password"], commands
        )
        if outputs is not None:
            hostname = extract_hostname(
                outputs[1]
            )  # Assuming the hostname command output is in index 1
            if hostname:
                save_config_to_file(hostname, outputs[1])
            else:
                save_config_to_file(device["hostname"], outputs[1])
        else:
            save_config_to_file(
                device["hostname"], "", success=False, error_message=error_message
            )


def run_on_demand(device_name, commands,port=None):
    #print('device_name',device_name.get('port'))
    
    # device_name = read_devices_from_file('device.json')
    # commands = ['terminal length 0', 'show running-config']
    # devices = [d for d in read_devices_from_file('device.json') if d['hostname'] == device_name['hostname']] #or d['hostname'] == device_name['hostname1']]
    devices = [
        d
        for d in read_devices_from_file("device.json")
        if d["hostname"] == device_name.get("host1")
        or d["hostname"] == device_name.get("host2")
    ]
    # print('111111111111111111',devices)
    adata=device_name.get('port')

    port= int (adata) if adata is not None else 22
    #print("PORT", port)
    if not devices:
        logger.error(f"No device found with hostname '{device_name}'")
        # error_message = f"No device found with hostname '{device_name}'"
        # for device_name['hostname'] in [device_name['hostname'],device_name['hostname1']]:
        #     save_config_to_file(device_name['hostname'], "", success=False, error_message=error_message)
        # return
        return
    #print("PORT", port)
    for device in devices:
        outputs, error_message = connect_ssh(
            device["hostname"],
            device["username"],
            device["password"],
            commands,
            port=port,
        )
        if outputs is not None:
            hostname = extract_hostname(outputs[1])
            if hostname:
                save_config_to_file(hostname, outputs[1])
            else:
                save_config_to_file(device["hostname"], outputs[1])
                logger.error(error_message)
        else:
            logger.error(error_message)
            # save_config_to_file(
            #     device["hostname"], "", success=False, error_message=error_message
            # )


try:
    print("On Demand CPE configurations")
    config = {
        i.split("=")[0]: i.split("=")[1].upper() for i in argv[1].split("#") if i != ""
    }
    logger.info("Configuration: %s", config)
   # print(config)
    commands = ["terminal length 0", "show configuration"]
    run_on_demand(device_name=config, commands=commands)

except:
    print("Run Scheduler")
    schedule_frequency = 1
    commands = ["terminal length 0", "show configuration"]
    schedule.every(schedule_frequency).minutes.at(":00").do(
        run_daily_tasks, read_devices_from_file("device.json"), commands
    )
    while True:
        schedule.run_pending()
        time.sleep(1)
