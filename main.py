from pwn import *
import time

context.log_level = "info"

SERIAL_DEV = "/dev/serial/by-id/usb-MediaTek_Inc_Product-if01"
BAUDRATE   = 9600
TIMEOUT    = .2

def send_at(io, cmd, desc):
    log.info(f"\n=== {desc} ===")
    log.info(f">>> {cmd}")

    io.sendline(cmd.encode())

    output = b""

    # Read until modem stops talking
    while True:
        try:
            chunk = io.recv(timeout=TIMEOUT)
            if not chunk:
                break
            output += chunk
        except EOFError:
            break

    decoded = output.decode(errors="ignore").strip()
    if decoded:
        log.info("<<< RESPONSE:")
        print(decoded)
    else:
        log.warning("<<< No response")

    if "ERROR" in decoded:
        log.failure(f"Command failed: {cmd}")
    elif "OK" in decoded:
        log.success("OK")
    else:
        log.warning("No explicit OK/ERROR")

    return decoded


def main():
    io = serialtube(
        SERIAL_DEV,
        baudrate=BAUDRATE,
        timeout=TIMEOUT
    )

    time.sleep(0.5)

    send_at(io, "AT",          "Testing AT protocol")
    send_at(io, "AT+CMEE=2",   "Enable verbose errors")
    send_at(io, "AT+CFUN=1",   "Full functionality")
    send_at(io, "AT+CGMM",     "Get chipset model")
    send_at(io, "AT+CGMR",     "Get firmware version")
    send_at(io, "AT+CSQ",      "Get signal quality")
    send_at(io, "AT+COPS?",    "Get registered operator")

    log.success("All prolog commands sent")

    io.interactive()

    # send_at(io, 'AT+CMGS=06xxxx\x0DTEST SMS\x1A', "Test a SMS")


    io.close()


if __name__ == "__main__":
    main()
