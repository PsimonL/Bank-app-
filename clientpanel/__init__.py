import uuid
from tkinter import *
from db.queries import *
from helpers import mySQL_connection, create_inputs, get_inputs


class ClientPanel():
    def __init__(self, user):
        self.user = user
        self.emp_panel = Tk()
        self.emp_panel.title("Client panel")
        self.credit_count = mySQL_connection("select count(id) from loans where accountNumber=" + str(user[0]))[0]
        self.client_container = Frame(self.emp_panel)
        self.client_container.pack()

        self.account_applications_container = Frame(self.client_container)
        self.account_applications_container.grid(row=0)

        wallet = mySQL_connection("select * from wallets where accountNumber=" + str(user[0]))
        currency = mySQL_connection("select * from currencies where id=" + str(wallet[4]))
        deposit = mySQL_connection("select value,interest from deposits where accountNumber=" + str(user[0]))

        self.value_of_wallet = str(float(currency[2]) * float(wallet[2]))
        currency_name = currency[1].upper()
        loan_count = \
        mySQL_connection("select count(id) from loans where accountNumber=" + str(user[0]) + " and confirmed =1")[0]
        welcome_text = "Welcome " + user[3] + " " + user[4]
        wallet_text = "Value " + self.value_of_wallet + currency_name

        if deposit is not None:
            deposit_text = "Deposited " + str(deposit[0]) + currency_name + "(" + str(deposit[1]) + "%)"
            self.deposit_label = Label(self.client_container, text=deposit_text)
            self.deposit_label.grid(row=2)
        if loan_count > 0:
            loan_text = "Loans " + str(loan_count)
            self.loan_label = Label(self.client_container, text=loan_text)
            self.loan_label.grid(row=3)

        welcome_label = Label(self.client_container, text=welcome_text)
        welcome_label.grid(row=0, column=0)

        self.wallet_label = Label(self.client_container, text=wallet_text)
        self.wallet_label.grid(row=1, column=0)
        self.client_container.grid_rowconfigure(1, minsize=55)

        self.transfer_button = Button(self.client_container, text="start a money transfer", command=self.transfer_money)
        self.transfer_button.grid(row=4)

        self.start_deposit_button = Button(self.client_container, text="start a deposit", command=self.deposit)
        self.start_deposit_button.grid(row=5)

        self.start_loan_button = Button(self.client_container, text="get a loan", command=self.loan_application)
        self.start_loan_button.grid(row=6)

        self.get_debit_card_button = Button(self.client_container, text="order a debit card",
                                            command=self.debit_card_application)
        self.get_debit_card_button.grid(row=7)

        self.add_cash_button = Button(self.client_container, text="Add cash", command=self.add_to_wallet)
        self.add_cash_button.grid(row=8)
        self.fields = None
        self.error_labels = dict()
        self.data = dict()

        self.transfer_error_label = Label(self.client_container, text="Check the value field")
        self.self_transfer_error_label = Label(self.client_container, text="You cannot transfer money to yourself")
        self.too_many_loans_error_label = Label(self.client_container, text="You cannot transfer money to yourself")

    def transfer_money(self):
        self.fields = ['account', 'value']

        def submit_transfer():
            if not get_inputs(inputs, self.data, self.error_labels):
                return
            if float(self.data['value']) > float(self.value_of_wallet):
                self.transfer_error_label.grid(row=6)
                return
            if str(self.data['account']) == str(self.user[0]):
                self.self_transfer_error_label.grid(row=7)
                return
            print(self.data)
            clients_wallet_value = str(float(self.value_of_wallet) - float(self.data['value']))
            receipient_initial_wallet = mySQL_connection(select_wallet_by_account_query + self.data['account'])[2]
            recipient_wallet_value = str(receipient_initial_wallet + float(self.data['value']))

            mySQL_connection(
                "UPDATE wallets SET value =" + recipient_wallet_value + " WHERE accountNumber =" + self.data[
                    'account'],
                True)
            mySQL_connection(
                "UPDATE wallets SET value =" + clients_wallet_value + " WHERE accountNumber =" + str(
                    self.user[0]),
                True)
            self.reinitialize()

        self.hide_option_buttons()
        inputs = create_inputs(self.fields, self.client_container, self.error_labels)

        submit_transfer_button = Button(self.client_container, text="transfer!!!", command=submit_transfer)
        submit_transfer_button.grid(row=3, column=1)

    def deposit(self):
        self.fields = ['value']

        def submit_deposit():
            if not get_inputs(inputs, self.data, self.error_labels):
                return
            if float(self.data['value']) <= 0:
                self.transfer_error_label.grid(row=6)
                return
            deposit = mySQL_connection("select * from deposits where accountNumber= " + str(self.user[0]))
            val = str(float(self.value_of_wallet) - float(self.data['value']))
            print(self.user[0])
            if deposit is None:
                query = "insert into deposits(accountNumber,value) Values(" + str(self.user[0]) + ", " + str(self.data[
                                                                                                                 'value']) + ")"
                print(query)
                mySQL_connection(query, True)
                mySQL_connection("UPDATE wallets SET value =" + val + " WHERE accountNumber =" + str(
                    self.user[0]), True)
                self.reinitialize()
                return
            print(deposit)
            value_of_deposit = deposit[2]
            final_deposit_value = value_of_deposit + float(self.data['value'])
            clients_wallet_value = str(float(self.value_of_wallet) - float(self.data['value']))
            mySQL_connection(
                "UPDATE deposits SET value =" + str(final_deposit_value) + " WHERE accountNumber =" + str(
                    self.user[0]),
                True)
            mySQL_connection("UPDATE wallets SET value =" + str(clients_wallet_value) + " WHERE accountNumber =" + str(
                self.user[0]), True)
            self.reinitialize()

        self.hide_option_buttons()
        inputs = create_inputs(self.fields, self.client_container, self.error_labels)

        submit_deposit_button = Button(self.client_container, text="Deposit", command=submit_deposit)
        submit_deposit_button.grid(row=3, column=1)

    def add_to_wallet(self):
        self.fields = ['value']

        def submit_deposit():
            if not get_inputs(inputs, self.data, self.error_labels):
                return
            if float(self.data['value']) <= 0:
                self.transfer_error_label.grid(row=6)
                return

            clients_wallet_value = str(float(self.value_of_wallet) + float(self.data['value']))

            mySQL_connection(
                "UPDATE wallets SET value =" + clients_wallet_value + " WHERE accountNumber =" + str(
                    self.user[0]),
                True)
            self.reinitialize()

        self.hide_option_buttons()
        inputs = create_inputs(self.fields, self.client_container, self.error_labels)

        submit_deposit_button = Button(self.client_container, text="Deposit", command=submit_deposit)
        submit_deposit_button.grid(row=3, column=1)

    def debit_card_application(self):
        mySQL_connection(
            "insert into creditcard(accountNumber,number) Values(" + str(self.user[0]) + ", " + str(uuid.uuid4())+ ")",
            True)
        self.reinitialize()

    def loan_application(self):
        if self.credit_count > 5:
            self.too_many_loans_error_label.grid()
            return
        self.fields = ['value', 'months']

        def submit_loan_application():
            if not get_inputs(inputs, self.data, self.error_labels):
                return
            if float(self.data['value']) <= 0:
                self.transfer_error_label.grid(row=6)
                return

            query = "insert into loans(accountNumber,value,remainedMonths) Values(" + str(self.user[0]) + ", " + str(
                self.data['value']) + ", " + self.data['months'] + ")"
            mySQL_connection(query, True)
            self.reinitialize()
            return

        self.hide_option_buttons()
        inputs = create_inputs(self.fields, self.client_container, self.error_labels)

        submit_deposit_button = Button(self.client_container, text="Apply for a loan", command=submit_loan_application)
        submit_deposit_button.grid(row=3, column=1)

    def reinitialize(self):
        self.emp_panel.destroy()
        ClientPanel(self.user)

    def hide_option_buttons(self):
        self.transfer_button.grid_forget()
        self.start_deposit_button.grid_forget()
        self.add_cash_button.grid_forget()
        self.start_loan_button.grid_forget()
        self.get_debit_card_button.grid_forget()

def end():
    exit(1)
