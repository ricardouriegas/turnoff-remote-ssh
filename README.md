# Turnoff Manager Using SSH
This project is a turnoff manager using SSH. With this i mean that with the application you can manage `x` amount of devices (specially UNIX based systems) via SSH.

## Requirements
- Python 3.6 or higher
- Paramiko
- Streamlit

## Installation
1. Clone the repository
```bash
git clone https://github.com/ricardouriegas/turnoff-remote-ssh.git
```
2. Install the requirements
```bash
pip install streamlit paramiko
```
3. Run the application in the manager PC
```bash
python3 -m streamlit run main.py
```
4. Run the bash script in the device to be managed
```bash
sudo bash setup-remote.sh
```

## How is it working?
The app works using SSH to connect to the device, then it tries different commands to turn off the device.


> ADVICE: This is a school project, not tested in Windows only in UNIX based systems.
