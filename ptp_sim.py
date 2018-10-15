# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 18:04:52 2018

@author: fd
"""

import matplotlib.pyplot as plt
import numpy as np
messagecache=[]
mmm=[]
second=1000000000
simtime=500
adjustdelay=False
improve=True
ERR=[]
class Message(object):
    def __init__(self,type,senderID,reciverID,time,hop=1000):
        self.type=str(type)
        self.senderID=senderID
        self.reciverID=reciverID
        self.hop=hop
        self.time=int(time)
        self.pathdelay=net_delay[senderID][reciverID]+int(abs(np.random.normal(0,net_delay_jitter[senderID][reciverID])))
    def __str__(self):
        return "============================================(%s) %s->%s 内容:%s ||| "%(self.type,self.senderID,self.reciverID,self.time)+str(self.hop)
class Master_Clock_info(object):
    def __init__(self,id=0,t1=0,t2=0,t3=0,t4=0,t5=0,t6=0,pop=0,clock=0,quality=1,hop=1,time_send_delay_req=100,t2t3flag=False):#q越大越好
        self.t1=t1
        self.t2=t2
        self.t3=t3
        self.t4=t4
        self.id=id
        self.hop=hop
        self.clock=0
        self.quality=quality
        self.time_send_delay_req=time_send_delay_req
        self.t2t3flag=t2t3flag
        self.sync_times=0
        self.sum_off=0
        self.delay_off=0
        self.t5=t5
        self.t6=t6
    def __str__(self):
        return "info: ID:%s    t1=%s t2=%s t3=%s t4=%s hop=%s clock=%s"%(self.id,self.t1,self.t2,self.t3,self.t4,self.hop,self.clock)
        
        
class Node(object):
    def __init__(self,i,clock,quality=1,e2e=False,hop=1000):
        self.isGrandMaster=False
        self.send_to_list=[] #type:int ID
        self.recive_from_list=[]# type:master_clock_info
        self.clock=clock
        self.clock_rate=1
        self.ID=i
        self.t2_t3=100
        self.bmcid=0
        self.hop=hop
        self.bmcquality=0
        self.quailty=quality
    def __str__(self):
        re="########################Node_info\r\n"
        re+= "ID:%s clock: %s MasterID:%s\r\n"%(self.ID,self.clock,self.bmcid)
        re+="Master_list:\r\n"
        for i in self.recive_from_list:
            re+="      "+str(i)+"\r\n"
        re+="send_to_list:"
        for i in self.send_to_list:
            re+=str(i)+" "
        re+="\r\n hop="+str(self.hop)
        return re
    
    def sendmessage(self,a): 
        messagecache.append(a)
        
    def appendmaster(self,master_clock_info):
        self.recive_from_list.append(master_clock_info)
        if master_clock_info.quality>self.bmcquality:
            self.bmcquality=master_clock_info.quality
            self.bmcid=master_clock_info.id
            
    def recive_message(self,ms):
        if ms.type=="Sync":
            masterid=ms.senderID
            for i in range(len(self.recive_from_list)):
                if self.recive_from_list[i].id==masterid:
                    self.recive_from_list[i].t1=ms.time
                    self.recive_from_list[i].hop=ms.hop #  我的算法
                    self.recive_from_list[i].t2=self.clock
                    self.recive_from_list[i].time_send_delay_req=self.t2_t3
                    self.recive_from_list[i].t2t3flag=True
                    
                    
        elif ms.type=="Delay_Req":
            self.sendmessage(Message("Delay_Resp",self.ID,ms.senderID,self.clock)) 
            
        elif ms.type=="Delay_Resp":
            masterid=ms.senderID
            for i in range(len(self.recive_from_list)):
                if self.recive_from_list[i].id==masterid:
                    self.recive_from_list[i].t4=ms.time;
                    d=self.recive_from_list[i].delay_off
                    if not adjustdelay:
                        d=0
                    else:
                        self.sendmessage(Message("Delay_Req2",self.ID,ms.senderID,self.clock))
                    ##更新根据节点i算出来的本地时间
                    self.recive_from_list[i].clock= (self.clock
                                         -(1/2*(self.recive_from_list[i].t2
                                                +self.recive_from_list[i].t3
                                                -self.recive_from_list[i].t1 
                                                -self.recive_from_list[i].t4)))+int(d/2)
                    self.recive_from_list[i].t5=self.recive_from_list[i].clock #记录t5
                    
                    ###原始时钟更新算法       直接按照最好的时钟更新本地时钟 
                    if not improve:
                        if self.recive_from_list[i].id==self.bmcid:
                            self.clock=int(self.recive_from_list[i].clock)
                    else:#我的算法

                        myhop_1=0  #1/hop
                        for i in range(len(self.recive_from_list)):
                            myhop_1+=1/(self.recive_from_list[i].hop+1)
                        self.hop=1/myhop_1#等效跳数
                        #加权 等待所有都发来了同步信息
                        for i in range(len(self.recive_from_list)):
                            if self.recive_from_list[i].id==masterid:
                                self.clock=int((self.clock
                                                 -1/((self.recive_from_list[i].hop+1)*myhop_1)*
                                                 (1/2*(self.recive_from_list[i].t2
                                                        +self.recive_from_list[i].t3
                                                        -self.recive_from_list[i].t1 
                                                        -self.recive_from_list[i].t4))))

                        
                        
                                
                                
                            
        elif ms.type=="Delay_Req2":
            self.sendmessage(Message("Delay_Resp2",self.ID,ms.senderID,self.clock)) 
        
        elif ms.type=="Delay_Resp2":
            masterid=ms.senderID
            
            for i in range(len(self.recive_from_list)):
                if self.recive_from_list[i].id==masterid:
                    self.recive_from_list[i].t6=ms.time
                    self.recive_from_list[i].sync_times+=1
                    #(t6-t5)*2-(t2-t1+t4-t3)
                    off=((self.recive_from_list[i].t6-self.recive_from_list[i].t5)*2
                                             -(self.recive_from_list[i].t2-self.recive_from_list[i].t1
                                               +self.recive_from_list[i].t4-self.recive_from_list[i].t3))
                    if self.recive_from_list[i].sync_times<100:
                        self.recive_from_list[i].sum_off+=off
                        a=self.recive_from_list[i].sum_off
                        b=a
                        print(self)
                        print(off)
                        print("\r\n")
                        
                    else:
                        self.recive_from_list[i].sum_off=self.recive_from_list[i].sum_off*99/100+off
                        self.recive_from_list[i].delay_off=self.recive_from_list[i].sum_off/100
                        a=self.recive_from_list[i].sum_off
                        b=a

                    
                    
                    
                       
                            
                                
                                
                        #print("clock",self.ID,"updated","\r\n")

    def plus1s(self):
        self.clock+=second-simtime
    def update(self):
        #先收发再更新
        if int(self.clock%1000000000)==0:
            for i in self.send_to_list:
                self.sendmessage(Message("Sync",self.ID,i,self.clock,self.hop))
        for i in range(len(self.recive_from_list)):   
            if self.recive_from_list[i].t2t3flag:
                self.recive_from_list[i].time_send_delay_req-=1
                if self.recive_from_list[i].time_send_delay_req==0:
                    #print(self.ID,"send delay_req to",self.recive_from_list[i].id)
                    self.sendmessage(Message("Delay_Req",self.ID,self.recive_from_list[i].id,0))
                    self.recive_from_list[i].t3=self.clock
                    self.recive_from_list[i].t2t3flag=False
        self.clock+=self.clock_rate
      
def connect(a,b,ab_delay=0,ba_delay=0,ab_jitter=0,ba_jitter=0):
      #a is master
    nodelist[a].send_to_list.append(b)
    h=1000
    if a==0:
        h=1
    nodelist[b].appendmaster(Master_Clock_info(id=a,quality=nodelist[a].quailty,hop=h))
    if ab_delay>0:
        net_delay[a][b]=ab_delay
    if ba_delay>0:
        net_delay[b][a]=ba_delay
    if improve and a==0:
        nodelist[b].hop=1
        
def Connect(l):
    
    for i in l.split(" "):
        a,b=i.split(",")
        connect(int(a),int(b))
    
##############主程序#####################
n=9
improve=True
net_delay=[[100 for i in range(n)] for i in range(n)]
net_delay_jitter=[[10 for i in range(n)] for i in range(n)]
nodelist=[]
nodelist.append(Node(0,-10,3,hop=0))#ID  初始时钟 quality grandmaster

for i in range(1,n):
    nodelist.append(Node(i,-20,2))
    
#Connect("0,1 1,2 0,3 1,4 2,5 3,4 4,5 3,6 4,7 5,8 6,7 7,8")
Connect("0,1 0,2 1,3 2,4 3,5 3,6 4,7 4,8")
#print(nodelist[1])
t=0
#    仿真单位：纳秒 一轮同步在simtime纳秒内完成
ERR=[] #用于存储每一次同步后的误差
while t<10000*second:#10s
    if t%second<=simtime:
        t+=1
        b=messagecache[::-1]
        for message in b:
            message.pathdelay-=1
            if message.pathdelay<=0:
#                if message.type=="Sync":
#                    print(message)
                nodelist[message.reciverID].recive_message(message)
                messagecache.remove(message)
        for i in nodelist:
            i.update()
    else:
        #一轮更新结束 进入下一轮 
        #统计信息
        error=[]
        for i in range(1,len(nodelist)):
            error.append(nodelist[i].clock-nodelist[0].clock)
        ERR.append(error)
        #print(error)
        t+=second-simtime #1s
        for i in nodelist:
            i.plus1s()
#print(ERR)

for i in range(n-1):
    i=i+1
    plt.subplot(2,4,i)
    a=[]
    for j in range(len(ERR)):
        a.append(ERR[j][i-1])
    a=np.array(a)
    print(np.var(a))
    plt.grid(axis='y', alpha=0.75)
    plt.ylabel('')
    plt.title('var:'+str(np.var(a))[0:4])
    plt.ylim((0, len(ERR)/1000*100))
    plt.xlim((-30,30))
    plt.hist(a, # 绘图数据
            bins = 300, # 指定直方图的条形数为20个
            color = 'steelblue', # 指定填充色
            edgecolor = 'k', # 指定直方图的边界色
            label = 'a' )# 为直方图呈现标签
plt.xlabel('offset from GrandMaster /ns')
plt.show()
