# coding:utf-8

import socket
from multiprocessing.dummy import Pool as ThreadPool
import io
import traceback
import logging


class Server(object):

    SERVER_STRING = b"Server: SimpleHttpd/1.0.0\r\n"

    def __init__(self, host, port, worker_count=4):
        self._host = host
        self._port = port
        self._listen_fd = None
        self._worker_count = worker_count
        self._worker_pool = ThreadPool(worker_count)
        self._logger = logging.getLogger("simple.httpd")
        self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(logging.StreamHandler())

    def run(self):
        self._listen_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listen_fd.bind((self._host, self._port))
        self._listen_fd.listen(self._worker_count)
        while True:
            conn, addr = self._listen_fd.accept()
            self._worker_pool.apply_async(self.accept_request, (conn, addr,))

    def accept_request(self, conn: socket.socket, addr):
        try:
            first_line = self._get_line(conn)
            method, path, http_version = first_line.strip().split()
            if method == "GET":
                code = self.unimplemented(conn)
            if method == "POST":
                code = self.unimplemented(conn)
            else:
                code = self.unimplemented(conn)
            self._logger.info("{}:{} {} {} {} {}".format(addr[0], addr[1], http_version, method, path, code))
            conn.close()
        except Exception as e:
            traceback.print_exc()

    def unimplemented(self, conn: socket.socket):
        html = "<html>"
        html += "<head><title>Method Not Implemented</title></head>"
        html += "<body>HTTP request method not supported</body>"
        html += "</html>"
        html = bytes(html, "utf-8")
        conn.send(b"HTTP/1.0 501 Method Not Implemented\r\n")
        conn.send(self.SERVER_STRING)
        conn.send(b"Content-Type: text/html\r\n")
        conn.send(b"Content-Encoding: utf-8\r\n")
        conn.send(bytes("Content-Length: {}\r\n".format(len(html)), "utf-8"))
        conn.send(b"\r\n")
        conn.send(html)
        return 501

    def _get_line(self, conn: socket.socket, length=1024):
        buf = io.BytesIO()
        i = 0
        while True and i <= length:
            data = conn.recv(1)
            buf.write(data)
            if data == b"\r":
                _next = conn.recv(1, socket.MSG_PEEK)
                if _next == b"\n":
                    buf.write(conn.recv(1))
                else:
                    buf.write(b"\n")
                break
            i += 1
        return buf.getvalue().decode("utf-8")


if __name__ == "__main__":
    server = Server("0.0.0.0", 3000)
    server.run()
