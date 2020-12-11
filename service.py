import os
import csv
import DAO
import bcrypt
import datetime
from os.path import dirname, abspath
from os import system

def authenticateClient(company, password):
    creds = DAO.authenticateClient(company)
    if creds:
        for cred in creds:
            if bcrypt.checkpw(password.encode('ascii'), cred[2].encode('ascii')):
                return (200, "Client authentication successful", cred[0])
        return (401, "Invalid password", 0)
    return(404, "Invalid client name", 0)

def getCompanyId(company):
    id = DAO.getCompanyId(company)
    if id:
        return (200, "Company ID found", id[0])
    return (404, "Company is not registered", 0)

def addNewEmployee(companyId, empCode, name):
    if DAO.getEmployeeId(companyId, empCode):
        return (500, "Employee already exists", 0)
    if DAO.addNewEmployee(companyId, empCode,name):
        empId = DAO.getEmployeeId(companyId,empCode)
        if empId:
            return (200, "Employee added successfully", empId[0])
    return(500, "Something went wrong", 0)

def deleteEmployee(companyId, company, empId, empCode):
    emp = dirname(abspath(__file__)) + f'/Clients/\'{company}\'/dataset/{empId}'
    system(f'rm -r {emp}')
    DAO.deleteEmployee(companyId, empCode)

def update_employee(company_id, emp_code, emp_name):
    if DAO.update_employee(company_id, emp_code, emp_name):
        return (200, "Employee updated succesfully!")
    return (500, "Something went wrong")

def getAllEmployee(companyId):
    employees = DAO.getAllEmployee(companyId)
    if employees:
        return list(employees)
    return ()

def getEmployeeList(companyId):
    employees = getAllEmployee(companyId)
    if not employees:
        return()
    employeeList = []
    for employee in employees:
        employeeList.append({'empId': employee[0], 'empCode': employee[2], 'empName': employee[3]})
    return employeeList

def checkEmployeeExists(companyId, empCode):
    if DAO.getEmployeeId(companyId, empCode):
        return True
    return False

def getEmployee(employeeId):
    result = DAO.getEmployee(employeeId)
    if result:
        return (200, "Employee name found", result[2], result[3])
    else:
        return (500, "Employee not found in database", 0, 0)
    
def recordTime(employeeId, detectedTime):
    if not DAO.checkForIncompleteRecord(employeeId):
        if DAO.recordInTime(employeeId, detectedTime):
            return (201, "Recorded In time successfully!")
    if DAO.recordOutTime(employeeId, detectedTime):
        return (201, "Recorded Out time successfully")
    return (500, "Something went wrong!")

def recordTimeInCSV(company, employeeCode, name, detectedTime):
    filename = setupDir(company, detectedTime)
    if os.path.exists(filename):
        reader = csv.reader(open(filename, 'r'))
        rows = list(reader)
        for row in rows:
            if row[0] == employeeCode and row[1] == name and row[3] == "NA":
                row[3] = detectedTime.strftime("%I:%M %p")
                writer = csv.writer(open(filename, 'w'))
                writer.writerows(rows)
                return f"Have a nice day! {name}"
    record = [employeeCode, name, detectedTime.strftime("%I:%M %p"), "NA"]
    writer = csv.writer(open(filename, 'a'))
    writer.writerow(record)
    #sos.system('cp -r /home/pi/Face/Records/ /home/pi/Face/Records_Backup')
    return f"Welcome! {name}"
    
    
def setupDir(company, dateTime):
    # dateTime = datetime.datetime.now()
    dateDir = dateTime.strftime("%d-%m-%Y")
    dirName = f"Records/{company}/EntryPendingFiles"
    if not os.path.exists(dirName):
        os.makedirs(dirName)
    filename = dirName + "/" + f"{dateDir}.csv"
    return filename

"""
def recordInTime(employeeId, inTime):
    if DAO.checkForIncompleteRecord(employeeId):
        return (403, "Please exit first to enter!")
    if DAO.recordInTime(employeeId, inTime):
        return ( 201, "Recorded In time successfully!")
    return (500, "Something went wrong!")

def recordOutTime(employeeId, outTime):
    if DAO.recordOutTime(employeeId, outTime):
        return (201, "Recorded Out time successfully")
    return (403, "Please enter first to exit")
"""

def registerCompany(company, password):
    if DAO.getCompanyId(company):
        return (403, "Company is already registered")
    password = bytes(password, 'utf-8')
    salt = bcrypt.gensalt(rounds=12)
    password = bcrypt.hashpw(password, salt)
    if DAO.registerCompany(company, password):
        return (201, "Company registered successfully")
    return (500, "Something went wrong")

def getAllCompanyNames():
    companies = DAO.getAllCompanyNames()
    if not companies:
        return ()
    companyList = []
    for company in companies:
        companyList.append(company[0])
    return companyList

def getLastTrained(company):
    result = DAO.getLastTrained(company)
    if result[0]:
        return (200, f" Last trained on {result[0]}! Do you still want to train?")
    else:
        return (404, "Train this company for the first time")

def updateLastTrained(company, lastTrained):
    if DAO.updateLastTrained(company,lastTrained):
        return (201, f"Trained successfully for {company}!")
    return (500, "Something went wrong")

# print(getEmployeeList('1'))
# deleteEmployee(1, 'Testing Phase', 13, 7)