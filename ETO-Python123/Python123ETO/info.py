import uuid, socket, datetime, subprocess

print('Locate Time:', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print('Computer UUID:', uuid.getnode())
print('SMBIOS UUID:', subprocess.check_output("wmic bios get serialnumber", shell=True).decode().split("\n")[1].strip())
print('IP Address:', socket.gethostbyname(socket.gethostname()))
print('MAC Address:', ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 8)][::-1]))
print(f'\033[91m\033[1m该访问行为已记录，请诚信考试！\033[0m')
