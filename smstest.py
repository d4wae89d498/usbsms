from pwn import *
import time

context.log_level = "info"

SERIAL_DEV = "/dev/serial/by-id/usb-MediaTek_Inc_Product-if01"
BAUDRATE   = 9600
TIMEOUT    = 0.2

CTRL_Z = b'\x1a'  # ASCII 26

def read_from_gsm(io):
    data = b""
    while True:
        try:
            chunk = io.recv(timeout=TIMEOUT)
            if not chunk:
                break
            data += chunk
        except EOFError:
            break
    return data

def main():
    io = serialtube(
        SERIAL_DEV,
        baudrate=BAUDRATE,
        timeout=TIMEOUT
    )

    time.sleep(0.5)

    # === Step 1: AT+CMGS ===
    commandStringGSM = 'AT+CMGS="+336xxxxxxxx"\r'
    io.send(commandStringGSM.encode())

    time.sleep(0.05)
    response = read_from_gsm(io)
    print(response.decode(errors="ignore"))

    time.sleep(0.5)

    # === Step 2: Message + CTRL+Z ===
    message = "New Test4 from BLE2!"
    io.send(message.encode() + CTRL_Z)

    time.sleep(0.05)
    response = read_from_gsm(io)
    print(response.decode(errors="ignore"))

    print()

    io.close()

if __name__ == "__main__":
    main()
