import serial
import serial.tools.list_ports
import random
import socket, select, queue, time
import threading
import struct


class Control_Manager(object):
    def __init__(self):
        self.mode = 1 << 0  # (1 << 0) 手动   (1 << 1) 路径巡航   (1 << 2) 视觉跟踪
        self.arg = None    # 最近一次获取的命令参数
        self.A, self.k, self.c = 0, 0, 0
        self.cur_mode = 0
        self.route = None
        self.cur_route = 0
        self.is_route = False
        self.is_bionic = False
        self.recv_false = 0
        self.Servo_serial = None
        self.k210_serial = None
        self.server = None
        self.inputs = []
        self.outputs = []
        self.message_queues = {}
        self.thread = threading.Thread(target=self.Processing_Command)

    def run(self):
        self.thread.start()
        self.Server_Init()

    def Bionic(self):
        time.sleep(random.random() + 1)
        self.Servo_Send(random.randint(2, 5),
                        random.choice([-1, 1])*random.choices([0, 5, 6, 7, 8],
                        weights=[0.3, 0.3, 0.2, 0.1, 0.1])[0], 0)
        time.sleep(random.random() + 1.5)
        self.Servo_Send(0, 0, 0)
        
    def Serial_Recv(self):
        return None

    def Serial_Send(self, text):
        pass

    def Servo_Send(self, a, k, c):
        try:
            for s in self.inputs:
                if s is not self.server:
                    self.message_queues[s].put('(0, ({}, {}, {}))'.format(int(a), int(k), int(c)) + '\n')
                    if s not in self.outputs:
                        self.outputs.append(s)
        except KeyError:
            pass
            
    def Serial_Reset(self, n=18):
        pass
  
    def Serial_Down(self, n=24):
        pass
        
    def Serial_Up(self, n=24):
        pass

    def Server_Init(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(0)
        ip_port = ('127.0.0.1', 3411)
        # ip_port = ('192.168.137.1', 3411)
        self.server.bind(ip_port)
        self.server.listen(5)
        self.inputs.append(self.server)
        while self.inputs:
            # print(len(self.inputs), len(self.outputs))  # 在这里加停止命令 需要把视觉、巡航相关参数也调零
            rs, ws, es = select.select(self.inputs, self.outputs, self.inputs)
            for s in rs:
                if s is self.server:
                    connection, address = s.accept()
                    print('connecting from', address)
                    connection.setblocking(0)
                    self.inputs.append(connection)
                    self.outputs.append(connection)
                    self.message_queues[connection] = queue.Queue()
                else:
                    try:
                        data = s.recv(4096).decode('utf-8')
                    except ConnectionResetError:
                        es.append(s)
                        continue
                    if data != '':
                        print('receive {} from {}'.format(data, s.getpeername()))
                        try:
                            command = eval(data)
                            self.cur_mode, self.arg = command[0], command[1]
                        except Exception:
                            self.cur_mode, self.arg = None, None
                        if self.cur_mode == 1 << 2:  # Camera
                            self.mode |= (1 << 2)
                        elif self.cur_mode == 1 << 1:
                            self.mode |= (1 << 1)
                        elif self.cur_mode == 1 << 0:
                            self.mode |= (1 << 0)
                        elif self.cur_mode == 1 << 8:
                            self.mode |= (1 << 8)
                        # self.message_queues[s].put(data)
                        if s not in self.outputs:
                            self.outputs.append(s)

                    else:
                        print('closing', s.getpeername())
                        if s in self.outputs:
                            self.outputs.remove(s)
                        self.inputs.remove(s)
                        s.close()
                        del self.message_queues[s]
            for s in ws:
                try:
                    message_queue = self.message_queues.get(s)
                    send_data = ''
                    if message_queue is not None:
                        send_data = message_queue.get_nowait()
                except queue.Empty:
                    pass
                else:
                    if send_data:
                        try:
                            s.send(send_data.encode('utf-8'))
                        except ConnectionResetError:
                            es.append(s)
                            continue

            for s in es:
                print('exception condition on', s.getpeername())
                self.inputs.remove(s)
                if s in self.outputs:
                    self.outputs.remove(s)
                s.close()
                del self.message_queues[s]

            time.sleep(0.01)

    def Processing_Command(self):
        while True:
            time.sleep(0.01)
            if self.cur_mode is None:
                if self.sep == 1 << 10:
                    if self.mode == 0 and self.is_bionic:
                        self.mode |= (1 << 8)
                else:
                    self.sep += 1
            else:
                self.sep = 0
                if self.cur_mode != 1 << 8:
                    self.mode &= ~(1 << 8)

            # 视觉命令启动
            if self.mode & (1 << 2):
                if self.cur_mode == 1 << 2:
                    if not self.arg:
                        self.mode &= ~(1 << 2)
                        self.cur_mode, self.arg = None, None
                        continue
                    else:
                        self.cur_mode, self.arg = None, None
                # send request to k210
                self.Serial_Send('hellow')
                temp = self.Serial_Recv()
                if temp:
                    try:
                        data = eval(temp)
                        print(data)
                    except:
                        continue
                else:
                    self.recv_false += 1
                    if self.recv_false == 40:
                        self.recv_false = 0
                        self.Serial_Reset(18)
                    continue
                if isinstance(data, tuple):
                    if self.control_socket and self.message_queues.get(self.control_socket):
                        # self.control_socket.send(str(('position', data)).encode('utf-8'))
                        self.message_queues[self.control_socket].put(str(('position', data))+'\n')
                        self.Servo_Send(5, 0.5)    # 跟踪算法
                        continue

            # 巡航
            if self.mode & (1 << 1):
                if self.cur_mode == 1 << 1:
                    if self.arg is False:
                        self.mode &= ~(1 << 1)
                        self.cur_mode, self.arg, self.is_route = None, None, False
                    elif isinstance(self.arg, list):
                        self.route = self.arg.copy()
                        self.cur_route = 0
                        self.cur_mode, self.arg, self.is_route = None, None, True
                    else:
                        self.cur_mode, self.arg, self.is_route = None, None, True
                if self.is_route:
                    if self.route:
                        if self.cur_route == len(self.route) - 1:
                            self.cur_route = 0
                        A, k = self.route[self.cur_route]
                        self.cur_route += 1
                        print(A, k)
                        self.Servo_Send(A, k, 0)  # 跟踪算法
                        time.sleep(2)
                else:
                    self.Servo_Send(0, 0, 0)
                continue

            # 手动命令 参数 频率和K
            if self.mode & (1 << 0):
                if self.cur_mode == 1 << 0:
                    self.mode ^= (1 << 0)
                    print(self.arg)
                    if self.arg == 'Up_0':
                        self.Serial_Up(24)
                    elif self.arg == 'Down_0':
                        self.Serial_Down(24)
                    elif self.arg == 'Up_1':
                        self.Serial_Up(23)
                    elif self.arg == 'Down_1':
                        self.Serial_Down(23)
                    else:
                        self.A, self.k, self.c = self.arg
                        self.Servo_Send(*self.arg)    # 跟踪算法
                    self.cur_mode, self.arg = None, None
                    continue

            if self.mode & (1 << 8):
                if self.cur_mode == 1 << 8:
                    if self.arg is False:
                        self.mode &= ~(1 << 8)
                        self.is_bionic = False
                        self.cur_mode, self.arg = None, None
                        continue
                    else:
                        self.is_bionic = True
                        self.cur_mode, self.arg = None, None
                self.Bionic()
                continue


if __name__ == '__main__':
    manager = Control_Manager()
    manager.run()
