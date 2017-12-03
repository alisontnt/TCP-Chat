import tkinter,time,threading,socket,os,struct
from tkinter import messagebox,Label,ttk,Entry,Frame,Text,StringVar
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import askopenfilename
def quit_stop():
    root.quit()
    if client.gui.flag==0:
        sk.sendall(bytes("quit", encoding="utf8"))
        sk.close()
    client.running=False 
class GuiPart():  
    def __init__(self):  
#布局1&标签1&标签1&单行文本框entry1
        self.flag=1
        self.frm1 = Frame(root)
        self.label1 = Label(self.frm1, text="服务器IP地址")
        self.label2 = Label(self.frm1, text="端口")
        self.label4 = Label(self.frm1, text="用户名")
        self.e1=StringVar()
        self.e2=StringVar()
        self.e4=StringVar()
        self.entry1 = Entry(self.frm1, textvariable=self.e1,width=15)
        self.entry2 = Entry(self.frm1, textvariable=self.e2,width=5)
        self.entry4 = Entry(self.frm1, textvariable=self.e4,width=15)
        self.buttontext = tkinter.StringVar()
        self.buttontext.set('连接')
        self.button1 = tkinter.Button(self.frm1, textvariable=self.buttontext, command=self.cmd)
        self.label1.pack(side="left")
        self.entry1.pack(side="left")
        self.label2.pack(side="left")
        self.entry2.pack(side="left")
        self.label4.pack(side="left")
        self.entry4.pack(side="left")
        self.button1.pack(side="left")
        self.frm1.pack()
#布局2&标签3&文本框Text作为对话框
        self.frm2 = Frame(root)
        self.label3 = Label(self.frm2, text="对话框")
        self.text=ScrolledText(self.frm2,width=62,height=15)
        self.text.bind("<KeyPress>",lambda e:"break")
        self.label3.pack(side="top")
        self.text.pack(side="bottom", fill = 'both', expand = True)
        self.frm2.pack()
#布局3
        self.frm3 = Frame(root)
        self.e3=StringVar()
        self.entry3 = Entry(self.frm3, textvariable=self.e3,width=59)
        self.buttontext2 = tkinter.StringVar()
        self.buttontext2.set('发送')
        self.button2 = tkinter.Button(self.frm3, textvariable=self.buttontext2, command=self.cmd2)
        self.entry3.pack(side="left")
        self.button2.pack(side="left")
        self.frm3.pack()
#布局4，文件传输
        self.frm4 = Frame(root)
        self.label5 = Label(self.frm4, text="文件地址")
        self.e5=StringVar()
        self.entry5 = Entry(self.frm4, textvariable = self.e5)
        self.buttontext3 = tkinter.StringVar()
        self.buttontext3.set('选择文件')
        self.buttontext4 = tkinter.StringVar()
        self.buttontext4.set('传送文件')
        self.button3 = tkinter.Button(self.frm4, textvariable=self.buttontext3, command=self.cmd3)
        self.button4 = tkinter.Button(self.frm4, textvariable=self.buttontext4, command=self.cmd4)
        self.label5.pack(side="left")
        self.entry5.pack(side="left")
        self.button3.pack(side="left")
        self.button4.pack(side="left")
        self.frm4.pack()
#其他一些东西的初始化
        self.sendfile_flag=0
        self.thread2=threading.Thread(target=self.workerThread2)
        root.bind("<Return>",self.cmd2)
    def cmd(self):
#主动与服务器连接，当返回值为0时说明连接成功，否则失败
        if self.entry1.get()=='' or self.entry2.get()=='' or self.entry4.get()=='' :
            messagebox.showinfo(title = "ERROR", message = "请把服务器ip，端口，用户名输入完整")
            return
        self.flag=sk.connect_ex((self.entry1.get(),int(self.entry2.get())))
        print(self.flag)
        if self.flag==0:
            sk.sendall(bytes(self.entry4.get(), encoding="utf8"))
            self.entry1['state']='readonly'
            self.entry2['state']='readonly'
            self.entry4['state']='readonly'
            self.text.insert(tkinter.END,"与服务器:"+self.entry1.get()+"端口"+self.entry2.get()+"连接成功"+"\n")
            self.text.see(tkinter.END)
        else:
             messagebox.showinfo(title = "ERROR", message = "连接失败，请检查")
        #print(self.flag)
    def cmd2(self,*args):
        if self.flag!=0:
            messagebox.showinfo(title = "ERROR", message = "还未连接服务器")
            return
        if self.sendfile_flag==1:
            messagebox.showinfo(title = "ERROR", message = "正在传送文件，无法发送")
            return         
        send_data=self.entry3.get()
        if self.entry3.get() == "quit":
            sk.sendall(bytes(send_data, encoding="utf8"))
            sk.close()
            self.text.insert(tkinter.END,"与服务器连接已断开"+"\n")
            self.text.see(tkinter.END)
            self.flag=1
        self.e3.set("")
        self.text.insert(tkinter.END,"我:"+send_data+"\n")#print(send_data)
        self.text.see(tkinter.END)
        sk.sendall(bytes(self.entry4.get()+":"+send_data, encoding="utf8"))
    def cmd3(self):
        path = askopenfilename()
        self.e5.set(path)
    def cmd4(self):
        if self.flag!=0:
            messagebox.showinfo(title = "ERROR", message = "还未连接服务器")
            return
        if self.sendfile_flag==1:
            messagebox.showinfo(title = "ERROR", message = "正在传送文件，无法发送")
            return
        self.text.insert(tkinter.END,"正在传输\n")
        self.text.see(tkinter.END)
        self.thread2.start()
#开个线程传文件
    def workerThread2(self):
        filepath=self.e5.get()
        sk.sendall(bytes("file",encoding="utf8"))
        if os.path.isfile(filepath):
            self.sendfile_flag=1
            fileinfo_size=struct.calcsize('128sl') #定义打包规则
        #定义文件头信息，包含文件名和文件大小
            fhead = struct.pack('128sl',bytes(os.path.basename(filepath),encoding="utf8"),os.stat(filepath).st_size)
            sk.send(fhead) 
            # with open(filepath,'rb') as fo: 这样发送文件有问题，发送完成后还会发一些东西过去
            fo = open(filepath,'rb')
            while True:
                filedata = fo.read(1024)
                if not filedata:
                    break
                sk.send(filedata)
            fo.close()
            print("ok")
            self.sendfile_flag=0
            self.text.insert(tkinter.END,"传输完成\n")
            self.text.see(tkinter.END)
        return
class ThreadedClient():  
    def __init__(self):
#self.gui用来初始化gui    
        self.gui=GuiPart()
#self.running为true表示线程可运行  
        self.running=True  
        self.thread1=threading.Thread(target=self.workerThread1)  
        self.thread1.start()  
        self.periodicCall()  
    def periodicCall(self):  
        root.after(200,self.periodicCall)    
        if not self.running:  
            root.destroy()
#线程1，用来接收服务器的数据  
    def workerThread1(self):
#当running为真时，这个线程会一直运行 
        while self.running:
            time.sleep(0.0001)
            file_flag=0
#如果gui.flag==0，说明套接字连接服务器成功
            if self.gui.flag==0:
                if file_flag==0:
                    accept_data = sk.recv(1024)
                    try:
                        acceptstr_data = str(accept_data, encoding="utf8")
                    except:
                        pass
                if acceptstr_data=="quit" and file_flag==0:
                    sk.close()
                    self.gui.text.insert(tkinter.END,"服务器连接已断开"+"\n")
                    self.gui.text.see(tkinter.END)
                    self.gui.flag=1
#接收文件
                elif acceptstr_data=="file" or file_flag==1:
                    file_flag=1
                    self.gui.text.insert(tkinter.END,"准备接收文件"+"\n")
                    self.gui.text.see(tkinter.END)
                    fileinfo_size=struct.calcsize('128sl') 
                    buf = sk.recv(fileinfo_size)
                    if buf: #如果不加这个if，第一个文件传输完成后会自动走到下一句
                        filename,filesize =struct.unpack('128sl',buf)
                        #filename_f = str(filename).strip('\00')
                        #print(str(filename_f,decoding="utf8"))
                        filename_f=str(filename,encoding="utf8").strip('\x00')        
                        print(repr(filename_f))
                        print(fileinfo_size)
                        #filenewname = os.path.join('d:\\',filename_f)
                        now = os.path.split(os.path.realpath(__file__))[0]
                        print(now)
                        filenewname=os.path.join(now,filename_f)
                        print(filenewname)
                        recvd_size = 0 #定义接收了的文件大小
                        file = open(filenewname,'wb')
                        self.gui.text.insert(tkinter.END,"正在接收文件"+"\n")
                        self.gui.text.see(tkinter.END)
                        while not recvd_size == filesize:
                            if filesize - recvd_size > 1024:
                                rdata = sk.recv(1024)
                                recvd_size += len(rdata)
                            else:
                                rdata = sk.recv(filesize - recvd_size) 
                                recvd_size = filesize
                            file.write(rdata)
                        file.close()
                        self.gui.text.insert(tkinter.END,"接收成功，目标文件在:"+filenewname+"\n")
                        self.gui.text.see(tkinter.END)
                        file_flag=0
#正常接收
                else:
                    self.gui.text.insert(tkinter.END,acceptstr_data+"\n")
                    self.gui.text.see(tkinter.END)
                #print(accept_data) 
sk = socket.socket() 
root=tkinter.Tk()
root.title("聊天客户端******MADE BY AlisonTNT")
root.protocol("WM_DELETE_WINDOW",quit_stop)  
client=ThreadedClient()
root.mainloop()  