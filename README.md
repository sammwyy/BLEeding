# 🩸 BLEeding

BLEeding is a tool that allows you to jam Bluetooth and BLE devices. It can be used to spam DeAuth requests or L2CAP ping requests. It supports Linux, macOS, Windows and Raspberry PI.

This tool was created for educational purposes only. I do not take any responsibility for the misuse of this tool.

## 📦 Installing dependencies

**🐧 Linux / 🍇 Raspberry PI**

```bash
# Install dependencies.
sudo apt-get install git pkg-config python pip libbluetooth-dev libboost-python-dev libboost-thread-dev libglib2.0-dev
```

**🍎 macOS**

```bash
# Install dependencies.
brew install bluez
```

**🟦 Windows**

```bash
# Install dependencies.
choco install git python3
```

## 💻 Setup

```bash
# Clone the repository.
git clone https://github.com/sammwyy/bleeding

# Go to the repository.
cd bleeding

# Install the requirements.
pip install -r requirements.txt
```

> Note: In order to use BLE in Linux, you must install "gattlib" python module. You can install it using the following command: `pip install gattlib`.

## 📚 Usage

```bash
python bleeding.py <options> COMMAND

# Or make it executable
chmod +x bleeding.py
./bleeding.py <options> COMMAND
```

| Command | Description | Options | OS Support |
| ------- | ----------- | ------- | ------- |
| `scan` | Scan for devices. | `ble` | 🐧 🍎 🟦 🍇 |
| `i` | **Interactive mode**: Scan → Select device → Enum services → Select service → DeAuth (60s) | | 🐧 🍎 🟦 🍇 |
| `random-mac` | Generate random trusted MAC addresses | | 🐧 🍎 🟦 🍇 |
| `enum <TARGET>` | Enum device services | | 🐧 🍎 🟦 🍇 |
| `deauth <TARGET>` | Spam DeAuth requests | `port`, `protocol`, `size`, `threads` | 🐧 🍇 🟦 |

| Option | Short | Description | type | Default |
| ------ | ----- | ----------- | :--: | :-----: |
| `--ble` | `-b` | Use BLE instead of Bluetooth. | bool | ❌ |
| `--port` | `-p` | Port to use. | int | 4097 |
| `--protocol` | `-P` | Protocol to use. | **enum:** l2cap, rfcomm | l2cap |
| `--size` | `-s` | Size of the packets. | int | 512 |
| `--threads` | `-t` | Number of threads. |  int | (vcore count) |

> Note: All flags are optional. Windows doesn't support L2CAP protocol.

### 🎮 Interactive Mode

The interactive mode (`i` command) provides a user-friendly TUI workflow:

1. **Scan** - Automatically scans for nearby Bluetooth devices (5s)
2. **Select Device** - Choose a device from the numbered list
3. **Enumerate Services** - Automatically enumerates all services on the selected device
4. **Select Service** - Choose a service/port to attack
5. **Attack** - Automatically launches a 60-second DeAuth attack

**Example:**
```bash
python bleeding.py i

# The tool will guide you through each step interactively
# Just enter the numbers to make your selections
```

## 🤝 Contributing

Contributions, issues and feature requests are welcome!
Feel free to check [issues page](https://github.com/sammwyy/bleeding/issues).

## ❤️ Show your support

Give a ⭐️ if this project helped you! Or buy me a coffee-latte 🙌 [Ko-fi](https://ko-fi.com/sammwy)

## 📝 License

Copyright © 2025 [Sammwy](https://github.com/sammwyy).
This project is [MIT](LICENSE) licensed.
