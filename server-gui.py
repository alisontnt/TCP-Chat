import tkinter,time,threading,socket,struct,os
import os.path
from tkinter import messagebox,Label,ttk,Entry,Frame,Text,StringVar,Checkbutton
from tkinter.scrolledtext import ScrolledText
def quit_stop():
    try:
        client.gui.flag=1
        client.running=False
    except:
        pass
    finally:
        root.quit()
class GuiPart():  
    def __init__(self):  
#布局1&标签1&标签1&单行文本框entry1
        self.flag=1
        self.frm1 = Frame(root)
        self.label1 = Label(self.frm1, text="服务器端口")
        self.e1=StringVar()
        self.entry1 = Entry(self.frm1, textvariable=self.e1 ,width=6)
        self.label3 = Label(self.frm1, text="服务器ip地址")
        self.e3=StringVar()
        self.entry3 = Entry(self.frm1, textvariable=self.e3)
        self.buttontext = tkinter.StringVar()
        self.buttontext.set('开启服务器')
        self.button1 = tkinter.Button(self.frm1, textvariable=self.buttontext, command=self.cmd)
        self.label3.pack(side="left")
        self.entry3.pack(side="left")
        self.label1.pack(side="left")
        self.entry1.pack(side="left")
        self.button1.pack(side="left")
        self.frm1.pack()
#布局2&标签2&文本框Text作为状态框
        self.frm2 = Frame(root)
        self.label2 = Label(self.frm2, text="状态框")
        self.text=ScrolledText(self.frm2,width=62,height=15)
        self.text.bind("<KeyPress>",lambda e:"break")
        self.label2.pack(side="top")
        self.text.pack(side="bottom",fill = 'both', expand = True)
        self.frm2.pack()
    def cmd(self):
        i=int(self.entry1.get())
        j=str(self.entry3.get())
        if i>=0 and i<=65535:
            try:
                sk.bind((j, i))
                sk.listen(5)
                self.flag=0
                self.text.insert('end',"服务器开启成功,端口:"+self.entry1.get()+"\n")
                self.text.see(tkinter.END)
            except socket.error:
                self.text.insert('end',"服务器开启失败\n")
                self.text.see(tkinter.END)
        else:
             self.text.insert('end',"端口输入错误\n")
             self.text.see(tkinter.END)
class ThreadedClient():  
    def __init__(self):
#self.gui用来初始化gui    
        self.gui=GuiPart()  
#self.running为true表示线程可运行
        self.running=True
#开始线程1，用来accept客户端的连接  
        self.thread1=threading.Thread(target=self.workerThread1)  
        self.thread1.daemon=True
        self.thread1.start()  
        self.periodicCall()
        self.sk_list=[]
        self.all_file_flag=0  
    def periodicCall(self):  
        root.after(200,self.periodicCall)    
        if not self.running:  
            root.destroy()
#线程1要干的事情：accept()
    def workerThread1(self):  
        while self.running==True:
            time.sleep(0.0001)
#self.gui.flag==0,说明服务已开启
            if self.gui.flag==0:
                try:
                    conn, addr = sk.accept()
#如果接收到了新的客户端连接，则开一个线程2
                    self.sk_list.append(conn)
                    name = str(conn.recv(1024),encoding="utf8")
                    print(name)
                    thread=threading.Thread(target=self.workerThread2,args=(conn, addr, name))
                    thread.daemon=True
                    thread.start()
                except:
                    pass
#线程2要干的事情，接收客户端的数据，并按要求发回
    def workerThread2(self,conn,addr,name):
        while self.running==True:
            time.sleep(0.0001)
            self.gui.text.insert('end',str(addr[0])+"@"+str(addr[1])+" "+name+" 建立连接\n")
            self.gui.text.see(tkinter.END)
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
                        self.gui.text.insert('end',str(addr[0])+"@"+str(addr[1])+" "+name+" 断开连接"+"\n")
                        self.gui.text.see(tkinter.END)
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
                            print ('stat receiving and sending...')
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
                            print ('done')
                            file_flag=0
                            self.all_file_flag=0
                            #connection.close()
                    elif file_flag==0 and self.all_file_flag==0: #当前通道没有传送文件
                        self.gui.text.insert('end',accept_strdata+"\n")
                        self.gui.text.see(tkinter.END)
                        for c in self.sk_list:
                            if c!=conn:
                                c.sendall(bytes(accept_strdata, encoding="utf8"))
                    elif file_flag==0 and self.all_file_flag==1:  #当前通道有其他用户在传送文件，阻塞
                        conn.sendall(bytes("当前通道正在传送文件，请稍后再试", encoding="utf8"))
            conn.close()  # 跳出循环时结束通讯
            self.sk_list.remove(conn)
            self.gui.text.insert('end',str(addr[0])+"@"+str(addr[1])+" "+name+" 断开连接\n")
            self.gui.text.see(tkinter.END)
#线程终止时尝试关闭套接字
        if self.running==False:
            try:
                conn.sendall(bytes("quit", encoding="utf8"))
                conn.close()
            except:
                pass
sk = socket.socket() 
root=tkinter.Tk()
root.title("聊天服务端******MADE BY AlisonTNT")
root.protocol("WM_DELETE_WINDOW",quit_stop)  
client=ThreadedClient()  
root.mainloop()  