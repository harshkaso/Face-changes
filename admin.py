#!/usr/bin/env python3
import RPi.GPIO as GPIO
from tkinter import Tk, Frame, Toplevel
from tkinter import messagebox, PhotoImage, Label, Button, Entry
from tkinter import CENTER, TOP, W, E, N, S, NW, NE, HORIZONTAL
from tkinter.ttk import Progressbar, Combobox

import os
import cv2
from PIL import Image,ImageTk
import sys
import time
import bcrypt
import imutils
import service
import _thread as thread
import train_model as tm
import extract_embeddings as ee
from datetime import datetime
from imutils.video import VideoStream

BG_COLOR = '#dfedfa'
CAP_ICON = 'icons/cap.png'
TRAIN_ICON = 'icons/train.png'
ADMIN_ICON = 'icons/admin.png'
NAV_CAP = 'icons/navcap.png'
NAV_TRAIN = 'icons/navtrain.png'
BACK = 'icons/back.png'
REGISTER = 'icons/register.png'
LOGOUT_ICON = "icons/logout.png"
FONT_1 = "Helvetica 15 bold"
FONT_2 = "Helvetica 13"
FONT_3 = "Helvetica 11"
GPIO.setmode(GPIO.BCM)
GPIO.setup(16,GPIO.OUT) # YELLOW LED
GPIO.output(16,GPIO.LOW)
GPIO.setup(26,GPIO.OUT) # GREEN LED
GPIO.output(26,GPIO.LOW)
GPIO.setup(12,GPIO.OUT) # RED LED
GPIO.output(12,GPIO.LOW)

class Admin:
    def __init__(self):
        window.title('ADMINISTRATOR')
        window.configure(bg=BG_COLOR)
        w=800
        h=480
        ws = window.winfo_screenwidth()
        hs = window.winfo_screenheight() 
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        window.geometry('%dx%d+%d+%d' % (ws, hs, 0, 0))
        window.minsize(width=w, height=h)
        window.resizable(0, 0)
        window.protocol("WM_DELETE_WINDOW", self.cleanup)
        window.attributes('-zoomed', True)
        self.testLEDON()
        window.after(500, self.testLEDOFF)

        self.show_frame(Login)

    def show_frame(self, cont, args=[]):
        frame = cont(window, self, args)
        frame.place(relwidth=1, relheight=1)
        frame.tkraise()

    
    def testLEDON(self):
        GPIO.output(12,GPIO.HIGH)
        GPIO.output(16,GPIO.HIGH)
        GPIO.output(26,GPIO.HIGH)
    
    def testLEDOFF(self):
        GPIO.output(12,GPIO.LOW)
        GPIO.output(16,GPIO.LOW)
        GPIO.output(26,GPIO.LOW)        
    
    def cleanup(self):
        GPIO.cleanup()
        sys.exit(0)
        
class Login(Frame):
    def __init__(self, parent, controller, args):
        Frame.__init__(self, parent)
        Frame.config(self, bg=BG_COLOR)

        adminIcon = PhotoImage(file=ADMIN_ICON)
        admin = Label(self, image=adminIcon, bg=BG_COLOR)
        admin.place(relx=0.53, rely=0.25, anchor=CENTER)
        admin.image = adminIcon

        userLabel = Label(self, text="Username : ", bg=BG_COLOR, font = FONT_1)
        userLabel.place(relx=0.43, rely=0.45, anchor=E)

        username = Entry(self, font = FONT_3)
        username.place(relx=0.53, rely=0.45, anchor=CENTER)

        passLabel = Label(self, text="Password : ", bg=BG_COLOR, font = FONT_1)
        passLabel.place(relx=0.43, rely=0.55, anchor=E)

        password = Entry(self, show="*",font = FONT_3)
        password.place(relx=0.53, rely=0.55, anchor=CENTER)

        login = Button(self, text='LOGIN', cursor='hand2', bg="#6497b1" , font=FONT_2)
        login.place(relx=0.53, rely=0.65, width=150, height=35, anchor=CENTER)
        login.bind("<1>", lambda valid: self.validate(username.get().strip(), password.get().strip(), controller))
        login.bind("<space>", lambda valid: self.validate(username.get().strip(), password.get().strip(), controller))
        

    def validate(self, username, password, controller):
        cntrl1 = b'$2b$12$KPbd8CaCt.nrFDnrvB/dFOJHtvnyTeMj/zFlQAOsip0XWWZ.CGgFu'
        cntrl2 = b'$2b$12$0r6O9ff0WLZOqYvzsIInturrd0PviwIVsK.JFD1EjBWkg9J69/O9C'
        if not username or not password:
            GPIO.output(12,GPIO.HIGH)
            messagebox.showwarning("Warning", "Both fields are required")
            GPIO.output(12,GPIO.LOW)
            return
        if bcrypt.checkpw(username.encode('ascii'), cntrl1)  and bcrypt.checkpw(password.encode('ascii'), cntrl2):
            GPIO.output(26,GPIO.HIGH)
            self.after(400, lambda: GPIO.output(26,GPIO.LOW))
            controller.show_frame(Nav)
        else:
            GPIO.output(12,GPIO.HIGH)
            messagebox.showwarning("Warning", "Invalid Credentials")
            GPIO.output(12,GPIO.LOW)
class Nav(Frame):
    def __init__(self, parent, controller, args):
        Frame.__init__(self, parent)
        Frame.config(self, bg=BG_COLOR)

        cap = PhotoImage(file=NAV_CAP)
        NavCap = Label(self, compound=TOP, text="CAPTURE", font="GoodTimes 15 bold", cursor='hand2', image=cap, bg=BG_COLOR)
        NavCap.place(relx=0.195, rely=0.45, anchor=CENTER)
        NavCap.image = cap
        NavCap.bind("<1>", lambda command: controller.show_frame(Dataset))

        train = PhotoImage(file=NAV_TRAIN)
        NavTrain = Label(self, compound=TOP, text="TRAIN", font="GoodTimes 15 bold", cursor='hand2', image=train, bg=BG_COLOR)
        NavTrain.place(relx=0.505, rely=0.45, anchor=CENTER)
        NavTrain.image = train
        NavTrain.bind("<1>", lambda command: controller.show_frame(Train))
        
        register = PhotoImage(file=REGISTER)
        NavRegister = Label(self, compound=TOP, text="REGISTER", font="GoodTimes 15 bold", cursor='hand2', image=register, bg=BG_COLOR)
        NavRegister.place(relx=0.815, rely=0.45, anchor=CENTER)
        NavRegister.image = register
        NavRegister.bind("<1>", lambda command: controller.show_frame(Register))
        
        logoutIcon = PhotoImage(file=LOGOUT_ICON)
        logout = Label(self, image=logoutIcon, cursor='hand2', bg=BG_COLOR)
        logout.place(relx=0.99, rely=0.01, anchor=NE)
        logout.image = logoutIcon
        logout.bind("<1>", lambda command: controller.show_frame(Login))

class Dataset(Frame):
    def __init__(self, parent, controller, args):
        Frame.__init__(self, parent)
        Frame.config(self, bg=BG_COLOR)

        backIcon = PhotoImage(file=BACK)
        back = Label(self, image=backIcon, cursor="hand2", bg=BG_COLOR)
        back.place(relx=0, rely=0, anchor=NW)
        back.image = backIcon
        back.bind("<1>", lambda command: controller.show_frame(Nav))

         
        companyLabel = Label(self, text="Company : ", bg=BG_COLOR, font = FONT_2 )
        companyLabel.place(relx=0.4, rely=0.25, anchor=E)
        
        companyList = service.getAllCompanyNames()
        company = Combobox(self, values=companyList, state='readonly', font = FONT_3 )
        company.current()
        company.place(relx=0.4, rely=0.25, anchor=W)

        codeLabel = Label(self, text="Employee Code : ", bg=BG_COLOR, font = FONT_2)
        codeLabel.place(relx=0.4, rely=0.35, anchor=E)

        eCode = Entry(self, font = FONT_3)
        eCode.place(relx=0.5, rely=0.35, anchor=CENTER)

        nameLabel = Label(self, text="Name : ", bg=BG_COLOR, font = FONT_2)
        nameLabel.place(relx=0.4, rely=0.45, anchor=E)
        name = Entry(self, font = FONT_3)
        name.place(relx=0.5, rely=0.45, anchor=CENTER)

        #capIcon = PhotoImage(file=CAP_ICON)
        #self.cap = Label(self, compound=TOP, text="Capture Data", font='Helvatica 10 bold', cursor='hand2', image=capIcon ,bg=BG_COLOR)
        self.cap = Button(self, text='Capture Dataset', cursor='hand2', bg="#6497b1" , font = FONT_2)
        self.cap.place(relx=0.5, rely=0.65, anchor=CENTER)
        self.cap.bind("<1>", lambda command: self.capture_dataset(company.get().strip(), eCode.get().strip(), name.get().strip(), controller))
        #self.cap.image = capIcon
        
        logoutIcon = PhotoImage(file=LOGOUT_ICON)
        logout = Label(self, image=logoutIcon, cursor='hand2', bg=BG_COLOR)
        logout.place(relx=0.99, rely=0.01, anchor=NE)
        logout.image = logoutIcon
        logout.bind("<1>", lambda command: controller.show_frame(Login))
    
    def capture_dataset(self, company, empCode, name, controller):
        state = str(self.cap['state'])
        if state == 'active':
            self.cap['state'] = 'disabled'
            window.update_idletasks()
            if not (company and empCode and name):
                GPIO.output(12,GPIO.HIGH)
                messagebox.showwarning("Warning", "All the fields are required")
                self.cap['state'] = 'normal'
                GPIO.output(12,GPIO.LOW)
                return
            status, message, companyId = service.getCompanyId(company)
            if not companyId and status == 404:
                GPIO.output(12,GPIO.HIGH)
                messagebox.showwarning("Warning", message)
                self.cap['state'] = 'normal'
                GPIO.output(12,GPIO.LOW)
                return
            if service.checkEmployeeExists(companyId, empCode):
                GPIO.output(12,GPIO.HIGH)
                messagebox.showwarning("Warning", "Employee already exists")
                self.cap['state'] = 'normal'
                GPIO.output(12,GPIO.LOW)
                return
            self.w = CaptureDataset(companyId, company, empCode, name, controller)
            window.wait_window(self.w.top)
            controller.show_frame(Dataset)
    
class CaptureDataset(object):
    def __init__(self, companyId, company, empCode, name, controller):
        self.go_ahead = False
        top = self.top = Toplevel(window)
        top.title("Capture Dataset")
        top.configure(bg=BG_COLOR)
        top.protocol("WM_DELETE_WINDOW", self.cleanup)
        top.iconify()
        self.display = None
        self.cap = Button(top, text="Start Capturing", cursor="hand2")
        self.cap.bind("<1>", lambda command: self.start_capturing(companyId, company, empCode, name, controller))
        self.cap.grid(row=1, column=0, columnspan=2, sticky=N,  pady=[0,20],padx=10)

        self.company = company
        self.empCode = empCode
        self.name = name
        self.running = True
        self.start_cap = False
        self.total = 0
        thread.start_new_thread(self.videoloop, ())
        
    def videoloop(self):
        try:
            CASCADE = "haarcascade.xml"
            INTERVAL = 2
            self.NIMAGES = 15
            detector = cv2.CascadeClassifier(CASCADE)
            self.vs = VideoStream(usePiCamera=True).start()
            time.sleep(0.1)
            start_time = time.time()
            while self.running:
                frame = self.vs.read()
                orig = frame.copy()
                frame = imutils.resize(frame, width=400)
                rects = detector.detectMultiScale(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), scaleFactor=1.1, 
                    minNeighbors=5, minSize=(30, 30))
                for (x, y, w, h) in rects:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                img = ImageTk.PhotoImage(img)
                if self.display == None:
                    self.display = Label(self.top, image=img, bg=BG_COLOR, relief="ridge")
                    self.display.image = img
                    self.display.grid(row=0, column=0, columnspan=2, sticky=W+E+N+S, padx = 20, pady= 20)
                    self.top.update()
                    w = self.top.winfo_width()
                    h = self.top.winfo_height()
                    ws = self.top.winfo_screenwidth()
                    hs = self.top.winfo_screenheight()
                    x = (ws/2) - (w/2)
                    y = (hs/2) - (h/2)
                    self.top.geometry('%dx%d+%d+%d' % (w, h, x, y))
                    self.top.deiconify()
                else:
                    self.display.configure(image = img)
                    self.display.image = img
                
                elapsed_time = time.time() - start_time
                
                if self.start_cap and elapsed_time >= INTERVAL:
                    OUTPUT = self.dirName
                    p = os.path.sep.join([OUTPUT, "{}.png".format(str(self.total).zfill(5))])
                    cv2.imwrite(p, orig)
                    print("[INFO] Total frame captured: ", self.total)
                    start_time = time.time()
                    self.total += 1
                    if self.total == self.NIMAGES:
                        self.cleanup()
                        break
                    
                    
        except Exception as e:
            print("[WARN] Exception occured in non tkinter thread: ", e)
            
    def start_capturing(self, companyId, company, empCode, name, controller):
        state = str(self.cap['state'])
        print(state)
        if state == 'active':
            GPIO.output(16,GPIO.HIGH)
            self.cap['state'] = "disabled"
            self.cap.configure(text="Please wait while dataset is being captured")

            status, message, empId = service.addNewEmployee(companyId, empCode, name)
            if status == 200 and empId:
                message = "Something went wrong, employee added to database but dataset is not captured!"
                self.dirName = f'Clients/{company}/dataset/{empId}'
                if not os.path.exists(self.dirName):
                    os.makedirs(self.dirName)
                self.start_cap = True
                window.wait_window(self.top)
                GPIO.output(16,GPIO.LOW)
                if self.total == self.NIMAGES:
                    GPIO.output(26,GPIO.HIGH)
                    messagebox.showinfo("Information", "Employee added successfully!")
                    GPIO.output(26,GPIO.LOW)
                    #controller.show_frame(Dataset)
                    return
            GPIO.output(12,GPIO.HIGH)    
            messagebox.showwarning("Warning", message)
            GPIO.output(12,GPIO.LOW)
            

            
    
    def cleanup(self):
        self.start_cap = False
        self.running = False
        self.vs.stop()
        self.top.destroy()
            
    

class Train(Frame):
    def __init__(self, parent, controller, args):
        Frame.__init__(self, parent)
        Frame.config(self, bg=BG_COLOR)

        backIcon = PhotoImage(file=BACK)
        back = Label(self, image=backIcon, cursor="hand2", bg=BG_COLOR)
        back.place(relx=0, rely=0, anchor=NW)
        back.image = backIcon
        back.bind("<1>", lambda command: controller.show_frame(Nav))

        companyLabel = Label(self, text="Company : ", bg=BG_COLOR, font = FONT_2)
        companyLabel.place(relx=0.4, rely=0.35, anchor=E)

        companyList = service.getAllCompanyNames()
        self.company = Combobox(self, values=companyList, state='readonly', font=FONT_3)
        self.company.current()
        self.company.place(relx=0.52, rely=0.35, anchor=CENTER)
        
        #trainIcon = PhotoImage(file=TRAIN_ICON)
        train = Button(self, text='Train Dataset', cursor='hand2', bg="#6497b1" , font = FONT_2)
        #train = Label(self, compound=TOP, text="Train", font='Helvatica 10 bold', cursor='hand2', image=trainIcon, bg=BG_COLOR)
        train.place(relx=0.52, rely=0.6, anchor=CENTER)
        train.bind("<1>", lambda command: controller.show_frame(TrainModel, [self.company.get(), Train]))
        #train.image = trainIcon
        
        logoutIcon = PhotoImage(file=LOGOUT_ICON)
        logout = Label(self, image=logoutIcon, cursor='hand2', bg=BG_COLOR)
        logout.place(relx=0.99, rely=0.01, anchor=NE)
        logout.image = logoutIcon
        logout.bind("<1>", lambda command: controller.show_frame(Login))

class Register(Frame):
    def __init__(self, parent, controller, args):
        Frame.__init__(self, parent)
        Frame.config(self, bg=BG_COLOR)

        backIcon = PhotoImage(file=BACK)
        back = Label(self, image=backIcon, cursor="hand2", bg=BG_COLOR)
        back.place(relx=0, rely=0, anchor=NW)
        back.image = backIcon
        back.bind("<1>", lambda command: controller.show_frame(Nav))

        logoutIcon = PhotoImage(file=LOGOUT_ICON)
        logout = Label(self, image=logoutIcon, cursor='hand2', bg=BG_COLOR)
        logout.place(relx=0.99, rely=0.01, anchor=NE)
        logout.image = logoutIcon
        logout.bind("<1>", lambda command: controller.show_frame(Login))

        compLabel = Label(self, text="Company : ", bg=BG_COLOR , font=FONT_2)
        compLabel.place(relx=0.45, rely=0.3, anchor=E)

        company = Entry(self, font = FONT_3)
        company.place(relx=0.55, rely=0.3, anchor=CENTER)

        passLabel = Label(self, text="Password : ", bg=BG_COLOR, font = FONT_2)
        passLabel.place(relx=0.45, rely=0.4, anchor=E)

        password = Entry(self, show="*", font=FONT_3)
        password.place(relx=0.55, rely=0.4, anchor=CENTER)

        confPassLabel = Label(self, text="Confirm Password : ", bg=BG_COLOR, font = FONT_2 )
        confPassLabel.place(relx=0.45, rely=0.5, anchor=E)

        confirmPassword = Entry(self, show="*", font = FONT_3)
        confirmPassword.place(relx=0.55, rely=0.5, anchor=CENTER)

        reg = Button(self, text='REGISTER', cursor='hand2', bg="#6497b1" , font = FONT_2)
        reg.place(relx=0.55, rely=0.6, width=150, height=35, anchor=CENTER)
        reg.bind("<1>", lambda valid: self.register(company.get().strip(), password.get().strip(), confirmPassword.get().strip(), controller))

    def register(self, company, password, confirmPassword, controller):
        if not (company and password and confirmPassword):
            GPIO.output(12, GPIO.HIGH)
            messagebox.showwarning("Warning", "All the fields are required")
            GPIO.output(12, GPIO.LOW)
            return
        if password != confirmPassword:
            GPIO.output(12, GPIO.HIGH)
            messagebox.showwarning("Warning", "Both Passwords should match")
            GPIO.output(12, GPIO.LOW)
            return
        status, message = service.registerCompany(company, password)
        if status == 201:
            os.makedirs(f'Clients/{company}/dataset')
            os.system(f'cp -r unknown Clients/\"{company}\"/dataset/unknown')
            GPIO.output(26, GPIO.HIGH)
            messagebox.showinfo("Information", message)
            GPIO.output(26, GPIO.LOW)
            controller.show_frame(Register)
            return
        GPIO.output(12, GPIO.HIGH)
        messagebox.showwarning("Warning", message)
        GPIO.output(12, GPIO.LOW)


class TrainModel(Frame):
    def __init__(self, parent, controller, args):
        Frame.__init__(self, parent)
        Frame.config(self, bg=BG_COLOR)
        self.cont = args[1]
        self.trainOnDataset(args[0], controller)

    def trainOnDataset(self, company, controller):
        if not company:
            GPIO.output(12, GPIO.HIGH)
            messagebox.showwarning("Warning", "Company name is required")
            GPIO.output(12, GPIO.LOW)
            
        elif self.confirmTrain(company):
            GPIO.output(16, GPIO.HIGH)
            self.running = True
            self.trained = False
            self.proglab = Label(self, text="Please wait while the model is training ...", bg=BG_COLOR)
            self.proglab.place(relx=0.5, rely=0.4, anchor=CENTER)
            self.progress = Progressbar(self, orient=HORIZONTAL, length=400, mode='indeterminate')
            self.progress.place(relx=0.5, rely=0.5, anchor=CENTER)
            self.progress.start()
            thread.start_new_thread(self.train_thread, (company,controller))
            self.after(20, self.check_thread)
            return
        self.destroy()
        controller.show_frame(self.cont, [company])
            
    def train_thread(self, company, controller):
        try:
            GPIO.output(16, GPIO.HIGH)
            if ee.extract_embeddings(company) and tm.train_model(company):
                status, self.message = service.updateLastTrained(company, datetime.now())
                GPIO.output(16, GPIO.LOW)
                self.running = False
                GPIO.output(26, GPIO.HIGH)
                messagebox.showinfo("Information", self.message)
                GPIO.output(26, GPIO.LOW)
        except Exception as e:
            GPIO.output(16, GPIO.LOW)
            self.running = False
            GPIO.output(12, GPIO.HIGH)
            messagebox.showwarning("Warning", f"Either no dataset for {company} exists or some internal error occured!")
            GPIO.output(12, GPIO.LOW)
            print("Exception occured in non tkinter thread: ", e)
        finally:
            controller.show_frame(self.cont, [company])


    def check_thread(self):
        if self.running:
            self.progress.step()
            self.after(20, self.check_thread)
        else:
            self.progress.stop()
            self.progress.destroy()
            self.proglab.destroy()
            self.destroy()
            
            
    def confirmTrain(self, company):
        status, message = service.getLastTrained(company)
        return messagebox.askyesno("Confirm", message)


window = Tk()
app = Admin()
window.mainloop()