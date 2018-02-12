import struct
import io
import sys
import socket
import pygame
from PIL import Image
BLACK = 0, 0, 0
from multiprocessing.pool import ThreadPool


class Server(object):
    def __init__(self, ip, port):
        self.client_connected = False
        self.pool = ThreadPool(processes=1)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.sock.listen(1)
        print('Listening at', self.sock.getsockname())
        print('Client should connect to {}'
              .format(socket.gethostbyname(socket.gethostname())))
        self.image_stream = io.BytesIO()

        self.async_connection = self.pool.apply_async(self.client_connection)

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('Shutting down server')
        if self.client_connected:
            self.conn.close()
        self.sock.close()
        sys.exit()

    def client_connection(self):
        self.conn = self.sock.accept()[0].makefile('rb')
        self.client_connected = True

    def __enter__(self):
        return self

    def img_stream(self):
        self.image_stream.seek(0)
        image_len = \
            struct.unpack('<L', self.conn.read(struct.calcsize('<L')))[0]
        if not image_len:
            raise ConnectionError('Image length is None')
        self.image_stream.write(self.conn.read(image_len))
        return self.image_stream


class Screen(object):
    def __init__(self, screen_size, fullscreen=False):
        self.screen_size = screen_size
        pygame.init()
        pygame.display.set_caption('eduROV')
        if fullscreen:
            fullscreen = pygame.FULLSCREEN
        self.screen = pygame.display.set_mode(screen_size, fullscreen)
        self.fullscreen = fullscreen

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def update(self, frame=None):
        self.read_keys()
        if frame:
            self.screen.blit(frame, (0,0))
        else:
            self.screen.fill(BLACK)
        pygame.display.flip()

    def read_keys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()
                if event.key == pygame.K_RETURN:
                    self.toggle_fullscreen()

    def quit(self):
        sys.exit()

    def toggle_fullscreen(self):
        if self.fullscreen:
            self.fullscreen = False
        else:
            self.fullscreen = pygame.FULLSCREEN
        pygame.display.set_mode(self.screen_size, self.fullscreen)


def server(ip, port, resolution, fullscreen):
    screen_size = tuple([int(val) for val in resolution.split('x')])
    screen = Screen(screen_size=screen_size, fullscreen=fullscreen)

    with Server(ip, port) as server:
        while True:
            if server.client_connected:
                pil_frame = Image.open(server.img_stream()).tobytes()
                frame = pygame.image.fromstring(pil_frame, screen_size, 'RGB')
                screen.update(frame)
            else:
                screen.update()
