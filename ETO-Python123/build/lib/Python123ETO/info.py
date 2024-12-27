import uuid, socket, datetime, subprocess
from Python123ETO.send import email_sender

item = {'Locate_Time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Computer_UUID': uuid.getnode(),
        'SMBIOS_UUID': subprocess.check_output("wmic bios get serialnumber", shell=True).decode().split("\n")[1].strip(),
        'IP_Address': socket.gethostbyname(socket.gethostname()),
        'MAC_Address': ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2 * 6, 8)][::-1])}

for i, j in item.items():
    print(f'{i}: {j}''')
email_sender(item)
print(f'\033[91m\033[1m该访问行为已记录，请诚信考试！\033[0m')
