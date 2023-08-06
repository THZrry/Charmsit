"""
CharmsIt mainfile.
CharmsIt is a python-based software to take Charmbar back to windows and
even posix systems!
through tkinter is not good at making gui with animation and handling touching
events, i made it more useful.
it's smooth, perhaps because tkinter is light..
"""
VERSION = "0.0.1.1-9"
import tkinter as tk
import time
import json
import pynput
import os
import sys
import getpass
import re
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

import getim
#import mss as msslib
#mss = msslib.mss()
import math

import platform
SYSTEM = platform.system()

ANIMATIONSPEED = 1
ALLOWANIMATION = 1
SEC1 = 1000

APPS_WIN_USR = r"C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs"
APPS_WIN_ALL = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs"
APPS_WIN_UWP = r"C:\Program Files\WindowsApps"
UWP_MATCH = re.compile("(?P<a>\D*)_\d*.\d*.\d*.\d*_\w\w\w__(?P<b>\w*)")
UWP_APPID_MATCH = re.compile('<Application Id="(?P<a>\w*)"')
UWP_ICONPATH_MATCH = re.compile('<Logo>(?P<a>\S+)</Logo>')

ANI_DUR = 1 # 1/1000 ms per frame
# FPS: 24 30 45 60 90 120 INF
# DUR: 41 33 22 16 11 8   1

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

def animate2(start,end,duration,passed):
    x = passed / duration
    #return start+(end-start)*(x**3 - 0.3*x*math.sin(x*3.14))
    return start+(end-start)*(3*math.sin(x-5.7)-2)
    #return start+(end-start)*(math.sqrt(x**4))
    #return start+(end-start)*(math.sin(x*3.14/2))

def animate3(start,end,duration,passed):
    x = passed / duration
    try:return start+(end-start)*(math.sqrt(x))
    except: return x

def animate4(start,end,duration,passed):
    x = passed / duration
    return start+(end-start)*(x**3 - 0.3*x*math.sin(x*3.14))
def animate5(start,end,duration,passed):
    x = passed / duration
    return start+(end-start)*(x**2)
def animate6(start,end,duration,passed):
    x = passed / duration
    return start+(end-start)*(math.sin(x*3.14/2))
def animate7(start,end,duration,passed):
    x = passed / duration
    return start+(end-start)*(1-(1-x)**5)
animate = animate2
def color(name):
    #return {"bg-normal":"#6400E6","bg-entered":"black","bg-pressed":"grey"}.get(name)
    #return {"bg-normal":"black","bg-entered":"grey","bg-pressed":"lightgrey","fg-normal":"white"}.get(name)
    return colordic.get(name)
FONT = ""

def lang(key,default=None):
    return langdic.get(key,default if default is not None else key.split('.')[-1])
def config(key,default=None):
    return confdic.get(key,default if default is not None else key.split('.')[-1])

def get_all_apps_win():
    lst = set()
    for path,dirs,files in os.walk(APPS_WIN_USR):
        for f in files:
            if f.endswith(".lnk"):
                lst.add(os.path.join(path,f))

    for path,dirs,files in os.walk(APPS_WIN_ALL):
        for f in files:
            if f.endswith(".lnk"):
                lst.add((f[:-4],os.path.join(path,f)))

    res = []
    environ = dict(os.environ).items()
    for name, file in list(lst):
        path, args = getlnkfrom.get_lnk_file(file)
        #args = args or ''
        for k, v in environ:
            path = path.replace("%%%s%%"%k, v)
        if not os.path.exists(path):
            continue
        command = lambda file=file: os.startfile(file)
        res.append((name,path,command))

    global APPS_WIN_UWP, UWP_APPID_MATCH, UWP_ICONPATH_MATCH
    APPS_WIN_UWP = APPS_WIN_UWP
    UWP_APPID_MATCH = UWP_APPID_MATCH
    UWP_ICONPATH_MATCH = UWP_ICONPATH_MATCH

    if not os.path.exists(APPS_WIN_UWP):
        APPS_WIN_UWP = '' # win7 and lower, the current dir have no uwp appx so nothing
    # below tested in Windows11 Enterprise 23H2 (22631.2050)
    for fold in os.listdir(APPS_WIN_UWP):
        # get all apps fold like xxx.xxx_000.0.0.0_xxx__xxxx
        # get the uwp apps
        match = UWP_MATCH.search(fold)
        if match is None:
            continue

        groups = match.groups()
        if not all(groups):
            continue

        # open the appxmanifest.xml
        # and get the appid and icon path
        with open(APPS_WIN_UWP+'\\'+fold+"\\AppxManifest.xml",'r',encoding='latin-1') as f:
            data = f.read()
        appid = UWP_APPID_MATCH.search(data)
        if appid is None:
            continue
        iconpath = UWP_ICONPATH_MATCH.search(data)
        if iconpath is None:
            continue

        appid = appid.groups()[0]
        command = lambda a=groups[0],b=groups[1],c=appid:os.popen("explorer shell:AppsFolder\\%s_%s!%s"%(a,b,c)) and None # return None
        img = APPS_WIN_UWP+'\\'+fold+"\\" + iconpath.groups()[0]
        if not os.path.exists(img):
            img = img.replace(".png",".scale-200.png")
            # some icons are not there so change to another iconfile.

        res.append((groups[0].split('.')[-1],img,command))

    return sorted(res,key=lambda l:l[0]) # sorted by name

def get_all_apps():
    if SYSTEM == "Windows":
        return get_all_apps_win()
    else:
        return [("Not supported :(",'',lambda:None)]

class AnimateManager:
    def __init__(self,widget,duration,start,end,before,during,after,aftertime=0):
        self.widget = widget
        self._duration = duration
        self.start = start
        self.end = end
        # functions
        self.before = before
        self.during = during
        self.after = after
        #
        self.aftertime = aftertime
        # the class saves the state of animating
        if not hasattr(widget,"animate"):
            widget.animate = 0
        self.func = animate
        #self.func_extra = []
        self._stopped = 0
        self.framesnum = 0
    def start_animate(self):
        " start an animation with default settings "
        # when there's a animate playing, set 0 to break it
        widget = self.widget
        if widget.animate:
            widget.animate = 0
        else:
            widget.animate = 1
        # prepare
        self.start_time = time.time() + self.aftertime/1000
        self.passed = 0
        self.duration = self._duration / ANIMATIONSPEED
        self.before()
        if ALLOWANIMATION:
            #print(self.aftertime,self.widget)
            widget.after(self.aftertime,self.loop)
        else:
            self.during(self.end)
            self.after()
    """# not used :(
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
            self.during(self.end)
            self.after()
            #print(self.framesnum/self.duration,file=open("testfps.txt",'w+'))
            return
        self.framesnum += 1
        var = self.func(self.start,self.end,self.duration,passed,*self.func_extra)
        self.during(var)
        #if not self._stopped:
        widget.after(ANI_DUR,self.loop)
    """
    def loop(self):
        " the loop of animation "
        " Closure brings an increase of 10~30 fps in inf fps mode. "
        widget = self.widget
        during = self.during
        gettime = time.time
        start_time = self.start_time
        start = self.start
        end = self.end
        func = self.func
        duration = self.duration
        #func_extra = self.func_extra
        after = widget.after
        def loopwork():
            if self._stopped:
                return
            if widget.animate == 0:
                widget.animate = 1
                self.after()
                return
            passed = gettime() - start_time
            if passed >= duration:
                widget.animate = 0
                during(end)
                self.after()
                #print(self.framesnum/passed,file=open("testfps.txt",'w+'))
                return
            self.framesnum += 1
            var = func(start,end,duration,passed)
            during(var)
            after(ANI_DUR,loopwork)
        loopwork()
    """# not used :( slow!
    def loop0(self):
        " the loop of animation "
        " No,LEGB is helpful, but generator is helpless(in fps) "
        def work():
            am = self
            widget = am.widget
            during = am.during
            gettime = time.time
            start_time = am.start_time
            start = am.start
            end = am.end
            func = am.func
            duration = am.duration
            func_extra = am.func_extra
            while 1:
                if am._stopped:
                    return
                if widget.animate == 0:
                    widget.animate = 1
                    am.after()
                    return
                passed = gettime() - start_time
                if passed >= duration:
                    widget.animate = 0
                    during(end)
                    am.after()
                    print(am.framesnum/passed,file=open("testfps.txt",'w+'))
                    return
                am.framesnum += 1
                var = func(start,end,duration,passed,*func_extra)
                during(var)
                yield 1
        gen = work()
        after = self.widget.after
        def loopwork(gen):
            try:
                next(gen)
            except:
                return
            after(ANI_DUR,loopwork,gen)
        loopwork(gen)
    """
    
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

    def __setitem__(self,k,v):
        if k == "command":
            self._command = v
        else:
            super().__setitem__(k,v)

#########################################
## ABOVE COPIED FROM MY OTHER PROJECTS ##
#########################################
        
class Charmspop(tk.Toplevel):
    width = 120
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
        self.sub.geometry("600x160+100-100")
        self.sub.overrideredirect(1)
        self.sub.attributes("-topmost",1)
        self.sub.withdraw()
        self.tf = Timerframe(self.sub)
        self.tf.pack(fill="both",expand=1)
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
        am = AnimateManager(self,0.2,swidth,swidth-self.width,self.before,self.during,self.aftera)
        am.start_animate()
        self.poped = 1
        self.frame.putup()
        global showing
        showing = self
        self.tf.update_min()
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
        #self.tf.updates()
        #self.frame["bg"] = tup_hex((100,0,230))

class Charmspopframe(tk.Frame):
    def __init__(self,master=None,*a,**b):
        super().__init__(master,*a,**b)
        bg = color("bg-charms")
        fg = color("fg-normal")
        self["bg"] = bg
        self.btnwin = Button(self,text=lang("main.win"),font="Simhei 20",fg=fg,compound='top',image=getim.get("win.png"),command=lambda:time.sleep(0.1) or pynput.keyboard.Controller().press(pynput.keyboard.Key.cmd) or pynput.keyboard.Controller().release(pynput.keyboard.Key.cmd) or self.master.disappear())
        #self.btnwin.place(relx=0.5,rely=0.5,width=120,height=120,anchor='center')
        self.btnsch = Button(self,text=lang("main.search"),font="Simhei 20",fg=fg,compound='top',image=getim.get("search.png"),command=self.search)
        self.btnshr = Button(self,text=lang("main.tools"),font="Simhei 20",fg=fg,compound='top',image=getim.get("tools.png"),command=self.tools)
        self.btnlch = Button(self,text=lang("main.launch"),font="Simhei 20",fg=fg,compound='top',image=getim.get("launch.png"),command=self.launch)
        self.btnset = Button(self,text=lang("main.settings"),font="Simhei 20",fg=fg,compound='top',image=getim.get("settings.png"),command=self.setting)
        Button(self,command=lambda:self.master.disappear() or pynput.keyboard.Controller().press(pynput.keyboard.Key.cmd) or pynput.keyboard.Controller().press('d') or pynput.keyboard.Controller().release(pynput.keyboard.Key.cmd)or pynput.keyboard.Controller().release('d')).place(x=0,y=self.winfo_screenheight()-20,width=200,height=20)
        #self.putup()
        self.btnlch.win = Launcherwin(self.master)
        self.btnset.win = Settingswin(self.master)
        self.btnsch.win = Searchwin(self.master)
        self.btnshr.win = Toolswin(self.master)
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
            self.btnwin.place(x=width/2,y=sheight/2,width=swidth,height=120,anchor='center')
            self.btnsch.place(x=width/2,y=sheight/2-240,width=swidth,height=120,anchor='center')
            self.btnshr.place(x=width/2,y=sheight/2-120,width=swidth,height=120,anchor='center')
            self.btnlch.place(x=width/2,y=sheight/2+120,width=swidth,height=120,anchor='center')
            self.btnset.place(x=width/2,y=sheight/2+240,width=swidth,height=120,anchor='center')
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
        """
        # not used :(
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
        """
        place_animate(self.btnwin,0.1,width*1.5,width/2,sheight/2,sheight/2,wait=200,kw={"width":swidth,"height":120,"anchor":"center"})
        place_animate(self.btnsch,0.15,width*1.5,width/2,sheight/2-240,sheight/2-240,wait=340,kw={"width":swidth,"height":120,"anchor":"center"})
        place_animate(self.btnshr,0.12,width*1.5,width/2,sheight/2-120,sheight/2-120,wait=280,kw={"width":swidth,"height":120,"anchor":"center"})
        place_animate(self.btnlch,0.12,width*1.5,width/2,sheight/2+120,sheight/2+120,wait=280,kw={"width":swidth,"height":120,"anchor":"center"})
        place_animate(self.btnset,0.15,width*1.5,width/2,sheight/2+240,sheight/2+240,wait=340,kw={"width":swidth,"height":120,"anchor":"center"})
        #"""
        # handle after
        self.after(700,after)
    def launch(self):
        self.btnlch.win.appear()
    def setting(self):
        self.btnset.win.appear()
    def search(self):
        self.btnsch.win.appear()
    def tools(self):
        self.btnshr.win.appear()

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
        self.look = 0
        #self.fill()

    def _mwhup(self,e):
        if showing != self.master:
            return
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
        if showing != self.master:
            return
        delta = e.delta / 120
        btnframe = self.btnframe
        info = btnframe.place_info()
        btnframe.place(y=int(info["y"])-delta,height=len(self.btns)*80)

        info = btnframe.place_info()
        if int(info["y"]) > 0:
            place_animate(btnframe,0.2,0,0,int(info["y"]),0)
        #elif int(info["y"]) < 140-self.winfo_screenheight():
        #    place_animate(btnframe,0.2,0,0,int(info["y"]),140-self.winfo_screenheight())
        elif int(info["y"])+int(info["height"]) < self.winfo_screenheight()/2:
            self.stopanimate = place_animate(btnframe,0.2,0,0,int(info["y"]),self.winfo_screenheight()/2-int(info["height"]))

    def _mwh(self,e):
        if showing != self.master:
            return
        if SYSTEM == "Windows":
            delta = e.delta / 120 * -3
        else:
            delta = e.delta * -3
        btnframe = self.btnframe
        info = btnframe.place_info()
        btnframe.place(y=int(info["y"])-delta*10,height=len(self.btns)*80)
        info = btnframe.place_info()
        def0 = lambda a: a if a<=0 else 0
        if int(info["y"]) > 0:
            #self.stopanimate()
            self.stopanimate = place_animate(btnframe,0.2,0,0,int(info["y"]),0)
        elif int(info["y"])+int(info["height"]) < self.winfo_screenheight()/2:
            #self.stopanimate()
            self.stopanimate = place_animate(btnframe,0.2,0,0,int(info["y"]),def0(self.winfo_screenheight()/2-int(info["height"])))
        #elif int(info["y"]) < 140-self.winfo_screenheight():
        #    #self.stopanimate()
        #    self.stopanimate = place_animate(btnframe,0.2,0,0,int(info["y"]),140-self.winfo_screenheight())

    def _b1p(self,e):
        self.mouse = (e.x, e.y)

    def _b1r(self,e):
        for btn in self.btns:
            btn._executable = 1
        """ # *1
        info = self.btnframe.place_info()
        if self.look:
            #self.stopanimate = place_animate(self.btnframe,1,0,0,int(info["y"]),int(info['y'])+self.look*100)
            def during(var):
                nonlocal y
                info = self.btnframe.place_info()
                self.btnframe.place(x=0,y=int(info['y'])+(var-y)*self.look)
                y = var
            y = 0
            am = AnimateManager(self.btnframe,1,1,100,lambda:None,during,lambda:None)
            am.start_animate()
        """
        # *1&*2&*3 : 'touch' experience, developing, hided

    def _mofm(self,e):
        if showing != self.master:
            return
        x = e.x
        y = e.y
        ox,oy = self.mouse
        if ox == 0 and oy == 0:
            self.mouse = (x,y)
            return
        for btn in self.btns:
            btn._executable = 0

        #self.stopanimate()
        info = self.btnframe.place_info()

        if (oy-y)*1.4 > 0:
            # up
            self.look = -1
        else:
            # down
            self.look = 1

        if int(info["y"]) > 0:
            #self.btnframe.place(y=0)
            #self.stopanimate = place_animate(self.btnframe,0.2,0,0,int(info["y"]),0) # *2
            self.look = 0
            return
        elif int(info["y"])+int(info["height"]) < self.winfo_screenheight()/2:
            def0 = lambda a: a if a<=0 else 0
            #self.stopanimate = place_animate(self.btnframe,0.2,0,0,int(info["y"]),def0(self.winfo_screenheight()/2-int(info["height"]))) # *3
            self.look = 0
            return
            #self.btnframe.place(y=140-self.winfo_screenheight())
        self.btnframe.place(y=int(info["y"])-(oy-y)*1.4,height=len(self.btns)*80)

    def fill(self):
        for w in self.btns:
            w.destory()
        self.btns.clear()
        idx = 0
        for name, path in get_all_apps():
            if not path.endswith(".lnk"):
                #print("not lnk,passed  ",path )
                continue
            if not ".exe" in getlnkfrom.get_lnk_file(path):
                print("not exe,passed  ",getlnkfrom.get_lnk_file(path) )
                #print("not exe,passed  ",path)
                continue
            #if not os.path.exists(getlnkfrom.get_lnk_file(path)):
            #    #print("not zai,passed  ",getlnkfrom.get_lnk_file(path) )
            #    continue
            btn = Button(self.btnframe,text=name,compound="left",font="Simhei 32",anchor='w',padx=20)
            btn["command"] = lambda path=path,self=self:(os.startfile(getlnkfrom.get_lnk_file(path)) or self.master.disappear() or self.master.master.disappear())
            #btn.place(x=40,y=100+idx*80,height=80,width=self.master.width-80)
            btn.place(x=0,y=idx*80,height=80,width=self.lw)
            btn.path = path
            btn.y = idx*80
            btn.stop = lambda:None
            self.btns.append(btn)
            idx += 1
        threading.Thread(target=self.geticons,daemon=1).start()

    def fill(self):
        for w in self.btns:
            w.destory()
        self.btns.clear()
        idx = 0
        for name, path, command in get_all_apps():
            btn = Button(self.btnframe,text=name,compound="left",font="Simhei 32",anchor='w',padx=20)
            btn["command"] = lambda path=path,self=self, command=command:(command() or self.master.disappear() or self.master.master.disappear())
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
            #path = getlnkfrom.get_lnk_file(path)[0]
            if path.endswith(".exe"):
                try:
                    rgb = geticon.rgb(geticon.get_raw_data(path,0,32),32,32)
                    im = Image.new("RGB",(32,32))
                    im.frombytes(rgb)
                except Exception as e:
                    #print(e,path)
                    #continue
                    im = Image.new("RGBA",(32,32))
            elif path.endswith(".png"):
                try:
                    im = Image.open(path).resize((32,32))
                except:
                    continue
            imt = ImageTk.PhotoImage(im)
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
        aniwait = 1
        info = self.btnframe.place_info()
        for btn in self.btns:
            btn.stop()
            btn.place_forget()
            if 0-240 <= btn.y+80+int(info['y']) <= int(info["height"])+80+240:
                btn.stop = place_animate(btn,0.3 if t else 0.6,self.lw,0,btn.y,btn.y,t,aniwait*20,kw={"width":self.lw,"height":80})
                aniwait += 1
            else:
                btn.place(x=0,y=btn.y,width=self.lw,height=80)
            wait += 1

class Settingsframe(tk.Frame):
    def __init__(self,master,*a,**b):
        super().__init__(master,*a,**b)
        self["bg"] = color("bg-normal")
        self.back = Button(self,text="<-",font="Simhei 24",command=self.master.disappear)
        self.back.place(x=20,y=20)
        self.titlel = tk.Label(self,text=lang("settings.title"),font="Simhei 24",bg=color("bg-normal"),fg=color("fg-normal"))
        self.titlel.place(x=80,y=20)
        self.exitbtn = Button(self,text=lang("settings.exit"),font="Simhei 24",bg=color("bg-normal"),fg=color("fg-normal"),command=lambda:root.destroy()or sys.exit)
        self.exitbtn.place(x=460,y=20,anchor='ne')
        #self.exitbtn._command = self.master.appear # a test
        

    def appear(self):
        #if not self.btns:
        #    self.fill()
        self._change()

    def disappear(self):
        self._change(True)

    def _change(self,t=False):
        place_animate(self.back,0.6,20+self.master.width,20,20,20,t)
        place_animate(self.titlel,0.7,80+self.master.width,80,20,20,t)
        place_animate(self.exitbtn,0.8,80+self.master.width+460,self.master.width-20,20,20,t)
        wait = 1
        """
        for btn in self.btns:
            btn.place_forget()
            btn.stop()
            btn.stop = place_animate(btn,0.2 if t else 0.4-wait*0.02,self.lw,0,btn.y,btn.y,t,wait*100,kw={"width":self.lw,"height":80})
            wait += 1
        """

class Searchframe(tk.Frame):
    def __init__(self,master,*a,**b):
        super().__init__(master,*a,**b)
        self["bg"] = color("bg-normal")
        self.back = Button(self,text="<-",font="Simhei 24",command=self.master.disappear)
        self.back.place(x=20,y=20)
        self.titlel = tk.Label(self,text=lang("search.title"),font="Simhei 24",bg=color("bg-normal"),fg=color("fg-normal"))
        self.titlel.place(x=80,y=20)
        self.entry = tk.Entry(self,relief="flat",bd=2,bg=color("bge-normal"),highlightcolor="grey",font="Simhei 24")
        #print(self.entry.config())
        self.entry.place(x=20,y=80,width=self.master.width-40)
        tk.Label(self,text="Too hard. try it latttttter.",bg=color("bg-normal"),fg=color("fg-normal"),font="Simhei 24").place(x=20,y=120)

    def appear(self):
        #if not self.btns:
        #    self.fill()
        self._change()

    def disappear(self):
        self._change(True)

    def _change(self,t=False):
        place_animate(self.back,0.6,20+self.master.width,20,20,20,t)
        place_animate(self.titlel,0.7,80+self.master.width,80,20,20,t)
        place_animate(self.entry,0.6,self.master.width-20,20,80,80,t)
        wait = 1
        """
        for btn in self.btns:
            btn.place_forget()
            btn.stop()
            btn.stop = place_animate(btn,0.2 if t else 0.4-wait*0.02,self.lw,0,btn.y,btn.y,t,wait*100,kw={"width":self.lw,"height":80})
            wait += 1
        """

class Toolsframe(tk.Frame):
    def __init__(self,master,*a,**b):
        super().__init__(master,*a,**b)
        self["bg"] = color("bg-normal")
        self.back = Button(self,text="<-",font="Simhei 24",command=self.master.disappear)
        self.back.place(x=20,y=20)
        self.titlel = tk.Label(self,text=lang("tools.title"),font="Simhei 24",bg=color("bg-normal"),fg=color("fg-normal"))
        self.titlel.place(x=80,y=20)
        self.lw = self.master.width-80
        self.frame = tk.Frame(self,bg=color("bg-normal"))
        self.frame.place(x=40,y=100,width=self.lw,height=self.winfo_screenheight()-140)
        btnframe = self.btnframe = tk.Frame(self.frame,bg=color("bg-normal"),)
        btnframe.place(x=0,y=0,width=self.lw,height=self.winfo_screenheight()-140)
        btnframe.bind_all("<MouseWheel>",self._mwh,1)
        btnframe.bind_all("<Button-4>",self._mwhup,1)
        btnframe.bind_all("<Button-5>",self._mwhdn,1)
        btnframe.bind_all("<B1-Motion>",self._mofm,1)
        btnframe.bind_all("<ButtonPress-1>",self._b1p,1)
        btnframe.bind_all("<ButtonRelease-1>",self._b1r,1)
        self.btns = []

        idx = 0
        no = lambda:None
        lst = (("tools.shot","shot.png",no),("tools.clipman","clipman.png",no),("tools.note","note.png",self.note),("tools.clock","clock.png",no),("tools.filetmp","filetmp.png",no),("tools.mkcolor","mkcolor.png",no),("tools.numcovert","numcovert.png",no))
        for langkey, img, command in lst:
            btn = Button(self.btnframe,text=lang(langkey),image=getim.get(img),compound="left",font="Simhei 32",anchor='w',padx=20,command=command)
            #btn._command = command
            btn.place(x=0,y=idx*80,height=80,width=self.lw)
            btn.y = idx*80
            btn.stop = lambda:None
            self.btns.append(btn)
            idx += 1
        self.fnote = Noteframe(self.master)
        
    def _mwhup(self,e):
        if showing != self.master:
            return
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
        if showing != self.master:
            return
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
        if showing != self.master:
            return
        if SYSTEM == "Windows":
            delta = e.delta / 120 * -3
        else:
            delta = e.delta * -3
        btnframe = self.btnframe
        info = btnframe.place_info()
        btnframe.place(y=int(info["y"])-delta*10,height=len(self.btns)*80)
        info = btnframe.place_info()
        def0 = lambda a: a if a<=0 else 0
        if int(info["y"]) > 0:
            self.stopanimate = place_animate(btnframe,0.2,0,0,int(info["y"]),0)
        #elif int(info["y"]) < 140-self.winfo_screenheight():
        #    self.stopanimate = place_animate(btnframe,0.2,0,0,int(info["y"]),140-self.winfo_screenheight())
        elif int(info["y"])+int(info["height"]) < self.winfo_screenheight()/2:
            self.stopanimate = place_animate(btnframe,0.2,0,0,int(info["y"]),def0(self.winfo_screenheight()/2-int(info["height"])))

    def _b1p(self,e):
        self.mouse = (e.x, e.y)

    def _b1r(self,e):
        for btn in self.btns:
            btn._executable = 1

    def _mofm(self,e):
        if showing != self.master:
            return
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

    def appear(self):
        #if not self.btns:
        #    self.fill()
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
            btn.stop = place_animate(btn,0.2 if t else 0.4,self.lw,0,btn.y,btn.y,t,wait*30,kw={"width":self.lw,"height":80})
            wait += 1
    def _chang2e(self,t=False):
        place_animate(self.back,0.6,20+self.master.width,20,20,20,t)
        place_animate(self.titlel,0.7,80+self.master.width,80,20,20,t)
        wait = 1
        for btn in reversed(self.btns):
            #btn.place_forget()
            btn.stop()
            btn.stop = place_animate(btn,0.3 if t else 0.6,self.lw,0,btn.y,btn.y,t,wait*30,kw={"width":self.lw,"height":80})
            wait += 1
    def takeshot(self):
        pass
    def note(self):
        self.fnote.appear()

class Subframe(tk.Frame):
    LANG = "subwin"
    def __init__(self,master=None,*a,**b):
        super().__init__(master,*a,**b)
        self["bg"] = color("bg-normal")
        self.back = Button(self,text="<-",font="Simhei 24",command=self.disappear)
        self.back.place(x=20,y=20)
        self.titlel = tk.Label(self,text=lang(self.LANG),font="Simhei 24",bg=color("bg-normal"),fg=color("fg-normal"))
        self.titlel.place(x=80,y=20)
        self._init()

    def _init(self):
        pass

    def _appear(self):
        pass

    def _disappear(self):
        pass

    def appear(self):
        frm = self.master.frame
        frm.disappear()
        #frm.place_forget()
        #print(self.master)
        #print(self.master.winfo_width())
        #self.place(height=self.master.winfo_height(),x=0,y=0,width=self.master.winfo_width())
        place_animate(self,0.2,self.master.winfo_width(),0,0,0,wait=100,kw={"width":self.master.winfo_width(),"height":self.winfo_screenheight()})
        self._appear()
        #self["bg"] = "black"
        #tk.Button(self,command=self.disappear,text="<-").place(x=20,y=20,width=40,height=40)
        place_animate(self.back,0.6,20+self.master.width,20,20,20)
        place_animate(self.titlel,0.7,80+self.master.width,80,20,20)
    def disappear(self):
        frm = self.master.frame
        #frm.disappear()
        #frm.place_forget()
        #print(self.master)
        #print(self.master.winfo_width())
        #self.place(height=self.master.winfo_height(),x=0,y=0,width=self.master.winfo_width())
        place_animate(self,0.2,0,self.master.winfo_width(),0,0,wait=100,kw={"width":self.master.winfo_width(),"height":self.winfo_screenheight()})
        self._disappear()
        frm.appear()
        place_animate(self.back,0.6,20+self.master.width,20,20,20,1)
        place_animate(self.titlel,0.7,80+self.master.width,80,20,20,1)

class Noteframe(Subframe):
    LANG = "tools.note"
    def _init(self):
        #self.
        pass

class Basicwin(tk.Toplevel):
    width = 480
    Frame = tk.Frame
    def __init__(self,master,*a,**b):
        super().__init__(master,*a,**b)
        self.overrideredirect(1)
        self.withdraw()
        self.protocol("WM_DELETE_WINDOW",lambda:None)
        self.frame = self.Frame(self)
        self.frame.pack(fill="both",expand=1)
        self.update()
    def appear(self):
        swidth = self.winfo_screenwidth()
        sheight = self.winfo_screenheight()
        width = self.master.width
        self.geometry("%dx%d+%d+0"%(self.width,sheight,swidth-width))
        self.attributes("-topmost",1,"-alpha",0.4)
        am = AnimateManager(self,0.6,0,1,lambda:None,self.during,lambda geo="+%d+0"%((self.master.width-self.width)+swidth-self.master.width):self.geometry(geo))
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
        self.after(400*ALLOWANIMATION,self.master.deiconify)
        self.after(400*ALLOWANIMATION,self.withdraw)
        global showing
        showing = self.master
    def disduring(self,var):
        swidth = self.winfo_screenwidth()
        sheight = self.winfo_screenheight() # 0 swidth-self.master.width   1 swidth-self.width
        x = (self.master.width-self.width) * var + swidth - self.master.width
        self.geometry("+%d+0"%x)
        self.attributes("-alpha",0.2*var+0.4)

class Launcherwin(Basicwin):
    width = 480
    Frame = Launcherframe

class Settingswin(Basicwin):
    width = 480
    Frame = Settingsframe

class Searchwin(Basicwin):
    width = 480
    Frame = Searchframe

class Toolswin(Basicwin):
    width = 480
    Frame = Toolsframe

class Timerframe(tk.Frame):
    def __init__(self,master=None,*a,**b):
        super().__init__(master,*a,**b)
        self["bg"] = "black"
        self.ltm = tk.Label(self,text="11:45",font="Simhei 90",bg="black",fg="white")
        self.ltm.place(x=20,rely=0.5,anchor='w')
        self.lts = tk.Label(self,text=":14",font="Simhei 36",bg="black",fg="white")
        self.lts.place(x=320,y=30)
        self.lwk = tk.Label(self,text="Mon",font="Simhei 36",bg="black",fg="white")
        self.lwk.place(x=420,y=30)
        self.ldy = tk.Label(self,text="19/19",font="Simhei 36",bg="black",fg="white")
        self.ldy.place(x=330,y=80)
        self.update_min()
        tk.Label(self,text="CharmsIt",font="Simsun 20",bg="black",fg="white").place(x=470,y=90)
        self.updates()
    def update_min(self):
        self.ltm["text"] = time.strftime("%H:%M")
        self.lwk["text"] = lang("main.day%s"%time.strftime("%w"))
        self.ldy["text"] = time.strftime("%m/%d")
    def updates(self):
        if self.master.master.poped:
            self.lts["text"] = time.strftime(":%S")
            if int(time.strftime("%S")) <= 2:
                self.update_min()
        self.after(100,self.updates)

class Popinvokewin(tk.Toplevel):
    def __init__(self,master=None,*a,**b):
        super().__init__(master,*a,**b)
        self.overrideredirect(1)
        self.geometry("2x%d+%d+0"%(self.winfo_screenheight(),self.winfo_screenwidth()-2))
        frm = tk.Frame(self,bg="black")
        frm.place(x=0,y=0,width=2,relheight=1)
        frm.bind("<B1-Motion>",self.motion,1)
    def motion(self,e):
        if e.x < -20:
            pop.popup()

def checkpopup1():
    " not good:( place your pointers to the right 30px of screen for 1 sec. "
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
    root.after(300,checkpopup1)

def checkpopup2():
    " similar to win8 -- but with bug:) "
    swidth = root.winfo_screenwidth()
    sheight = root.winfo_screenheight()
    mx,my = root.winfo_pointerxy()
    if swidth-mx > 30:
        root.clock = 16
    elif not pop.poped:
        #print(mx,my)
        if root.clock==16 and mx+1==swidth and (my==0 or my==sheight-1):
            root.clock = 1
            root.my = my
        elif mx+1!=swidth:
            root.my = -sheight*2
        else:
            root.clock -= time.time()-root.now
            if root.clock >= 0 and mx+1==swidth and abs(my-root.my)*3>=swidth:
                pop.popup()
                root.clock = 16
            elif root.clock<0 or mx+1!=swidth:
                root.my = -sheight*2
    root.now = time.time()
    root.after(100,checkpopup2)

checkpopup = checkpopup1

def place_animate(wid,t,xs,xe,ys,ye,reverse=False,wait=0,kw=None):
    if not kw:
        kw = {}
    # legb
    xe = xe
    ye = ye
    xx = xe-xs
    yy = ye-ys
    def during(var):
        wid.place(x=xx*var+xs,y=yy*var+ys,**kw)
    def after():
        wid.place(x=xe,y=ye,**kw)
    am = AnimateManager(wid,t,0,1,lambda:None,during,after,aftertime=wait)
    if reverse:
        am = AnimateManager(wid,t,1,0,lambda:None,during,after,aftertime=wait)
    am.start_animate()
    return am.stop

if __name__ == "__main__":
    with open("config.json",'r') as f:
        confdic = json.loads(f.read())
    try:
        with open("lang/%s.json"%(config("main.language")),'r') as f:
            langdic = json.loads(f.read())
    except:
        langdic = {}
    colordic = getim.colordic
    ANI_DUR = int(1000 / (config("main.fps",30)or 30)) - 2
    if ANI_DUR <= 0:
        ANI_DUR = 1
    ALLOWANIMATION = bool(config("main.animation",1))
    root = tk.Tk()
    root.withdraw()
    if config("main.launchscreen",1):
        charmsit = tk.Toplevel()
        charmsit.overrideredirect(1)
        charmsit.geometry("300x160+%d+%d"%((root.winfo_screenwidth()-300)//2,(root.winfo_screenheight()-160)//2))
        tk.Label(charmsit,text="CharmsIt",font="Simsun 48",bg=color("bg-normal"),fg=color("fg-normal")).place(x=150,y=80,anchor="center",width=300,height=160)
        tk.Label(charmsit,text=VERSION,font="Simsun 20",bg=color("bg-normal"),fg=color("fg-normal")).place(x=280,y=120,anchor='e')
        charmsit.attributes("-alpha",0,"-topmost",1)
        for i in range(0,10,1):
            #charmsit.attributes("-alpha",i/10)
            charmsit.attributes("-alpha",animate(0,1,10,i))
            charmsit.update()
            time.sleep(0.03*ALLOWANIMATION)
        time.sleep(0.5+(0 if ALLOWANIMATION else 0.6))
        for i in range(10,-1,-1):
            #charmsit.attributes("-alpha",i/10)
            charmsit.attributes("-alpha",animate(0,1,10,i))
            charmsit.update()
            time.sleep(0.03*ALLOWANIMATION)
        charmsit.destroy()
        del charmsit

    root.now = time.time()
    root.clock = 0
    root.my = -2 * root.winfo_screenheight()
    pop = Charmspop()
    pop.withdraw()
    pop.overrideredirect(1)
    pop.attributes("-topmost",1)
    pop.bindall()
    showing = pop
    checkpopup()
    #pop.popup()
    #pop.disappear()
    #Popinvokewin()
    #root.after(0,pop.popup())
    root.mainloop()
