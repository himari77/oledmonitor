import socket
import time
from mss import mss
from PIL import Image

def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # koneksi dummy ke IP publik, tidak benar-benar kirim paket
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]  # ini akan jadi IP privat LAN PC
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

SERVER_IP = get_lan_ip()
SERVER_PORT = 8888
CHUNK_SIZE = 64
FPS_DELAY = 0.001  # ~30 FPS
print("Server akan bind ke IP LAN:", SERVER_IP)

def linear_to_page(linear):
    pagebuf = bytearray(1024)
    for page in range(8):
        for x in range(128):
            b = 0
            for bit in range(8):
                y = page*8 + bit
                idx = y*128 + x
                if linear[idx]:
                    b |= (1 << bit)
            pagebuf[page*128 + x] = b
    return bytes(pagebuf)

def send_frame(sock, frame):
    try:
        for i in range(0, 1024, CHUNK_SIZE):
            sock.send(frame[i:i+CHUNK_SIZE])
        return True
    except (BlockingIOError, BrokenPipeError, OSError):
        return False

with mss() as sct:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((SERVER_IP, SERVER_PORT))
    sock.listen(1)
    sock.setblocking(True)  # non-blocking listen

    client = None
    last_frame = None

    while True:
        # cek client baru
        if client is None:
            try:
                client, addr = sock.accept()
                print("ESP connected from", addr)
                client.setblocking(False)
            except BlockingIOError:
                pass  # tidak ada client baru

        # ambil screen capture
        scr = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", scr.size, scr.rgb)
        img = img.resize((128,64)).convert("1")
        pixels = list(img.getdata())
        frame = linear_to_page(pixels)
        last_frame = frame

        # kirim frame kalau ada client
        if client:
            if not send_frame(client, frame):
                print("ESP disconnected, closing client")
                try: client.close()
                except: pass
                client = None

        time.sleep(FPS_DELAY)
