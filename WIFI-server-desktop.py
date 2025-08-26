import socket
import time
from mss import mss
from PIL import Image

SERVER_IP = "MAI AIPI ADRESS"
SERVER_PORT = 8888 # port bebas pokok ra tabrakan
CHUNK_SIZE = 64
FPS_DELAY = 0.01 # gantien sak senengmu wes

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
            sock.sendall(frame[i:i+CHUNK_SIZE])
        return True
    except:
        return False

with mss() as sct:
    while True:
        print("Waiting for ESP01...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((SERVER_IP, SERVER_PORT))
        sock.listen(1)

        client, addr = sock.accept()
        print("ESP connected from", addr)

        try:
            while True:
                scr = sct.grab(sct.monitors[1])
                img = Image.frombytes("RGB", scr.size, scr.rgb)
                img = img.resize((128,64)).convert("1")
                pixels = list(img.getdata())
                frame = linear_to_page(pixels)

                if not send_frame(client, frame):
                    print("Connection lost")
                    client.close()
                    break

                time.sleep(FPS_DELAY)

        except:
            try: client.close()
            except: pass
            print("Connection lost")
