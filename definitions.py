# -----------------------------------------------------------------
STEAM_PROC_NAME = 'steam.exe'
STEAM_CLIENT_MODULE_NAME = 'steamclient.dll'

ORIG_STEAM_CLIENT_ADDRESS = '0x38000000'
ORIG_CTR = '0x3837743F'
ORIG_LOCK = '0x38377358'

ORIG_CTR_BYTES = ['0x0f', '0x8e', '0xde', '0x01', '0x00', '0x00']
NEW_CTR_BYTES = ['0xE9', '0xDF', '0x01', '0x00']

ORIG_LOCK_BYTES = ['0x7e', '0x45']
NEW_LOCK_BYTES = ['0xEB', '0x45']
# -----------------------------------------------------------------


MODE_SCAN = 'SCAN'
# fills need for more accurate bytes scan ( or not.. just testing )
CTR_FILL_BYTES = ' 8b 40 1c'
LOCK_FILL_BYTES = ' 57 eb 03'
# fills
MODE_LEGACY = 'LEGACY'
