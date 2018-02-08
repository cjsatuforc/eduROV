import socket, io, struct, time
import picamera
from ..common.classes import ROVManager


class SplitFrames(object):
    def __init__(self, connection):
        self.connection = connection
        self.stream = io.BytesIO()
        self.count = 0

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # Start of new frame; send the old one's length then the data
            size = self.stream.tell()
            if size > 0:
                self.connection.write(struct.pack('<L', size))
                self.connection.flush()
                self.stream.seek(0)
                self.connection.write(self.stream.read(size))
                self.count += 1
                self.stream.seek(0)
        self.stream.write(buf)


def read_camera(host, port, resolution):
    client_socket = socket.socket()
    client_socket.connect((host, port))
    print('Client has been assigned socket name', client_socket.getsockname())
    connection = client_socket.makefile('wb')
    try:
        output = SplitFrames(connection)
        with picamera.PiCamera(resolution=resolution, framerate=30) as camera:
            time.sleep(2)
            camera.capture('./captures/{}.jpg'.format(resolution))
            start = time.time()
            camera.start_recording(output, format='mjpeg')
            camera.wait_recording(60)
            camera.stop_recording()
            connection.write(struct.pack('<L', 0))  # Tell server we are done
    finally:
        connection.close()
        client_socket.close()
        finish = time.time()
    print('Sent %d images in %d seconds at %.2ffps' % (
        output.count, finish - start, output.count / (finish - start)))


def start_camera(server_ip, port_cam, port_var):
    pass

def rov_main(server_ip, port_cam, port_var):
    print('created server')