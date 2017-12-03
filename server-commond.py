#!/usr/bin/env python
# coding:utf-8
import time,threading,socket,struct,os
import os.path
class ThreadedClient():  
    def __init__(self):
#self.running为true表示线程可运行
        self.running=True
#开始线程1，用来accept客户端的连接  
        self.thread1=threading.Thread(target=self.workerThread1)  
        self.thread1.daemon=True
        self.thread1.start()
        self.thread1.join() 
        self.sk_list=[]
        self.all_file_flag=0  
#线程1要干的事情：accept()
    def workerThread1(self):  
        while self.running==True:
            time.sleep(0.0001)
            try:
                conn, addr = sk.accept()
#如果接收到了新的客户端连接，则开一个线程2
                self.sk_list.append(conn)
                name = str(conn.recv(1024),encoding="utf8")
                thread=threading.Thread(target=self.workerThread2,args=(conn, addr, name))
                thread.daemon=True
                thread.start()
            except:
                pass
#线程2要干的事情，接收客户端的数据，并按要求发回
    def workerThread2(self,conn,addr,name):
        while self.running==True:
            time.sleep(0.0001)
            print(str(addr[0])+"@"+str(addr[1])+" "+name+" 建立连接\n")
            file_flag=0
            while True:
                if file_flag==0:
                    accept_data = conn.recv(1024)
                    if file_flag==0:
                        accept_strdata = str(accept_data,encoding="utf8")
                    #print("".join(["接收内容：", accept_data, "     客户端口：", str(addr[1])]))
                    if accept_strdata == "quit" and file_flag==0:  # 如果接收到“quit”则跳出循环结束和第一个客户端的通讯，开始与下一个客户端进行通讯
                        conn.close()
                        self.sk_list.remove(conn)
                        print(str(addr[0])+"@"+str(addr[1])+" "+name+" 断开连接"+"\n")
                        return
                    elif accept_strdata=="file" or file_flag==1:
                        if file_flag==0:
                            file_flag=1
                            self.all_file_flag=1
                            for c in self.sk_list:
                                if c!=conn:
                                    c.sendall(bytes(accept_strdata, encoding="utf8"))
                        fileinfo_size=struct.calcsize('128sl') 
                        buf = conn.recv(fileinfo_size)
                        for c in self.sk_list:
                            if c!=conn:
                                c.send(buf)
                        if buf: #如果不加这个if，第一个文件传输完成后会自动走到下一句
                            filename,filesize =struct.unpack('128sl',buf) 
                            recvd_size = 0 #定义接收了的文件大小
                            while not recvd_size == filesize:
                                if filesize - recvd_size > 1024:
                                    rdata = conn.recv(1024)
                                    recvd_size += len(rdata)
                                    for c in self.sk_list:
                                        if c!=conn:
                                            c.send(rdata)
                                else:
                                    rdata = conn.recv(filesize - recvd_size) 
                                    recvd_size = filesize
                                    for c in self.sk_list:
                                        if c!=conn:
                                            c.send(rdata)
                            file_flag=0
                            self.all_file_flag=0
                            #connection.close()
                    elif file_flag==0 and self.all_file_flag==0: #当前通道没有传送文件
                        for c in self.sk_list:
                            if c!=conn:
                                c.sendall(bytes(accept_strdata, encoding="utf8"))
                    elif file_flag==0 and self.all_file_flag==1:  #当前通道有其他用户在传送文件，阻塞
                        conn.sendall(bytes("当前通道正在传送文件，请稍后再试", encoding="utf8"))
            conn.close()  # 跳出循环时结束通讯
            self.sk_list.remove(conn)
            print(str(addr[0])+"@"+str(addr[1])+" "+name+" 断开连接\n")
#线程终止时尝试关闭套接字
        if self.running==False:
            try:
                conn.sendall(bytes("quit", encoding="utf8"))
                conn.close()
            except:
                pass
sk = socket.socket()
j=str(input("输入本机网卡绑定的地址(推荐在ssh中输入ifconfig查看，非本地调试勿输入127.0.0.1):"))
i=int(input("输入端口:"))
if i>=0 and i<=65535:
    try:
        sk.bind((j, i))
        sk.listen(5)
        print("服务器开启成功,端口:"+str(i)+"\n")
        client=ThreadedClient()
    except socket.error:
        print("服务器开启失败，退出\n")
    else:
        print("端口输入错误，退出\n")
  