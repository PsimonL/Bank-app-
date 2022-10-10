from tkinter import *
from db.queries import *
from helpers import mySQL_connection


class EmployeePanel():

    def __init__(self, user):
        self.user = user
        self.emp_panel = Tk()
        self.emp_panel.title("Employee panel")

        self.employee_container = Frame(self.emp_panel)
        self.employee_container.pack()

        self.account_applications_container = Frame(self.employee_container)
        self.account_applications_container.grid(row=1)

        self.loans_applications_container = Frame(self.employee_container)
        self.loans_applications_container.grid(row=2)

        self.debit_applications_container = Frame(self.employee_container)
        self.debit_applications_container.grid(row=3)

        welcome_text = "Welcome " + user[2] + " " + user[1]

        welcome_label = Label(self.employee_container, text=welcome_text)
        welcome_label.grid(row=0, column=0)
        self.create_account_application_list()
        self.create_debit_application_List()
        self.create_loan_application_List()

    def reinitialize(self):
        self.emp_panel.destroy()
        EmployeePanel(self.user)

    def employee_approved(self, type, application):
        id=str(application.id)
        if type == "account":
            confirm_client_account_query = "UPDATE clients SET confirmed = 1,wallet="+id+",accountNumber=id WHERE pesel ="
            mySQL_connection(confirm_client_account_query + application.pesel, True)
            mySQL_connection("insert into wallets(id,accountNumber,value) values("+id+","+id+","+str(0)+")",True)
            self.reinitialize()
        elif type == "loan":
            prev_value=str(mySQL_connection("select value from clients where id="+id)[0])
            mySQL_connection("UPDATE loans SET confirmed = 1, interest=5 where accountNumber="+id,True)
            mySQL_connection("UPDATE wallets SET value = "+"prev_value"+" where accountNumber="+id,True)
            self.reinitialize()
        elif type == "card":
            mySQL_connection("UPDATE creditcard SET confirmed = 1 where accountNumber="+str(application.id),True)
            self.reinitialize()

    def employee_rejected(self, type, application):
        id = str(application.id)
        if type == "account":
            mySQL_connection(reject_client_account_query + application.pesel, True)
            self.reinitialize()
        elif type == "loan":
            mySQL_connection("UPDATE loans SET hidden = 1 where accountNumber=" + id, True)
            self.reinitialize()
        elif type == "card":
            mySQL_connection("UPDATE creditcard SET hidden = 1 where accountNumber=" + id, True)
            self.reinitialize()

    def create_account_application_list(self):
        applications = mySQL_connection(select_unconfirmed_clients_query, False, True)
        application_id = 0
        print(applications)
        if not applications :
            print(applications)
            return
        for appl in applications:
            print("applications")
            application_row = application_id + 2
            self.account_applications_container.grid_rowconfigure(application_row, minsize=45)
            application = Frame(self.account_applications_container)
            application.grid(row=application_row, column=0)
            application.grid_columnconfigure(0, minsize=120)
            application.pesel = appl[1]
            application.id = appl[0]
            name_label = Label(application, text=appl[3] + " " + appl[4])
            name_label.grid(row=application_row, column=0)

            pesel_label = Label(application, text=appl[1])
            pesel_label.grid(row=application_row, column=1)

            approve_button = Button(application, text="Approve application",
                                    command=lambda bound_appl=application: self.employee_approved("account",
                                                                                                  bound_appl))
            reject_button = Button(application, text="Reject application",
                                   command=lambda bound_appl=application: self.employee_rejected("account", bound_appl))

            approve_button.grid(row=application_row, column=2)
            reject_button.grid(row=application_row, column=3)
            application_id += 1
    def create_debit_application_List(self):
        applications = mySQL_connection("select * from creditcard where confirmed=0 and hidden=0", False, True)
        application_id = 0
        if len(applications) == 0:
            return
        for appl in applications:
            application_row = application_id + 2
            application = Frame(self.debit_applications_container)
            application.grid(row=application_row, column=0)
            application.id = appl[2]
            name_label = Label(application, text="AccountNumber: "+str(appl[1]))
            name_label.grid(row=application_row, column=0)

            approve_button = Button(application, text="Approve application",
                                    command=lambda bound_appl=application: self.employee_approved("card",
                                                                                                  bound_appl))
            reject_button = Button(application, text="Reject application",
                                   command=lambda bound_appl=application: self.employee_rejected("card", bound_appl))

            approve_button.grid(row=application_row, column=2)
            reject_button.grid(row=application_row, column=3)
            application_id += 1
    def create_loan_application_List(self):
        applications = mySQL_connection("select * from loans where confirmed=0 and hidden=0", False, True)
        application_id = 0
        if len(applications) == 0:
            return
        for appl in applications:
            application_row = application_id + 2
            application = Frame(self.loans_applications_container)
            application.grid(row=application_row, column=0)
            application.id = appl[1]
            account_label = Label(application, text="Account: "+str(appl[1]))
            account_label.grid(row=application_row, column=1)

            value_label = Label(application, text=str(appl[3])+"PLN")
            value_label.grid(row=application_row, column=2)

            interest_label = Label(application, text=str(appl[4])+"%")
            interest_label.grid(row=application_row, column=3)
            time_label = Label(application, text="time: "+str(appl[5]))
            time_label.grid(row=application_row, column=4)

            approve_button = Button(application, text="Approve application",
                                    command=lambda bound_appl=application: self.employee_approved("loan",
                                                                                                  bound_appl))
            reject_button = Button(application, text="Reject application",
                                   command=lambda bound_appl=application: self.employee_rejected("loan", bound_appl))

            approve_button.grid(row=application_row, column=5)
            reject_button.grid(row=application_row, column=6)
            application_id += 1
def end():
    exit(1)
