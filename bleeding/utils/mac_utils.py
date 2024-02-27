import random

MAC_MIN = 0x00
MAC_MAX = 0xff

VENDORS_OUI = {
    "acer": "C0:98:79",
    "apple": "FC:FC:48",
    "asus": "FC:C2:33",
    "dell": "D8:D0:90",
    "google": "F8:8F:CA",
    "hp": "B0:5C:DA",
    "htc": "98:0D:2E",
    "intel": "FC:F8:AE",
    "lenovo": "A4:8C:DB",
    "lg": "F8:A9:D0",
    "microsoft": "C4:9D:ED",
    "motorola": "F8:F1:B6",
    "samsung": "FC:F1:36",
    "sony": "D4:38:9C",
    "toshiba": "EC:21:E5",
    "xiaomi": "FC:64:BA",
}

def random_mac_head():
    # Generate first 3 bytes.
    vendor = random.choice(list(VENDORS_OUI.values()))
    return vendor
    
def random_mac_tail():
    # Generate last 3 bytes.
    last_bytes = [random.randint(MAC_MIN, MAC_MAX) for _ in range(3)]
    
    # Set the 2nd least significant bit to 1 (locally administered).
    return ':'.join(map(lambda x: format(x, '02x'), last_bytes))

def random_mac():
    return random_mac_head() + ":" + random_mac_tail()

def random_mac_all_vendors():
    vendors = list(VENDORS_OUI.keys())
    macs = []
    
    for vendor in vendors:
        head = VENDORS_OUI[vendor]
        tail = random_mac_tail()
        mac = head + ":" + tail
        macs.append([vendor, mac])
        
    return macs