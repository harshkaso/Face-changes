import MySQLdb as mdb
import json
from os.path import dirname, abspath
#from os import getcwd
with open(dirname(abspath(__file__)) + '/config.json') as config_file:
    config = json.load(config_file)
def connect():
    return mdb.connect(config['HOST'], config['USER'], config['PASS'], config['SCHEMA'])

def authenticateClient(company):
    try:
        con = connect()

        cur = con.cursor()
        conditions ='1'
        conditions += ' and company = %(company)s' if company else True
        query = f'SELECT * FROM credentials WHERE {conditions}'
        cur.execute(query,{'company': company})
        results = cur.fetchall()
        return results

    except mdb.Error as e:
        print("Error %d: %s"%(e.args[0], e.args[1]))
        return

    finally:
        if con:
            con.close()


def getAllCompanyNames():
    try:
        con = connect()
        cur = con.cursor()
        query = 'SELECT company FROM credentials'
        cur.execute(query)
        results = cur.fetchall()
        return results
    except mdb.Error as e:
        print("Error %d: %s"%(e.args[0], e.args[1]))
        return

    finally:
        if con:
            con.close()

def getCompanyId(company):
    try:
        con = connect()
        cur = con.cursor()
        conditions = '1'
        conditions += ' and company = %(company)s' if company else True
        query = f'SELECT company_id FROM credentials WHERE {conditions}'
        cur.execute(query, {'company': company})
        results = cur.fetchone()
        return results

    except mdb.Error as e:
        print("Error %d: %s"%(e.args[0], e.args[1]))
        con.rollback()
        return

    finally:
        if con:
            con.close()

def addNewEmployee(companyId, empCode, name):
    try:
        con = connect()
        cur = con.cursor()
        query = """
            INSERT INTO employee (company_id, employee_code, employee_name)
            VALUES (%(companyId)s, %(empCode)s, %(name)s);
        """
        cur.execute(query, {'companyId': companyId, 'empCode': empCode,'name': name})
        con.commit()
        return True

    except mdb.Error as e:
        print("Error %d: %s"%(e.args[0], e.args[1]))
        return False

    finally:
        if con:
            con.close()

def deleteEmployee(companyId, empCode):
    try:
        con = connect()
        cur = con.cursor()
        query = """
            UPDATE employee
            SET presently_working = FALSE
            WHERE company_id = %(companyId)s AND employee_code = %(empCode)s
        """
        cur.execute(query, {'companyId': companyId, 'empCode': empCode})
        con.commit()
    except mdb.Error as e:
        print("Error %d: %s"%(e.args[0], e.args[1]))
    finally:
        if con:
            con.close()

def update_employee(company_id, emp_code, emp_name):
    try:
        con = connect()
        cur = con.cursor()
        query = """
            UPDATE employee
            SET employee_name = %(emp_name)s
            WHERE company_id = %(company_id)s AND employee_code = %(emp_code)s
        """
        cur.execute(query, {'company_id': company_id, 'emp_code': emp_code, 'emp_name': emp_name})
        con.commit()
        return True
    except mdb.Error as e:
        print("Error %d: %s"%(e.args[0], e.args[1]))
        return False
    finally:
        if con:
            con.close()

def getEmployeeId(companyId, empCode):
    try:
        con = connect()
        cur = con.cursor()
        conditions = '1'
        conditions += ' and company_id = %(companyId)s' if companyId else True
        conditions += ' and employee_code = %(empCode)s' if empCode else True
        query = f'SELECT employee_id FROM employee WHERE {conditions}'
        cur.execute(query, {'companyId': companyId, 'empCode': empCode})
        results = cur.fetchone()
        return results

    except mdb.Error as e:
        print("Error %d: %s"%(e.args[0], e.args[1]))
        return

    finally:
        if con:
            con.close()

def getEmployee(employeeId):
    try:
        con = connect()
        cur = con.cursor()
        conditions = '1'
        conditions += ' and employee_id = %(employeeId)s' if employeeId else True
        query = f'SELECT * FROM employee WHERE {conditions}'
        cur.execute(query, {'employeeId': employeeId})
        results = cur.fetchone()
        return results

    except mdb.Error as e:
        print("Error %d: %s"%(e.args[0], e.args[1]))
        return

    finally:
        if con:
            con.close()

def getAllEmployee(companyId):
    try:
        con = connect()
        cur = con.cursor()
        conditions = '1'
        conditions += ' and company_id = %(companyId)s' if companyId else True
        conditions += ' and presently_working = TRUE'
        query = f'SELECT * FROM employee WHERE {conditions}'
        cur.execute(query, {'companyId': companyId})
        results = cur.fetchall()
        return results

    except mdb.Error as e:
        print("Error %d: %s"%(e.args[0], e.args[1]))
        return
    finally:
        if con:
            con.close()

def checkForIncompleteRecord(employeeId):
    try:
        con = connect()
        cur = con.cursor()
        conditions = '1'
        conditions += ' and employee_id = %(employeeId)s' if employeeId else True
        conditions += ' and out_time IS NULL'
        query = f'SELECT * FROM records WHERE {conditions}'
        cur.execute(query, {'employeeId': employeeId})
        results = cur.fetchone()
        return results

    except mdb.Error as e:
        print("Error %d: %s"%(e.args[0], e.args[1]))
        return

    finally:
        if con:
            con.close()

def recordInTime(employeeId, inTime):
    try:
        con = connect()
        cur = con.cursor()
        query = """
            INSERT INTO records (employee_id, in_time) 
            VALUES (%(employeeId)s, %(inTime)s)
        """
        cur.execute(query, {'employeeId': employeeId, 'inTime': inTime})
        con.commit()
        return True

    except mdb.Error as e:
        print("Error %d: %s"%(e.args[0], e.args[1]))
        con.rollback()
        return False

    finally:
        if con:
            con.close()

def recordOutTime(employeeId, outTime):
    try:
        con = connect()
        cur = con.cursor()
        query = """
            UPDATE records
            SET out_time = (%(outTime)s)
            WHERE employee_id = %(employeeId)s and out_time IS NULL
        """
        result = cur.execute(query, {'employeeId': employeeId, 'outTime': outTime})
        con.commit()
        return result

    except mdb.Error as e:
        print("Error %d: %s"%(e.args[0], e.args[1]))
        con.rollback()
        return False

    finally:
        if con:
            con.close()


def registerCompany(company, password):
    try:
        con = connect()
        cur = con.cursor()
        query = """
            INSERT INTO credentials (company, password)
            VALUES (%(company)s, %(password)s)
        """
        result = cur.execute(query, {'company': company, 'password': password})
        con.commit()
        return result

    except mdb.Error as e:
        print("Error %d: %s"%(e.args[0], e.args[1]))
        con.rollback()
        return False

    finally:
        if con:
            con.close()

def getLastTrained(company):
    try:
        con = connect()
        cur = con.cursor()
        conditions = ''
        conditions += 'and company = %(company)s' if company else True
        query = f'SELECT last_trained FROM credentials WHERE 1 {conditions}'
        cur.execute(query, {'company': company})
        result = cur.fetchone()
        return result
    except mdb.Error as e:
        print("Error %d: %s"%(e.args[0], e.args[1]))
        return False

    finally:
        if con:
            con.close()

def updateLastTrained(company, lastTrained):
    try:
        con = connect()
        cur = con.cursor()
        query ="""
            UPDATE credentials
            SET last_trained = (%(lastTrained)s)
            WHERE company = %(company)s
        """
        result = cur.execute(query, {'lastTrained': lastTrained, 'company': company})
        con.commit()
        return result

    except mdb.Error as e:
        print("Error %d: %s"%(e.args[0], e.args[1]))
        con.rollback()
        return False

    finally:
        if con:
            con.close()

def getAllRecords():
    try:
        con = connect()
        cur = con.cursor()
        query = 'SELECT * FROM records'
        cur.execute(query)
        results = cur.fetchall()
        return results
    except mdb.Error as e:
        print("Error %d: %s"%(e.args[0], e.args[1]))
        return

    finally:
        if con:
            con.close()
