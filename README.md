# 🩸 BLEeding

BLEeding is a tool that allows you to jam Bluetooth (BR/EDR) and BLE devices. It can be used to spam DeAuth requests or L2CAP ping requests. It supports Linux, macOS, Windows and Raspberry PI.

**Key Features:**
- 🔵 **Dual Mode Support**: Works with both classic Bluetooth (BR/EDR) and Bluetooth Low Energy (BLE)
- 🎯 **Modular Architecture**: Separate implementations for BLE (`bleak`) and BR/EDR (`pybluez`)
- 🚀 **Multi-threaded**: Supports concurrent attacks for maximum impact
- 🖥️ **Interactive Mode**: User-friendly TUI for device discovery and attacks
- 🔄 **Cross-Platform**: Works on Linux, macOS, Windows, and Raspberry Pi

This tool was created for educational purposes only. I do not take any responsibility for the misuse of this tool.

## 📦 Installing dependencies

**🐧 Linux / 🍇 Raspberry PI**

```bash
# Install system dependencies for BR/EDR support
sudo apt-get install git pkg-config python3 python3-pip libbluetooth-dev libboost-python-dev libboost-thread-dev libglib2.0-dev

# BLE support uses bleak (installed via pip, no extra system dependencies needed)
```

**🍎 macOS**

```bash
# Install dependencies (BLE works out of the box via bleak)
brew install bluez
```

**🟦 Windows**

```bash
# Install dependencies (BLE works out of the box via bleak)
choco install git python3
```

## 💻 Setup

```bash
# Clone the repository.
git clone https://github.com/sammwyy/bleeding

# Go to the repository.
cd bleeding

# Install Python requirements.
pip install -r requirements.txt
```

> **Note**: The tool now uses `bleak` for BLE support (cross-platform) and `pybluez` for BR/EDR support. Both are installed via requirements.txt.

## 📚 Usage

```bash
python bleeding.py <options> COMMAND

# Or make it executable
chmod +x bleeding.py
./bleeding.py <options> COMMAND
```

| Command | Description | Options | OS Support |
| ------- | ----------- | ------- | ------- |
| `scan` | Scan for devices. | `--ble` | 🐧 🍎 🟦 🍇 |
| `enum <TARGET>` | Enumerate device services | `--ble` | 🐧 🍎 🟦 🍇 |
| `deauth <TARGET>` | Spam DeAuth/flood requests | `--ble`, `--port`, `--protocol`, `--size`, `--threads`, `--timeout` | 🐧 🍇 🟦 |
| `i` | **Interactive mode**: Scan → Select → Enum → Attack | `--ble` | 🐧 🍎 🟦 🍇 |
| `random-mac` | Generate random trusted MAC addresses | | 🐧 🍎 🟦 🍇 |

### Command Options

| Option | Short | Description | Type | Default | Applies To |
| ------ | ----- | ----------- | :--: | :-----: | :--------: |
| `--ble` | `-b` | Use BLE mode instead of BR/EDR | bool | ❌ | All commands |
| `--port` | `-p` | Port to use (BR/EDR only) | int | 4097 | deauth |
| `--protocol` | `-P` | Protocol: l2cap or rfcomm (BR/EDR only) | enum | l2cap | deauth |
| `--size` | `-s` | Size of the packets | int | 512 | deauth |
| `--threads` | `-t` | Number of threads |  int | (vcore count) | deauth |
| `--timeout` | `-T` | Attack duration in seconds | int | none | deauth |

> **Notes**: 
> - All flags are optional
> - Windows doesn't support L2CAP protocol for BR/EDR attacks
> - BLE mode uses GATT characteristic flooding
> - BR/EDR mode uses socket flooding (L2CAP or RFCOMM)

### 🎮 Interactive Mode

The interactive mode (`i` command) provides a user-friendly TUI workflow:

1. **Scan** - Automatically scans for nearby devices (5s)
2. **Select Device** - Choose a device from the numbered list
3. **Enumerate Services** - Automatically enumerates all services on the selected device
4. **Select Service** - Choose a service/port to attack
5. **Attack** - Automatically launches a 60-second DeAuth attack

**Examples:**

```bash
# Interactive mode for BR/EDR (classic Bluetooth)
python bleeding.py i

# Interactive mode for BLE
python bleeding.py i --ble
```

### 📡 Usage Examples

**Scanning:**
```bash
# Scan for BR/EDR devices
python bleeding.py scan

# Scan for BLE devices
python bleeding.py scan --ble
```

**Enumerate Services:**
```bash
# Enumerate BR/EDR device services
python bleeding.py enum AA:BB:CC:DD:EE:FF

# Enumerate BLE device services (GATT)
python bleeding.py enum AA:BB:CC:DD:EE:FF --ble
```

**DeAuth/Flood Attack:**
```bash
# Attack BR/EDR device with L2CAP
python bleeding.py deauth AA:BB:CC:DD:EE:FF --port 4097 --protocol l2cap --threads 4

# Attack BLE device (60 second duration)
python bleeding.py deauth AA:BB:CC:DD:EE:FF --ble --threads 4 --timeout 60
```

## 🤝 Contributing

Contributions, issues and feature requests are welcome!
Feel free to check [issues page](https://github.com/sammwyy/bleeding/issues).

## ❤️ Show your support

Give a ⭐️ if this project helped you! Or buy me a coffee-latte 🙌 [Ko-fi](https://ko-fi.com/sammwy)

## 📝 License

Copyright © 2025 [Sammwy](https://github.com/sammwyy).
This project is [MIT](LICENSE) licensed.
