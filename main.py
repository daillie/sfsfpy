import sys
from os import system

from frida import attach, ProcessNotFoundError
from time import sleep

from definitions import *
from hex_calc import *
from scripts import *

steam_client_ready = False
steam_client_base = '0x00000000'


def on_message(message, data):
    if message.get('type') != 'send':
        print("[%s] -> %s" % (message, data))
        return
    print('%s' % message.get('payload'))


def on_steamclient_ready(message, data):
    global steam_client_ready
    if message.get('type') == 'error':
        return

    if message.get('type') == 'send':
        if message.get('payload') == 'ready':
            steam_client_ready = True


def on_steamclient_base_addr(message, data):
    global steam_client_base
    if message.get('type') != 'send':
        print(message)
        return
    steam_client_base = message.get('payload')
    print('steamclient base: %s' % steam_client_base)


def steam_get_ready():
    try:
        session = attach(STEAM_PROC_NAME)
        script = session.create_script("""            
            console.log('steam PID: '+ Process.id);
        """)
        script.load()
        session.detach()
        return True
    except ProcessNotFoundError:
        return False


def steam_client_wait():
    print('check for steamclient memory...')
    while not steam_client_ready:
        check_steam_client_ready()
        if steam_client_ready:
            break
        sleep(0.2)
    print('steamclient export found')


def check_steam_client_ready():
    session = attach(STEAM_PROC_NAME)
    script = session.create_script("""
                var steamclientModule = Process.getModuleByName("%s");                
                send('ready');
        """ % STEAM_CLIENT_MODULE_NAME)
    script.on('message', on_steamclient_ready)
    script.load()
    session.detach()


def wait_for_steam():
    print('check for steam memory...')
    while not steam_get_ready():
        sleep(0.5)
    print('steam process found')


def set_steam_client_base():
    session = attach(STEAM_PROC_NAME)
    script = session.create_script(script_get_module_base(STEAM_CLIENT_MODULE_NAME))
    script.on('message', on_steamclient_base_addr)
    script.load()
    session.detach()


def patch_bytes(addr: str, original_bytes, new_bytes, name: str = None):
    if name is None:
        name = addr
    session = attach(STEAM_PROC_NAME)
    script = session.create_script(script_patch(addr, original_bytes, new_bytes, name))

    script.on('message', on_message)
    script.load()
    session.detach()


def patch_bytes_scan(bytes_pattern, new_bytes, module_name: str, name: str = 'Unknown'):
    session = attach(STEAM_PROC_NAME)
    script = session.create_script(
        script_scan_patch(bytes_pattern, new_bytes, module_name, name)
    )
    script.on('message', on_message)
    script.load()
    session.detach()


def legacy_patch():
    offset = sub_hex(steam_client_base, ORIG_STEAM_CLIENT_ADDRESS)
    # print('[+]\toffset: %s' % offset)
    ctr_address = sum_hex(ORIG_CTR, offset)
    lock_address = sum_hex(ORIG_LOCK, offset)

    print('original:\nctr: %s\tlock: %s' % (ORIG_CTR, ORIG_LOCK))
    print('steam:\nctr: %s\tlock: %s' % (ctr_address, lock_address))

    patch_bytes(ctr_address, ORIG_CTR_BYTES, NEW_CTR_BYTES, 'ctr')
    patch_bytes(lock_address, ORIG_LOCK_BYTES, NEW_LOCK_BYTES, 'lock')


def scan_patch():
    ctr_scan_pattern = ' '.join((x.split('x')[1] for x in ORIG_CTR_BYTES)) + CTR_FILL_BYTES
    lock_scan_pattern = ' '.join((x.split('x')[1] for x in ORIG_LOCK_BYTES)) + LOCK_FILL_BYTES

    patch_bytes_scan(ctr_scan_pattern, NEW_CTR_BYTES, STEAM_CLIENT_MODULE_NAME, 'ctr')
    patch_bytes_scan(lock_scan_pattern, NEW_LOCK_BYTES, STEAM_CLIENT_MODULE_NAME, 'lock')


def main():
    args = sys.argv[1:]
    mode = MODE_SCAN
    if len(args) > 0:
        mode = args[0].upper()
        if mode not in [MODE_SCAN, MODE_LEGACY]:
            print('invalid mode: %s' % mode)
            return

    wait_for_steam()
    steam_client_wait()
    set_steam_client_base()

    system('CLS')
    print('mode: ' + mode)
    if mode == MODE_SCAN:
        scan_patch()
    else:
        legacy_patch()

    sleep(0.2)
    input('press enter to exit...')


if __name__ == '__main__':
    main()
