import serial
import serial.tools.list_ports

# -------------查看串口列表---------------#
port_list = list(serial.tools.list_ports.comports())
if len(port_list) == 0:
    print('无可用串口')
else:
    for i in range(0, len(port_list)):
        print(port_list[i])


# --------------打开串口--------------------#

# ser为串口对象，后续调用均用点运算符
ser = serial.Serial('COM7', 9600, 8, 'N', 1)  # 'COM7', 3000000, bytesize=8, parity='N', stopbits=1
flag = ser.is_open

if flag:
    print('success\n')
    # ser.close()
else:
    print('Open Error\n')


# -------------读取数据帧------------------#
print(ser.read(size=1))   # 如果设置了超时，它可能会根据要求返回更少的字符。 没有超时，它将阻塞直到读取请求的字节数。
print(ser.read_until()[:-1].decode('gb2312'))    # 不断读取字节直到遇到指定的字符 默认\n
print(ser.read_all())       # 不断读取直到字节数达到in_waiting
print(ser.readline())       # 读一行, 换行时读取
print(ser.readlines())      # 不断读取直到串口退出

# -------------发送数据帧-------------------#

ser.write('hellow'.encode('utf-8'))  # 发送的数据需要编码

# -------------其他---------------#
print(ser.in_waiting)  # 获取输入缓冲区中的字节数
print(ser.out_waiting)   # 获取输出缓冲区中的字节数
print(ser.rts)           # 查看RTS线路的状态 （请求发送） 可直接设置
print(ser.dtr)           # 查看DTR线路的状态 （数据终端准备好） 可直接设置
print(ser.is_open)       # 查看串口是否打开成功
print(ser.readable())    # 查看是否可读
print(ser.writable())
# port, baudrate, bytesize, parity(校验), stopbits, timeout(读取), write_timeout(写入) 都可查看和设置

