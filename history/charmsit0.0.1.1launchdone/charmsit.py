VERSION = "0.0.1.1"
import tkinter as tk
import time
import json
import pynput
import os
import getpass
import threading
from PIL import Image, ImageTk
try:
    import geticon
    import getlnkfrom
    CANICON = 1
except:
    import geticon_notwin as geticon
    import getlnkfrom_notwin as getlnkfrom
    CANICON = 0

import platform
SYSTEM = platform.system()

ANIMATIONSPEED = 1
ALLOWANIMATION = 1
SEC1 = 1000

APPS_WIN_USR = r"C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs"
APPS_WIN_ALL = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs"
#print(os.listdir(PRO_WIN_USR%getpass.getuser()))

def tup_hex(tup):
    " color converting "
    if isinstance(tup,str):
        return tup
    return "#%.2X%.2X%.2X"%tup

def hex_tup(string):
    " color converting "
    if isinstance(string,tuple):
        return string
    return int(string[1:3],16),int(string[3:5],16),int(string[5:7],16)

def animate1(start,end,duration,passed):
    " y=kx+b "
    return (passed/duration) * (end-start) + start

def animate2(start,end,duration,passed,middle,mtime=None):
    " y=ax2+bx+c "
    if mtime is None:
        mtime = (end - start)/2
    y = quadratic((0,start),(mtime,middle),(duration,end))
    return y(passed)

def animatep(start,end,duration,passed,middle,mtime=None):
    " the function image is a polyline"
    if passed >= mtime:
        #return animate1(middle,end,duration-mtime,passed-mtime)
        return ((passed-mtime)/(duration-mtime)) * (end-middle) + middle
    #return animate1(start,middle,mtime,passed)
    return (passed / mtime) * (middle-start) + start # less call, less cpu use

def _quadratic(p1,p2,p3):
    " y = ax^2 + bx + c "
    x1,y1 = p1
    x2,y2 = p2
    x3,y3 = p3
    a = y1/(x1-x2)/(x1-x3) + y2/(x2-x1)/(x2-x3) + y3/(x3-x1)/(x3-x2)
    b = - y1*(x3+x2)/(x1-x2)/(x1-x3) - y2*(x3+x1)/(x2-x1)/(x2-x3) - y3*(x1+x2)/(x3-x1)/(x3-x2)
    c = y1 - a * x1 * x1 - b * x1
    return a,b,c

def quadratic(p1,p2,p3):
    a,b,c = _quadratic(p1,p2,p3)
    return lambda x: a*x**2 + b * x + c

def color(name):
    #return {"bg-normal":"#6400E6","bg-entered":"black","bg-pressed":"grey"}.get(name)
    return {"bg-normal":"black","bg-entered":"grey","bg-pressed":"lightgrey","fg-normal":"white"}.get(name)
FONT = ""

def lang(key,default=None):
    return langdic.get(key,defalut if default else key.split('.')[-1])

def get_all_apps():
    lst = set()
    for path,dirs,files in os.walk(APPS_WIN_USR):
        for f in files:
            if f.endswith(".lnk"):
                lst.add(os.path.join(path,f))

    for path,dirs,files in os.walk(APPS_WIN_ALL):
        for f in files:
            if f.endswith(".lnk"):
                lst.add((f[:-4],os.path.join(path,f)))

    return sorted(list(lst))

class AnimateManager:
    def __init__(self,widget,duration,start,end,before,during,after,passtime=None,forceopen=0):
        self.widget = widget
        self._duration = duration
        self.start = start
        self.end = end
        # functions
        self.before = before
        self.during = during
        self.after = after
        # the pass time of two frames
        self.passtime = 1
        if passtime:
            self.passtime = passtime
        # the class saves the state of animating
        if not hasattr(widget,"animate"):
            self.widget.animate = 0
        self.func = animate1
        self.func_extra = []
        self.forceopen = forceopen
        self._stopped = 0
    def start_animate(self,nextani=None):
        " start an animation with default settings "
        # when there's a animate playing, set 0 to break it
        widget = self.widget
        if widget.animate:
            widget.animate = 0
        else:
            widget.animate = 1
        # prepare
        self.start_time = time.time()
        self.passed = 0
        self.duration = self._duration / ANIMATIONSPEED
        self.before()
        if ALLOWANIMATION or self.forceopen:
            self.widget.after(self.passtime,self.loop)
        else:
            self.after()
    def loop(self):
        " the loop of animation "
        if self._stopped:
            return
        widget = self.widget
        if widget.animate == 0:
            widget.animate = 1
            self.after()
            return
        passed = time.time() - self.start_time
        if passed >= self.duration:
            widget.animate = 0
            self.after()
            return
        var = self.func(self.start,self.end,self.duration,passed,*self.func_extra)
        self.during(var)
        #if not self._stopped:
        widget.after(self.passtime,self.loop)
    def stop(self):
        self._stopped = 1

class Button(tk.Label):
    def __init__(self,master=None,*a,**b):
        self._command = b.pop("command",None)
        b.setdefault("font",(FONT,20))
        super().__init__(master,*a,**b)
        self.bind("<Enter>",self._enter,1)
        self.bind("<ButtonPress-1>",self._pressed,1)
        self.bind("<ButtonRelease-1>",self._release,1)
        self.bind("<Leave>",self._leave,1)
        self["bg"] = color("bg-normal")
        self["fg"] = color("fg-normal")
        self._executable = 1
    def _enter(self,e):
        self["bg"] = color("bg-entered")

    def _pressed(self,e):
        self["bg"] = color("bg-pressed")
        """
        command = self._command
        if callable(command):
            command()
        """
    def _release(self,e):
        self["bg"] = color("bg-entered")
        command = self._command
        if callable(command) and self._executable:
            command()
    def _leave(self,e):
        self["bg"] = color("bg-normal")

#########################################
## ABOVE COPIED FROM MY OTHER PROJECTS ##
#########################################
        
class Charmspop(tk.Toplevel):
    width = 180
    def __init__(self,master=None,*a,**b):
        super().__init__(master,*a,**b)
        self.poped = 0
    def bindall(self):
        self.onfoc = 1
        self.bind("<Enter>",lambda e,self=self:setattr(self,"onfoc",1))
        self.bind("<Leave>",lambda e,self=self:((setattr(self,"onfoc",0) or self.after(SEC1,self.checkpop)) if self.winfo_pointerx() < self.winfo_screenwidth()-self.width  else 0))
        # above is surely a bug, but i dont want to modify =P
        self.frame = Charmspopframe(pop)
        self.frame.pack(fill='both',expand=1)
        self.poped = 0
        self.sub = tk.Toplevel(self)
        self.sub.geometry("600x200+100-100")
        self.sub.overrideredirect(1)
        self.sub.attributes("-topmost",1)
        self.sub.withdraw()
        Timerframe(self.sub).pack(fill="both",expand=1)
        self.protocol("WM_DELETE_WINDOW",lambda:None)
    def disappear(self):
        def funcd(var):
            showing.attributes("-alpha",var)
            self.sub.attributes("-alpha",var)
        def funca():
            showing.withdraw()
            self.sub.withdraw()
        am = AnimateManager(showing,0.2,0.2,0,lambda:None,funcd,lambda:None)
        am.start_animate()
        self.after(100,funca)
        self.poped = 0

    def checkpop(self):
        if not self.onfoc:
            self.disappear()
            self.poped = 0

    def popup(self):
        swidth = self.winfo_screenwidth()
        sheight = self.winfo_screenheight()
        self.geometry("%dx%d+%d+0"%(self.width,sheight,swidth) )
        self.deiconify()
        self.sub.attributes("-alpha",0)
        self.sub.deiconify()
        am = AnimateManager(self,0.6,swidth,swidth-self.width,self.before,self.during,self.aftera)
        am.start_animate()
        self.poped = 1
        self.frame.putup()
        global showing
        showing = self
    def before(self):
        pass
    def during(self,var):
        swidth = self.winfo_screenwidth()
        sheight = self.winfo_screenheight()
        self.geometry("%dx%d+%d+0"%(self.width,sheight,var) )
        if var == swidth:
            var = swidth - 0.01
        per = (swidth-var)/self.width
        #self.attributes("-alpha",self.width/(swidth-var) * 0.14 + 0.2)
        self.attributes("-alpha",per*0.4)# 0 0  1 0.4
        self.sub.attributes("-alpha",per)
        #r = int(100 * per)
        #g = 0
        #b = int(230 * per)
        #self.frame["bg"] = tup_hex((r,g,b))
    def aftera(self):
        swidth = self.winfo_screenwidth()
        sheight = self.winfo_screenheight()
        self.geometry("%dx%d+%d+0"%(self.width,sheight,swidth-self.width) )
        self.attributes("-alpha",0.4)
        #self.frame["bg"] = tup_hex((100,0,230))

class Charmspopframe(tk.Frame):
    def __init__(self,master=None,*a,**b):
        super().__init__(master,*a,**b)
        bg = color("bg-normal")
        fg = color("fg-normal")
        self["bg"] = bg
        self.btnwin = Button(self,text=lang("main.win"),font="Simhei 20",fg=fg,command=lambda:time.sleep(0.1) or pynput.keyboard.Controller().press(pynput.keyboard.Key.cmd) or pynput.keyboard.Controller().release(pynput.keyboard.Key.cmd) or self.master.disappear())
        #self.btnwin.place(relx=0.5,rely=0.5,width=120,height=120,anchor='center')
        self.btnsch = Button(self,text=lang("main.search"),font="Simhei 20",fg=fg)
        self.btnshr = Button(self,text=lang("main.tools"),font="Simhei 20",fg=fg)
        self.btnlch = Button(self,text=lang("main.launch"),font="Simhei 20",fg=fg,command=self.launch)
        self.btnset = Button(self,text=lang("main.settings"),font="Simhei 20",fg=fg)
        Button(self,command=lambda:self.master.disappear() or pynput.keyboard.Controller().press(pynput.keyboard.Key.cmd) or pynput.keyboard.Controller().press('d') or pynput.keyboard.Controller().release(pynput.keyboard.Key.cmd)or pynput.keyboard.Controller().release('d')).place(x=0,y=self.winfo_screenheight()-20,width=200,height=20)
        #self.putup()
        self.btnlch.win = Launcherwin(self.master)
    def putup(self):
        def during(wid,seek):
            nonlocal swidth, sheight
            def func(var):
                nonlocal swidth, sheight
                wid.place(x=var,y=sheight/2+seek,width=120,height=120,anchor='center')
                #print(var)
                self.update()
            return func
        def after():
            swidth = self.winfo_screenwidth()
            sheight = self.winfo_screenheight()
            width = self.master.width
            self.btnwin.place(x=width/2,y=sheight/2,width=120,height=120,anchor='center')
            self.btnsch.place(x=width/2,y=sheight/2-240,width=120,height=120,anchor='center')
            self.btnshr.place(x=width/2,y=sheight/2-120,width=120,height=120,anchor='center')
            self.btnlch.place(x=width/2,y=sheight/2+120,width=120,height=120,anchor='center')
            self.btnset.place(x=width/2,y=sheight/2+240,width=120,height=120,anchor='center')
        # forget before appearance
        self.btnsch.place_forget()
        self.btnshr.place_forget()
        self.btnwin.place_forget()
        self.btnlch.place_forget()
        self.btnset.place_forget()
        # vars
        swidth = self.winfo_screenwidth()
        sheight = self.winfo_screenheight()
        width = self.master.width
        # set time-order animation
        am = AnimateManager(self.btnsch,0.3,width*1.5,width/2,lambda:None,during(self.btnsch,-240),lambda:None)
        self.after(200,am.start_animate)
        am = AnimateManager(self.btnshr,0.3,width*1.5,width/2,lambda:None,during(self.btnshr,-120),lambda:None)
        self.after(300,am.start_animate)
        am = AnimateManager(self.btnwin,0.3,width*1.5,width/2,lambda:None,during(self.btnwin,0),lambda:None)
        self.after(400,am.start_animate)
        am = AnimateManager(self.btnlch,0.3,width*1.5,width/2,lambda:None,during(self.btnlch,120),lambda:None)
        self.after(500,am.start_animate)
        am = AnimateManager(self.btnset,0.3,width*1.5,width/2,lambda:None,during(self.btnset,240),lambda:None)
        self.after(600,am.start_animate)
        # handle after
        self.after(1000,after)
    def launch(self):
        self.btnlch.win.appear()

class Launcherwin(tk.Toplevel):
    width = 480
    def __init__(self,master,*a,**b):
        super().__init__(master,*a,**b)
        self.overrideredirect(1)
        self.withdraw()
        self.protocol("WM_DELETE_WINDOW",lambda:None)
        self.frame = Launcherframe(self)
        self.frame.pack(fill="both",expand=1)
        self.update()
    def appear(self):
        swidth = self.winfo_screenwidth()
        sheight = self.winfo_screenheight()
        width = self.master.width
        self.geometry("%dx%d+%d+0"%(self.width,sheight,swidth-width))
        self.attributes("-topmost",1,"-alpha",0.4)
        am = AnimateManager(self,0.6,0,1,lambda:None,self.during,lambda:None)
        am.start_animate()
        self.frame.appear()
        self.deiconify()
        self.after(10,self.master.withdraw)
        global showing
        showing = self
    def during(self,var):
        swidth = self.winfo_screenwidth()
        sheight = self.winfo_screenheight() # 0 swidth-self.master.width   1 swidth-self.width
        x = (self.master.width-self.width) * var + swidth - self.master.width
        self.geometry("+%d+0"%x)
        self.attributes("-alpha",0.2*var+0.4)
    def disappear(self):
        swidth = self.winfo_screenwidth()
        sheight = self.winfo_screenheight()
        width = self.master.width
        self.geometry("%dx%d+%d+0"%(self.width,sheight,swidth-width))
        self.attributes("-topmost",1,"-alpha",0.4)
        am = AnimateManager(self,0.4,1,0,lambda:None,self.disduring,lambda:None)
        am.start_animate()
        self.frame.disappear()
        self.after(400,self.master.deiconify)
        self.after(400,self.withdraw)
        global showing
        showing = self.master
    def disduring(self,var):
        swidth = self.winfo_screenwidth()
        sheight = self.winfo_screenheight() # 0 swidth-self.master.width   1 swidth-self.width
        x = (self.master.width-self.width) * var + swidth - self.master.width
        self.geometry("+%d+0"%x)
        self.attributes("-alpha",0.2*var+0.4)
    

class Timerframe(tk.Frame):
    def __init__(self,master=None,*a,**b):
        super().__init__(master,*a,**b)
        self["bg"] = "black"
        self.ltm = tk.Label(self,text="11:45",font="Simhei 90",bg="black",fg="white")
        self.ltm.place(x=20,rely=0.5,anchor='w')
        self.lts = tk.Label(self,text=":14",font="Simhei 36",bg="black",fg="white")
        self.lts.place(x=320,y=40)
        self.lwk = tk.Label(self,text="Mon",font="Simhei 36",bg="black",fg="white")
        self.lwk.place(x=420,y=40)
        self.ldy = tk.Label(self,text="19/19",font="Simhei 36",bg="black",fg="white")
        self.ldy.place(x=330,y=100)
        self.update_min()
        tk.Label(self,text="CharmsIt",font="Simsun 20",bg="black",fg="white").place(x=470,y=110)
        self.updates()
    def update_min(self):
        self.ltm["text"] = time.strftime("%H:%M")
        self.lwk["text"] = lang("main.day%s"%time.strftime("%w"))
        self.ldy["text"] = time.strftime("%m/%d")
    def updates(self):
        #print(type(self.master),self.master.master)
        if self.master.master.poped:
            self.lts["text"] = time.strftime(":%S")
            if int(time.strftime("%S")) <= 2:
                self.update_min()
        self.after(100,self.updates)

class Launcherframe(tk.Frame):
    def __init__(self,master,*a,**b):
        super().__init__(master,*a,**b)
        self["bg"] = color("bg-normal")
        self.back = Button(self,text="<-",font="Simhei 24",command=self.master.disappear)
        self.back.place(x=20,y=20)
        self.titlel = tk.Label(self,text=lang("launch.title"),font="Simhei 24",bg=color("bg-normal"),fg=color("fg-normal"))
        self.titlel.place(x=80,y=20)
        self.lw = self.master.width-80
        self.frame = tk.Frame(self,bg=color("bg-normal"))
        self.frame.place(x=40,y=100,width=self.lw,height=self.winfo_screenheight()-140)
        btnframe = self.btnframe = tk.Frame(self.frame,bg=color("bg-normal"),)
        btnframe.place(x=0,y=0,width=self.lw,height=self.winfo_screenheight()-140)
        #btnframe.bind_all("<>")
        btnframe.bind_all("<MouseWheel>",self._mwh,1)
        btnframe.bind_all("<Button-4>",self._mwhup,1)
        btnframe.bind_all("<Button-5>",self._mwhdn,1)
        btnframe.bind_all("<B1-Motion>",self._mofm,1)
        btnframe.bind_all("<ButtonPress-1>",self._b1p,1)
        btnframe.bind_all("<ButtonRelease-1>",self._b1r,1)
        #Button(self,bitmap="question",text="QUESTION",compound="left",font="Simhei 36",anchor='w',padx=20).place(x=40,y=100,height=80,width=self.master.width-80)
        self.btns = []
        self.stopanimate = lambda:None
        self.mouse = (0,0)

    def _mwhup(self,e):
        delta = e.delta / 120
        btnframe = self.btnframe
        info = btnframe.place_info()
        btnframe.place(y=int(info["y"])+delta,height=len(self.btns)*80)

        info = btnframe.place_info()
        if int(info["y"]) > 0:
            place_animate(btnframe,0.2,0,0,int(info["y"]),0)
        elif int(info["y"]) < 140-self.winfo_screenheight():
            place_animate(btnframe,0.2,0,0,int(info["y"]),140-self.winfo_screenheight())

    def _mwhdn(self,e):
        delta = e.delta / 120
        btnframe = self.btnframe
        info = btnframe.place_info()
        btnframe.place(y=int(info["y"])-delta,height=len(self.btns)*80)

        info = btnframe.place_info()
        if int(info["y"]) > 0:
            place_animate(btnframe,0.2,0,0,int(info["y"]),0)
        elif int(info["y"]) < 140-self.winfo_screenheight():
            place_animate(btnframe,0.2,0,0,int(info["y"]),140-self.winfo_screenheight())

    def _mwh(self,e):
        if SYSTEM == "Windows":
            delta = e.delta / 120 * -3
        else:
            delta = e.delta * -3
        btnframe = self.btnframe
        info = btnframe.place_info()
        btnframe.place(y=int(info["y"])-delta*10,height=len(self.btns)*80)
        info = btnframe.place_info()
        if int(info["y"]) > 0:
            #self.stopanimate()
            self.stopanimate = place_animate(btnframe,0.2,0,0,int(info["y"]),0)
        elif int(info["y"]) < 140-self.winfo_screenheight():
            #self.stopanimate()
            self.stopanimate = place_animate(btnframe,0.2,0,0,int(info["y"]),140-self.winfo_screenheight())

    def _b1p(self,e):
        self.mouse = (e.x, e.y)

    def _b1r(self,e):
        for btn in self.btns:
            btn._executable = 1

    def _mofm(self,e):
        x = e.x
        y = e.y
        ox,oy = self.mouse
        if ox == 0 and oy == 0:
            self.mouse = (x,y)
            return
        for btn in self.btns:
            btn._executable = 0
        info = self.btnframe.place_info()
        if int(info["y"])-(oy-y) > 0:
            #self.btnframe.place(y=0)
            return
        elif int(info["y"])-(oy-y) < 140-self.winfo_screenheight():
            return
            #self.btnframe.place(y=140-self.winfo_screenheight())
        self.btnframe.place(y=int(info["y"])-(oy-y),height=len(self.btns)*80)

    def fill(self):
        for w in self.btns:
            w.destory()
        self.btns.clear()
        idx = 0
        for name, path in get_all_apps():
            if not path.endswith(".lnk"):
                continue
            if not getlnkfrom.get_lnk_file(path).endswith(".exe"):
                continue
            if not os.path.exists(getlnkfrom.get_lnk_file(path)):
                continue
            btn = Button(self.btnframe,text=name,compound="left",font="Simhei 32",anchor='w',padx=20)
            btn._command = lambda path=path,self=self:(os.startfile(getlnkfrom.get_lnk_file(path)) or self.master.master.disappear())
            #btn.place(x=40,y=100+idx*80,height=80,width=self.master.width-80)
            btn.place(x=0,y=idx*80,height=80,width=self.lw)
            btn.path = path
            btn.y = idx*80
            btn.stop = lambda:None
            self.btns.append(btn)
            idx += 1
        threading.Thread(target=self.geticons,daemon=1).start()

    def geticons(self,):
        #print(CANICON)
        if not CANICON:
            return
        for btn in self.btns:
            path = btn.path
            path = getlnkfrom.get_lnk_file(path)
            #print(path)
            #rgb = geticon.rgb(geticon.get_raw_data(path,0,32),32,32)
            try:
                rgb = geticon.rgb(geticon.get_raw_data(path,0,32),32,32)
            except Exception as e:
                #print(e)
                continue
            im = Image.new("RGB",(32,32))
            im.frombytes(rgb)
            #im.save("demo.jpg")
            imt = ImageTk.PhotoImage(im)
            #btn.im = im
            btn.imt = imt
            btn["image"] = imt

    def appear(self):
        if not self.btns:
            self.fill()
        self._change()

    def disappear(self):
        self._change(True)

    def _change(self,t=False):
        place_animate(self.back,0.6,20+self.master.width,20,20,20,t)
        place_animate(self.titlel,0.7,80+self.master.width,80,20,20,t)
        wait = 1
        for btn in self.btns:
            btn.place_forget()
            btn.stop()
            btn.stop = place_animate(btn,0.2 if t else 0.4-wait*0.02,self.lw,0,btn.y,btn.y,t,wait*100,kw={"width":self.lw,"height":80})
            wait += 1


def checkpopup():
    swidth = root.winfo_screenwidth()
    sheight = root.winfo_screenheight()
    mx,my = root.winfo_pointerxy()
    if swidth-mx > 30:
        root.clock = 16
    elif not pop.poped:
        if root.clock == 16:
            root.clock = 1
        else:
            root.clock -= time.time()-root.now
            if root.clock <= 0:
                #print("Popup!")
                pop.popup()
                root.clock = 16
    root.now = time.time()
    root.after(100,checkpopup)

def place_animate(wid,t,xs,xe,ys,ye,reverse=False,wait=0,kw=None):
    if not kw:
        kw = {}
    def during(var):
        wid.place(x=(xe-xs)*var+xs,y=(ye-ys)*var+ys,**kw)
    def after():
        wid.place(x=xe,y=ye,**kw)
    am = AnimateManager(wid,t,0,1,lambda:None,during,after)
    if reverse:
        am = AnimateManager(wid,t,1,0,lambda:None,during,after)
    if wait == 0:
        am.start_animate()
    else:
       wid.after(wait,am.start_animate)
    return am.stop

with open("lang/zh-cn.json",'r') as f:
#with open("lang/en-us.json",'r') as f:
    langdic = json.loads(f.read())
root = tk.Tk()
root.withdraw()
root.now = time.time()
root.clock = 0
pop = Charmspop()
pop.overrideredirect(1)
pop.attributes("-topmost",1)
pop.bindall()
showing = pop
checkpopup()
#root.after(0,pop.popup())
root.mainloop()
