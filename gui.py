#!/usr/bin/env python3
try:
    import RPi.GPIO as GPIO
except:
    print('RPi not found')

from PIL import Image,ImageTk
from tkinter import Tk, Frame, Toplevel
from tkinter import messagebox, simpledialog, PhotoImage, Label, Button, Entry, StringVar
from tkinter import CENTER, N, E, S, W, NE, NW, TOP, END, HORIZONTAL
from tkinter.ttk import Progressbar, Combobox

import os
import sys
import cv2
import time
import imutils 
import subprocess
import _thread as thread
from recognize import face
from datetime import datetime
from imutils.video import VideoStream


import service
import train_model as tm
import extract_embeddings as ee

# SOME GLOBAL CONFIG VARIBALES
RED = 12
YELLOW = 16
GREEN = 26
fullscreen_state = False
BG_COLOR = "#dfedfa"
BACK_ICON = os.path.dirname(os.path.abspath(__file__)) + "/icons/back.png"
MANCAP_ICON = os.path.dirname(os.path.abspath(__file__)) + "/icons/mancap.png"
LOGOUT_ICON = os.path.dirname(os.path.abspath(__file__)) + "/icons/logout.png"
YES_ICON = os.path.dirname(os.path.abspath(__file__)) + "/icons/yes.png"
NO_ICON = os.path.dirname(os.path.abspath(__file__)) + "/icons/no.png"
CAP_ICON = os.path.dirname(os.path.abspath(__file__)) + "/icons/cap.png"
TRAIN_ICON = os.path.dirname(os.path.abspath(__file__)) + "/icons/train.png"
ADMIN_ICON = os.path.dirname(os.path.abspath(__file__)) + "/icons/admin.png"
DETECT_ICON = os.path.dirname(os.path.abspath(__file__)) + "/icons/face-detection.png"
CRUD_ICON = os.path.dirname(os.path.abspath(__file__)) + "/icons/crud.png"
AUTO_ICON = os.path.dirname(os.path.abspath(__file__)) + "/icons/auto.png"
MANUAL_ICON = os.path.dirname(os.path.abspath(__file__)) + "/icons/manual.png"
ADD_ICON = os.path.dirname(os.path.abspath(__file__)) + "/icons/add-user.png"
UPDATE_ICON = os.path.dirname(os.path.abspath(__file__)) + "/icons/update-user.png"
REMOVE_ICON = os.path.dirname(os.path.abspath(__file__)) + "/icons/remove-user.png"
if 'RPi' in sys.modules:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17,GPIO.IN)
    GPIO.setup(16,GPIO.OUT)
    GPIO.output(16,GPIO.LOW)
    GPIO.setup(26,GPIO.OUT)
    GPIO.output(26,GPIO.LOW)
    GPIO.setup(12,GPIO.OUT)
    GPIO.output(12,GPIO.LOW)
    GPIO.setup(5,GPIO.OUT)
    GPIO.output(5,GPIO.LOW)

class Client:
    def __init__(self, window):
        w=800
        h=400
        ws = window.winfo_screenwidth()
        hs = window.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        #window.geometry('%dx%d+%d+%d' % (ws, hs, 0, 0))
        window.minsize(width=w, height=h)
        window.title('FACE')
        window.configure(bg=BG_COLOR)
        window.lift()
        window.attributes('-zoomed', True)
        window.protocol('WM_DELETE_WINDOW', self.closeApp)

        
        self.testLEDON()
        window.after(500, self.testLEDOFF)

        self.show_frame(Login)

        
    def testLEDON(self):
        if 'RPi' in sys.modules:
            GPIO.output(12,GPIO.HIGH)
            GPIO.output(16,GPIO.HIGH)
            GPIO.output(26,GPIO.HIGH)
    
    def testLEDOFF(self):
        if 'RPi' in sys.modules:
            GPIO.output(12,GPIO.LOW)
            GPIO.output(16,GPIO.LOW)
            GPIO.output(26,GPIO.LOW)
    
    def closeApp(self):
        if 'RPi' in sys.modules:
            GPIO.cleanup()
        window.destroy()
        sys.exit(0)


    def show_frame(self, cont, args=[]):
        frame = cont(window, self, args)
        frame.place(relwidth=1, relheight=1)
        frame.focus_set()
        frame.tkraise()
        frame.bind("<1>", lambda event: frame.focus_set())

class Login(Frame):
    def __init__(self, parent, controller, args):
        Frame.__init__(self, parent)
        Frame.config(self, bg=BG_COLOR)
        window.attributes('-fullscreen', False)
        utility.set_fullscreen_state(False)
        admin_icon = PhotoImage(file=ADMIN_ICON)
        admin = Label(self, image=admin_icon, bg=BG_COLOR)
        admin.place(relx=0.5, rely=0.25, anchor=CENTER)
        admin.image = admin_icon

        companyLabel = Label(self, text="Company  : ", bg=BG_COLOR, font = "Helvetica 14 bold")
        companyLabel.place(relx=0.4, rely=0.45, anchor=E)
        company = Entry(self,font = "Helvetica 10")
        company.place(relx=0.5, rely=0.45, anchor=CENTER)
        company.bind("<FocusIn>", lambda command: utility.show_keyboard(100, 275))
        company.bind("<FocusOut>", lambda command: utility.hide_keyboard())    

        passLabel = Label(self, text="Password : ", bg=BG_COLOR, font = "Helvetica 14 bold")
        passLabel.place(relx=0.4, rely=0.55, anchor=E)

        password = Entry(self, show="*", font = "Helvetica 10")
        password.place(relx=0.5, rely=0.55, anchor=CENTER)
        password.bind("<FocusIn>", lambda command: utility.show_keyboard(100, 50))
        password.bind("<FocusOut>", lambda command: utility.hide_keyboard())

        login = Button(self, text='LOGIN', cursor='hand2', bg="#6497b1", font = "Helvetica 12")
        login.place(relx=0.5, rely=0.65, width=150, height=35, anchor=CENTER)
        login.bind("<1>", lambda valid: self.validate(company.get(), password.get(), controller))
        login.bind("<space>", lambda valid: self.validate(company.get(), password.get(), controller))

    
            
    def validate(self, company, password, controller):
        utility.hide_keyboard()
        if not company or not password:
            GPIO.output(12,GPIO.HIGH)
            messagebox.showwarning('Warning', 'Both fields are required')
            GPIO.output(12,GPIO.LOW)
            return 

        (status, message, id) = service.authenticateClient(company, password)
        if status == 200 and id:
            # GPIO.output(26,GPIO.HIGH)
            # self.after(400, lambda: GPIO.output(26,GPIO.LOW))
            msg = f"Welcome to {company}"
            controller.show_frame(Nav, [company.strip()])  
            return

        if status == 401:
            GPIO.output(12,GPIO.HIGH)
            messagebox.showwarning('Warning', message)
            GPIO.output(12,GPIO.LOW)
            return

        if status == 404:
            GPIO.output(12,GPIO.HIGH)
            messagebox.showwarning('Warning', message)
            GPIO.output(12,GPIO.LOW)   
            return
        GPIO.output(12,GPIO,GPIO.HIGH)
        messagebox.showwarning('Warning', 'Something went wrong')
        GPIO.output(12,GPIO.LOW)


class Nav(Frame):
    def __init__(self, parent, controller, args):
        Frame.__init__(self, parent)
        Frame.config(self, bg=BG_COLOR)
        
        crud_icon = PhotoImage(file= CRUD_ICON)
        crud = Label(self, text='CRUD ICON', cursor='hand2', bg=BG_COLOR, image = crud_icon)
        crud.place(relx=0.25, rely=0.5, anchor=CENTER)
        crud.bind("<1>", lambda command: controller.show_frame(Crud, [args[0]]))
        crud.image = crud_icon
        
        detect_icon = PhotoImage(file= DETECT_ICON)
        detect = Label(self, text='DETECT_ICON', cursor='hand2', bg=BG_COLOR, image = detect_icon)
        detect.place(relx=0.75, rely=0.5, anchor=CENTER)
        detect.bind("<1>", lambda command: controller.show_frame(Mode, [args[0]]))
        detect.image = detect_icon
        
        logout_icon = PhotoImage(file=LOGOUT_ICON)
        logout = Label(self, image=logout_icon, cursor='hand2', bg=BG_COLOR)
        logout.place(relx=0.99, rely=0.01, anchor=NE)
        logout.image = logout_icon
        logout.bind("<1>", lambda command: utility.logout_with_pin(controller))
        
    def logout(self, controller):
        controller.show_frame(Login, [])
  
class Crud(Frame):
    def __init__(self, parent, controller, args):
        Frame.__init__(self, parent)
        Frame.config(self, bg=BG_COLOR)

        back_icon = PhotoImage(file=BACK_ICON)
        back = Label(self, image=back_icon, cursor="hand2", bg=BG_COLOR)
        back.place(relx=0, rely=0, anchor=NW)
        back.image = back_icon
        back.bind("<1>", lambda command: utility.back(controller, Nav, [args[0]]))

        logout_icon = PhotoImage(file=LOGOUT_ICON)
        logout = Label(self, image=logout_icon, cursor='hand2', bg=BG_COLOR)
        logout.place(relx=0.99, rely=0.01, anchor=NE)
        logout.image = logout_icon
        logout.bind("<1>", lambda command: utility.logout_with_pin(controller))

        add_icon = PhotoImage(file=ADD_ICON)
        add = Label(self, text='ADD', cursor='hand2', bg=BG_COLOR, image = add_icon)
        add.place(relx=0.215, rely=0.5, anchor=CENTER)
        add.bind("<1>", lambda command: controller.show_frame(Create, [args[0]]))
        add.image = add_icon

        update_icon = PhotoImage(file=UPDATE_ICON)
        update = Label(self, text='UPDATE', cursor='hand2', bg=BG_COLOR, image=update_icon)
        update.place(relx=0.5, rely=0.48, anchor=CENTER)
        update.bind("<1>", lambda command: controller.show_frame(Update, [args[0]]))
        update.image = update_icon

        delete_icon = PhotoImage(file= REMOVE_ICON)
        delete = Label(self, text='DELETE', cursor='hand2', bg=BG_COLOR, image = delete_icon)
        delete.place(relx=0.835, rely=0.5, anchor=CENTER)
        delete.bind("<1>", lambda command: controller.show_frame(Delete, [args[0]]))
        delete.image = delete_icon

    
        
class Create(Frame):
    def __init__(self, parent, controller, args):
        Frame.__init__(self, parent)
        Frame.configure(self, bg=BG_COLOR)
        company = args[0]
        
        logout_icon = PhotoImage(file=LOGOUT_ICON)
        logout = Label(self, image=logout_icon, cursor='hand2', bg=BG_COLOR)
        logout.place(relx=0.99, rely=0.01, anchor=NE)
        logout.image = logout_icon
        logout.bind("<1>", lambda command: utility.logout_with_pin(controller))
        
        back_icon = PhotoImage(file=BACK_ICON)
        back = Label(self, image=back_icon, cursor="hand2", bg=BG_COLOR)
        back.place(relx=0, rely=0, anchor=NW)
        back.image = back_icon
        back.bind("<1>", lambda command: self.back(controller, company))
        
        companyLabel = Label(self, text='Company : ', font="Helvetica 12", bg=BG_COLOR)
        companyLabel.place(relx=0.4, rely=0.3, anchor=E)
        companyname = Entry(self, font = "Helvetica 10")
        companyname.place(relx=0.5, rely=0.3, anchor=CENTER)
        companyname.delete(0, END)
        companyname.insert(0, company)
        companyname['state'] = 'readonly'
        
        codeLabel = Label(self, text="Employee Code : ", bg=BG_COLOR, font="Helvetica 12")
        codeLabel.place(relx=0.4, rely=0.4, anchor=E)

        eCode = Entry(self, font="Helvetica 10")
        eCode.place(relx=0.5, rely=0.4, anchor=CENTER)
        eCode.bind("<FocusIn>", lambda command: utility.show_keyboard(100, 275))
        eCode.bind("<FocusOut>", lambda command: utility.hide_keyboard())


        nameLabel = Label(self, text="Name : ", bg=BG_COLOR, font="Helvetica 12")
        nameLabel.place(relx=0.4, rely=0.5, anchor=E)

        name = Entry(self, font="Helvetica 10")
        name.place(relx=0.5, rely=0.5, anchor=CENTER)
        name.bind("<FocusIn>", lambda command: utility.show_keyboard(100, 50))
        name.bind("<FocusOut>", lambda command: utility.hide_keyboard())


        cap_icon = PhotoImage(file=CAP_ICON)
        self.cap = Label(self, compound=TOP, text="Capture Data", font='Helvatica 10 bold', cursor='hand2', image=cap_icon ,bg=BG_COLOR)
        self.cap.place(relx=0.4, rely=0.7, anchor=CENTER)
        self.cap.bind("<1>", lambda command: self.capture_dataset(company, eCode.get().strip(), name.get().strip(), controller))
        self.cap.image = cap_icon
        
        train_icon = PhotoImage(file=TRAIN_ICON)
        train = Label(self, compound=TOP, text="Train", font='Helvatica 10 bold', cursor='hand2', image=train_icon, bg=BG_COLOR)
        train.place(relx=0.6, rely=0.7, anchor=CENTER)
        train.bind("<1>", lambda command: controller.show_frame(TrainModel, [company, Create]))
        train.image = train_icon
            
    def back(self, controller, company):
        GPIO.output(26,GPIO.LOW)
        GPIO.output(16,GPIO.LOW)
        GPIO.output(12,GPIO.LOW)
        self.running = False
        controller.show_frame(Nav, [company])
    
    def capture_dataset(self, company, empCode, name, controller):
        state = str(self.cap['state'])
        if state == 'normal':
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
            status, message, empId = service.addNewEmployee(companyId, empCode, name)
            if status == 200 and empId:
                self.w = CaptureDataset(companyId, company, empId, empCode, name, controller)
                window.wait_window(self.w.top)
                controller.show_frame(Create, [company])
                return
            messagebox.showwarning("Warning", message)
    
            
class Update(Frame):
    def __init__(self, parent, controller, args):
        Frame.__init__(self, parent)
        Frame.config(self, bg=BG_COLOR)

        self.company = args[0]

        back_icon = PhotoImage(file=BACK_ICON)
        back = Label(self, image=back_icon, cursor="hand2", bg=BG_COLOR)
        back.place(relx=0, rely=0, anchor=NW)
        back.image = back_icon
        back.bind("<1>", lambda command: utility.back(controller, Crud, [self.company]))

        logout_icon = PhotoImage(file=LOGOUT_ICON)
        logout = Label(self, image=logout_icon, cursor='hand2', bg=BG_COLOR)
        logout.place(relx=0.99, rely=0.01, anchor=NE)
        logout.image = logout_icon
        logout.bind("<1>", lambda command: utility.logout_with_pin(controller))

        status, message, companyId = service.getCompanyId(self.company)
        
        self.employeeList = service.getEmployeeList(companyId)
        emps = [(str(emp.get('empCode')) + ', ' + str(emp.get('empName'))) for emp in self.employeeList]

        employeeLabel = Label(self, text="Employee : ", font="Helvetica 12", bg=BG_COLOR)
        employeeLabel.place(relx=0.4, rely=0.3, anchor=E)

        employee = Combobox(self, values=emps, state='readonly', font="Helvetica 10" )
        employee.current()
        employee.place(relx=0.5, rely=0.3, anchor=CENTER)
        employee.bind("<<ComboboxSelected>>", lambda command: self.fill_employee_details(employee.get()))

        codeLabel = Label(self, text="Employee Code : ", bg=BG_COLOR, font="Helvetica 12")
        codeLabel.place(relx=0.4, rely=0.4, anchor=E)

        self.emp_code_var = StringVar()
        eCode = Entry(self, font="Helvetica 10", state='readonly', text=self.emp_code_var)
        eCode.place(relx=0.5, rely=0.4, anchor=CENTER)


        nameLabel = Label(self, text="Name : ", bg=BG_COLOR, font="Helvetica 12")
        nameLabel.place(relx=0.4, rely=0.5, anchor=E)

        self.name_var = StringVar()
        name = Entry(self, font="Helvetica 10", text=self.name_var)
        name.place(relx=0.5, rely=0.5, anchor=CENTER)
        name.bind("<FocusIn>", lambda command: utility.show_keyboard(100, 50))
        name.bind("<FocusOut>", lambda command: utility.hide_keyboard())

        self.update = Label(self, text='UPDATE', cursor='hand2', bg=BG_COLOR)
        self.update.place(relx=0.5, rely=0.7, anchor=CENTER)
        self.update.bind("<1>", lambda command: self.update_employee(companyId, name.get(), eCode.get(), controller))

    def fill_employee_details(self, emp):
        empCode = emp.split(', ')[0]
        empName = emp.split(', ')[1]
        self.emp_code_var.set(empCode)
        self.name_var.set(empName)
        
    def update_employee(self, company_id, emp_name, emp_code, controller):
        self.update['state'] = 'disabled'
        if emp_name and emp_code:
            status, message = service.update_employee(company_id, emp_code, emp_name)
            if status == 200:
                for employee in self.employeeList:
                    if employee.get('empCode') == emp_code and employee.get('empName') == emp_name:
                        emp_id = employee.get('empId')
                        break
                if messagebox.askyesno("Confirm", f"Do you want to update the dataset for {emp_name} as well?"):
                    self.w = CaptureDataset(company_id, self.company, emp_id, emp_code, emp_name, controller)
                    window.wait_window(self.w.top)
                    controller.show_frame(Update, [self.company])
            else:
                messagebox.showwarning("Warning", message)
        else:
            messagebox.showwarning("Warning", "All fields are required")
        self.update['state'] = 'normal'

class CaptureDataset(object):
    def __init__(self, companyId, company, empId, empCode, name, controller):
        self.go_ahead = False
        top = self.top = Toplevel(window)
        top.withdraw()
        top.attributes('-topmost', True)
        top.title("Capture Dataset")
        top.configure(bg=BG_COLOR)
        top.protocol("WM_DELETE_WINDOW", self.cleanup)
        self.display = None
        self.cap = Button(top, text="Start Capturing", cursor="hand2")
        self.cap.bind("<1>", lambda command: self.start_capturing(companyId, company, empId, empCode, name, controller))
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
            INTERVAL = 1.5
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
            
    def start_capturing(self, companyId, company, empId, empCode, name, controller):
        state = str(self.cap['state'])
        print(state)
        if state == 'active':
            GPIO.output(16,GPIO.HIGH)
            self.cap['state'] = "disabled"
            self.cap.configure(text="Please wait while dataset is being captured")

            self.dirName = f'Clients/{company}/dataset/{empId}'
            if not os.path.exists(self.dirName):
                os.makedirs(self.dirName)
            self.start_cap = True
            window.wait_window(self.top)
            GPIO.output(16,GPIO.LOW)
            if self.total == self.NIMAGES:
                GPIO.output(26,GPIO.HIGH)
                messagebox.showinfo("Information", "Employee dataset captured successfully!")
                GPIO.output(26,GPIO.LOW)
                return
            GPIO.output(12,GPIO.HIGH)    
            messagebox.showwarning("Warning", "Something went wrong, employee added to database but dataset is not captured!")
            GPIO.output(12,GPIO.LOW)
                
    def cleanup(self):
        self.start_cap = False
        self.running = False
        self.vs.stop()
        self.top.destroy()

class Delete(Frame):
    def __init__(self, parent, controller, args):
        company = args[0]
        Frame.__init__(self, parent)
        Frame.config(self, bg=BG_COLOR)

        logout_icon = PhotoImage(file=LOGOUT_ICON)
        logout = Label(self, image=logout_icon, cursor='hand2', bg=BG_COLOR)
        logout.place(relx=0.99, rely=0.01, anchor=NE)
        logout.image = logout_icon
        logout.bind("<1>", lambda command: utility.logout_with_pin(controller))
        
        back_icon = PhotoImage(file=BACK_ICON)
        back = Label(self, image=back_icon, cursor="hand2", bg=BG_COLOR)
        back.place(relx=0, rely=0, anchor=NW)
        back.image = back_icon
        back.bind("<1>", lambda command: utility.back(controller, Crud, [company]))
        
        status, message, companyId = service.getCompanyId(company)
        
        self.employeeList = service.getEmployeeList(companyId)
        emps = [(str(emp.get('empCode')) + ', ' + str(emp.get('empName'))) for emp in self.employeeList]

        employeeLabel = Label(self, text="Employee : ", font="Helvetica 12", bg=BG_COLOR)
        employeeLabel.place(relx=0.4, rely=0.4, anchor=E)

        employee = Combobox(self, values=emps, state='readonly', font="Helvetica 10" )
        employee.current()
        employee.place(relx=0.5, rely=0.4, anchor=CENTER)

        delete_icon = PhotoImage(file=CAP_ICON) # TODO: Change delete icon
        self.delete = Label(self, compound=TOP, text="Delete", font='Helvatica 10 bold', cursor='hand2', image=delete_icon ,bg=BG_COLOR)
        self.delete.place(relx=0.4, rely=0.7, anchor=CENTER)
        self.delete.bind("<1>", lambda command: self.deleteEmployee(company, companyId, employee.get(), controller))
        self.delete.image = delete_icon
        
        train_icon = PhotoImage(file=TRAIN_ICON)
        train = Label(self, compound=TOP, text="Train", font='Helvatica 10 bold', cursor='hand2', image=train_icon, bg=BG_COLOR)
        train.place(relx=0.6, rely=0.7, anchor=CENTER)
        train.bind("<1>", lambda command: controller.show_frame(TrainModel, [company, Delete]))
        train.image = train_icon

    def deleteEmployee(self, company, companyId, emp, controller):
        empCode = emp.split(', ')[0]
        empName = emp.split(', ')[1]
        for emp in self.employeeList:
            if emp.get('empCode') == empCode:
                empId = emp.get('empId')
                break
        if messagebox.askyesno("Warning", f"Do you really want to delete {empName}?"):
            service.deleteEmployee(companyId, company, empId, empCode)
            controller.show_frame(Delete, [company])

    
    def back(self, controller, company):
        GPIO.output(26,GPIO.LOW)
        GPIO.output(16,GPIO.LOW)
        GPIO.output(12,GPIO.LOW)
        self.running = False
        controller.show_frame(Nav, [company])
    
    def logout(self, controller):
        GPIO.output(26,GPIO.LOW)
        GPIO.output(16,GPIO.LOW)
        GPIO.output(12,GPIO.LOW)
        controller.show_frame(Login, [])

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
        if self.confirmTrain(company):
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

class Mode(Frame):
    def __init__(self, parent, controller, args):
        Frame.__init__(self, parent)
        Frame.config(self, bg=BG_COLOR)
        window.attributes('-fullscreen', True)
        utility.set_fullscreen_state(True)
        self.bind('<F11>', lambda command: utility.toggle_fullscreen())

        logout_icon = PhotoImage(file=LOGOUT_ICON)
        logout = Label(self, image=logout_icon, cursor='hand2', bg=BG_COLOR)
        logout.place(relx=0.99, rely=0.01, anchor=NE)
        logout.image = logout_icon
        logout.bind("<1>", lambda command: utility.logout_with_pin(controller))

        auto_icon = PhotoImage(file=AUTO_ICON)
        auto = Label(self, cursor='hand2', bg=BG_COLOR , image = auto_icon)
        auto.place(relx=0.25, rely=0.5, anchor=CENTER)
        auto.image = auto_icon
        auto.bind("<1>", lambda command: controller.show_frame(Auto, [args[0]]))
        
        manual_icon = PhotoImage(file=MANUAL_ICON)
        manual = Label(self,  cursor='hand2', bg=BG_COLOR , image = manual_icon)
        manual.place(relx=0.75, rely=0.5, anchor=CENTER)
        manual.image = manual_icon
        manual.bind("<1>", lambda command: controller.show_frame(Manual, [args[0]]))


class Auto(Frame):
    def __init__(self, parent, controller, args):
        GPIO.output(26,GPIO.LOW)
        GPIO.output(16,GPIO.LOW)
        GPIO.output(12,GPIO.LOW)
        
        companyname = args[0]
        Frame.__init__(self, parent)
        Frame.config(self, bg=BG_COLOR)
        self.bind('<F11>', lambda command: utility.toggle_fullscreen())

        self.message = ""
        logout_icon = PhotoImage(file=LOGOUT_ICON)

        back_icon = PhotoImage(file=BACK_ICON)
        back = Label(self, image=back_icon, cursor="hand2", bg=BG_COLOR)
        back.place(relx=0, rely=0, anchor=NW)
        back.image = back_icon
        back.bind("<1>", lambda command: self.back(controller, companyname))

        logout = Label(self, image=logout_icon, cursor='hand2', bg=BG_COLOR)
        logout.place(relx=0.99, rely=0.01, anchor=NE)
        logout.image = logout_icon
        logout.bind("<1>", lambda command: utility.logout_with_pin(controller))

        company = Label(self, text=f"Welcome to {companyname} ", bg=BG_COLOR, font="Helvetica 30 bold")
        company.place(relx=0.5, rely=0.15, anchor=CENTER)

        self.label = Label(self)
        self.f = face(companyname)
        self.running = True
        self.releaseSensor = True
        self.detected = False
        thread.start_new_thread(self.initialize, ())
        self.after(20, lambda: self.check_thread(companyname))
                
    def back(self, controller, companyname):
        GPIO.output(26,GPIO.LOW)
        GPIO.output(16,GPIO.LOW)
        GPIO.output(12,GPIO.LOW)
        self.running = False
        controller.show_frame(Mode, [companyname])
        
        
    def handleLabel(self):
        self.label.destroy()
        GPIO.output(26, GPIO.LOW)
        GPIO.output(16, GPIO.LOW)
        GPIO.output(12, GPIO.LOW)
        self.releaseSensor = True
    
    def initialize(self):
        try:
            GPIO.output(26,GPIO.LOW)
            GPIO.output(16,GPIO.LOW)
            GPIO.output(12,GPIO.LOW)
            while self.running:
                if GPIO.input(17) and self.releaseSensor:
                    GPIO.output(16,GPIO.HIGH)
                    self.releaseSensor = False
                    self.empId, self.detectedTime = self.f.recognize()
                    self.detected = True
                    
        except Exception as e:
            print("[WARN] Exception occured in non tkinter thread: ", e)
            
    def check_thread(self, company):
        if self.detected:
            self.detected = False
            message = "Please try again"
            if self.empId != "unknown":
                status, msg, self.empCode, self.name = service.getEmployee(self.empId)
                if status == 200 and self.confirmName(self.name):
                    ####################################################
                    utility.copy_display_to_dataset(company, self.empId)
                    ####################################################
                    status, message = service.recordTime(self.empId, self.detectedTime)
                    if status == 201:
                        message = service.recordTimeInCSV(company, self.empCode, self.name, self.detectedTime)
                        GPIO.output(26,GPIO.HIGH)
                        GPIO.output(5,GPIO.HIGH)
                        self.after(800, lambda: GPIO.output(5,GPIO.LOW))
                else:
                    GPIO.output(16,GPIO.LOW)
                    GPIO.output(12, GPIO.HIGH)
            else:
                GPIO.output(16,GPIO.LOW)
                GPIO.output(12, GPIO.HIGH)
            self.label = Label(window, text=message, bg=BG_COLOR, font = "Helvetica 18")
            self.label.place(relx=0.5, rely=0.35, anchor=CENTER)
            self.label.after(2000, self.handleLabel)
            
        if self.running:
            self.after(20, lambda: self.check_thread(company))

    def confirmName(self, name):
        self.w = confirmNamePopup(name)
        window.wait_window(self.w.top)
        return self.w.confirm

class Manual(Frame):
    def __init__(self, parent, controller, args):
        GPIO.output(26,GPIO.LOW)
        GPIO.output(16,GPIO.LOW)
        GPIO.output(12,GPIO.LOW)
        companyname = args[0]
        Frame.__init__(self, parent)
        Frame.config(self, bg=BG_COLOR)
        self.bind('<F11>', lambda command: utility.toggle_fullscreen())

        self.message = ""
        mancap_icon = PhotoImage(file=MANCAP_ICON)
        logout_icon = PhotoImage(file=LOGOUT_ICON)

        back_icon = PhotoImage(file=BACK_ICON)
        back = Label(self, image=back_icon, cursor="hand2", bg=BG_COLOR)
        back.place(relx=0, rely=0, anchor=NW)
        back.image = back_icon
        back.bind("<1>", lambda command: self.back(controller, companyname))

        logout = Label(self, image=logout_icon, cursor='hand2', bg=BG_COLOR)
        logout.place(relx=0.99, rely=0.01, anchor=NE)
        logout.image = logout_icon
        logout.bind("<1>", lambda command: utility.logout_with_pin(controller))

        self.mancap = Label(self, image=mancap_icon, cursor='hand2', bg=BG_COLOR)
        self.mancap.place(relx = 0.5, rely=0.75, anchor=CENTER)
        self.mancap.bind('<1>', lambda command: self.reckon(companyname))
        self.mancap.image = mancap_icon

        company = Label(self, text=f"Welcome to {companyname} ", bg=BG_COLOR, font="Helvetica 30 bold")
        company.place(relx=0.5, rely=0.15, anchor=CENTER)

        self.label = Label(self)
        self.f = face(companyname)
                
    def back(self, controller, companyname):
        GPIO.output(26,GPIO.LOW)
        GPIO.output(16,GPIO.LOW)
        GPIO.output(12,GPIO.LOW)
        controller.show_frame(Mode, [companyname])
        
    
    def handleLabel(self):
        GPIO.output(26,GPIO.LOW)
        GPIO.output(16,GPIO.LOW)
        GPIO.output(12,GPIO.LOW)
        self.label.destroy()
        self.mancap['state'] = 'normal'
        

    def reckon(self, company):
        GPIO.output(16,GPIO.HIGH)
        state = str(self.mancap['state'])
        if state == 'normal':
            self.mancap['state'] = 'disabled'
            self.update_idletasks()
            empId, detectedTime = self.f.recognize()
            message = "Please try again"
            if empId != "unknown":
                status, msg, self.empCode, self.name = service.getEmployee(empId)
                if status == 200 and self.confirmName(self.name):
                    ####################################################
                    utility.copy_display_to_dataset(company, empId)
                    ####################################################
                    status, message = service.recordTime(empId, detectedTime)
                    if status == 201:
                        message = service.recordTimeInCSV(company, self.empCode, self.name, detectedTime)
                        GPIO.output(26,GPIO.HIGH)
                        GPIO.output(5,GPIO.HIGH)
                        self.after(800, lambda: GPIO.output(5,GPIO.LOW))
                else:
                    GPIO.output(16,GPIO.LOW)
                    GPIO.output(12, GPIO.HIGH)
            else:
                GPIO.output(16,GPIO.LOW)
                GPIO.output(12, GPIO.HIGH)
            self.label = Label(window, text=message, bg=BG_COLOR , font="Helvetica 18")
            self.label.place(relx=0.5, rely=0.35, anchor=CENTER)
            self.label.after(2000, self.handleLabel)

    def confirmName(self, name):
        self.w = confirmNamePopup(name)
        window.wait_window(self.w.top)
        return self.w.confirm

    



class confirmNamePopup:
    def __init__(self, name):
        self.confirm = False
        self.state = 'normal'
        top=self.top=Toplevel(window)
        top.withdraw()
        top.lift()
        top.title("Confirm your identity")
        top.configure(bg=BG_COLOR)
        top.protocol("WM_DELETE_WINDOW", lambda: self.cleanup(False))
        top.bind("<FocusOut>", lambda command: self.cleanup(False))

        label = Label(top, text=f"Are you {name} ?", bg=BG_COLOR, font="Helvetica 18 bold", pady=10)
        label.grid(row=0, column=0, columnspan=2)
        img = ImageTk.PhotoImage(image=Image.open(os.path.dirname(os.path.abspath(__file__)) + '/icons/display.png'))
        display = Label(top,image=img, bg=BG_COLOR, relief='ridge')
        display.image = img
        display.grid(row=1, column=0, columnspan=2, sticky=W+E+N+S, padx=3)
        yes_icon = ImageTk.PhotoImage(image=Image.open(YES_ICON))
        yes = Label(top, image=yes_icon, cursor='hand2', pady=20, bg=BG_COLOR)
        yes.grid(row=5, column=0)
        yes.image = yes_icon
        yes.bind("<1>", lambda command: self.cleanup(True))
        no_icon = ImageTk.PhotoImage(image=Image.open(NO_ICON))
        no = Label(top, image=no_icon, cursor='hand2', pady=20, bg=BG_COLOR)
        no.grid(row=5, column=1)
        no.image = no_icon
        no.bind("<1>", lambda command: self.cleanup(False))

        top.update()
        w = top.winfo_width()
        h = top.winfo_height()
        ws = top.winfo_screenwidth()
        hs = top.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        top.geometry('%dx%d+%d+%d' % (w, h, x, y))
        top.deiconify()
        GPIO.output(16,GPIO.LOW)
        top.after(10000, lambda: self.cleanup(False))



    def cleanup(self, confirm):
        if self.state == 'normal':
            self.top.destroy()
            self.state = 'disabled'
            self.confirm = confirm

class LogoutPopup:
    def __init__(self, controller):
        top = self.top = Toplevel(window)
        top.withdraw()
        top.title("LOGOUT")
        top.configure(bg=BG_COLOR)
        top.lift()
        top.focus_set()
        top.bind("<FocusOut>", lambda command: self.cleanup())

        label = Label(top, text='Enter the pin:', bg=BG_COLOR)
        label.grid(row=0, column=0, columnspan=2)
        pin = Entry(top)
        pin.grid(row=1, column=0, columnspan=2)
        pin.bind("<FocusIn>", lambda command: utility.show_keyboard(200, 100))
        pin.bind("<FocusOut>", lambda command: utility.hide_keyboard())
        ok = Button(top, text='Ok', command=lambda: self.logout(pin.get().strip(), controller))
        ok.grid(row=2, column=0)
        cancel = Button(top, text='Cancel', command=self.cleanup)
        cancel.grid(row=2, column=1)

        top.update()
        w = top.winfo_width()
        h = top.winfo_height()
        ws = top.winfo_screenwidth()
        hs = top.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        top.geometry('%dx%d+%d+%d' % (w, h, x, y))
        top.deiconify()
    
    def logout(self, pin_value, controller):
        if pin_value == '0000':
            controller.show_frame(Login)
        self.cleanup()

    def cleanup(self):
        utility.hide_keyboard()
        self.top.destroy()

class Utility:

    def back(self, controller, prev_frame, args=[]):
        if 'RPi' in sys.modules:
            GPIO.output(26,GPIO.LOW)
            GPIO.output(16,GPIO.LOW)
            GPIO.output(12,GPIO.LOW)
        controller.show_frame(prev_frame, args)

    def logout_with_pin(self, controller):
        if 'RPi' in sys.modules:
            GPIO.output(26,GPIO.LOW)
            GPIO.output(16,GPIO.LOW)
            GPIO.output(12,GPIO.LOW)
        logout_popup = LogoutPopup(controller)
        window.wait_window(logout_popup.top)

    def turn_led_on(self, leds):
        if 'RPi' in sys.modules:
            for led in leds:
                GPIO.output(led, GPIO.HIGH)
    
    def turn_led_off(self, leds):
        if 'RPi' in sys.modules:
            for led in leds:
                GPIO.output(led, GPIO.LOW)


    def copy_display_to_dataset(self, company, empId):
        emp_dataset = os.path.dirname(os.path.abspath(__file__)) + f'/Clients/{company}/dataset/{empId}'

        valid_extensions = ('png',)
        valid_files = [f for f in os.listdir(emp_dataset) if '.' in f and \
            f.rsplit('.')[-1] in valid_extensions and os.path.isfile(os.path.join(emp_dataset,f))]

        from_display = os.path.dirname(os.path.abspath(__file__)) + '/icons/display.png'
        to_dataset = os.path.dirname(os.path.abspath(__file__)) + f'/Clients/\"{company}\"/dataset/{empId}/{str(len(valid_files)).zfill(5)}.png'

        os.system(f'cp {from_display} {to_dataset}')
    
    def toggle_fullscreen(self):
        global fullscreen_state
        fullscreen_state = not fullscreen_state
        window.attributes('-fullscreen', fullscreen_state)
    
    def set_fullscreen_state(self, state):
        global fullscreen_state
        fullscreen_state = state
    
    def show_keyboard(self, x, y):
        try:
            p = subprocess.Popen([f'florence move {x},{y}'], shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE, universal_newlines=True)
            if not "" == p.stderr.readline():
                subprocess.Popen(['florence'], shell=True)
                p = subprocess.Popen([f'florence move {x},{y}'], shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE, universal_newlines=True)
            subprocess.Popen(['florence show'], shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE, universal_newlines=True)
        except Exception as e:
            print(e)
            
    def hide_keyboard(self):
        try:
            subprocess.Popen(['florence hide'], shell=True, stdout= subprocess.PIPE, stderr= subprocess.PIPE, universal_newlines=True)
        except Exception as e:
            print(e)

window = Tk()
utility = Utility()
app = Client(window)
window.mainloop()
