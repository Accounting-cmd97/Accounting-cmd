import xml.etree.ElementTree as ET
from datetime import date, timedelta
from datetime import datetime
import xml.dom.minidom
import os

TRANSACTIONS_FILE = 'transactions.xml'
ACCOUNTS_FILE = 'chart_of_accounts.xml'


def prettify(elem):
    """Return a pretty-printed XML string."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = xml.dom.minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def create_accounts_file():
    """Create an empty chart_of_accounts.xml file if it doesn't exist."""
    if not os.path.exists(ACCOUNTS_FILE):
        root = ET.Element('accounts')
        xml_str = prettify(root)
        with open(ACCOUNTS_FILE, 'wb') as file:
            file.write(xml_str.encode())
        print(f"Created file: {ACCOUNTS_FILE}")
    else:
        print(f"File already exists: {ACCOUNTS_FILE}")


def create_transactions_file():
    """Create an empty transactions.xml file if it doesn't exist."""
    if not os.path.exists(TRANSACTIONS_FILE):
        root = ET.Element('transactions')
        xml_str = prettify(root)
        with open(TRANSACTIONS_FILE, 'wb') as file:
            file.write(xml_str.encode())
        print(f"Created file: {TRANSACTIONS_FILE}")
    else:
        print(f"File already exists: {TRANSACTIONS_FILE}")


def load_transactions():
    try:
        tree = ET.parse(TRANSACTIONS_FILE)
        root = tree.getroot()
        transactions = []

        for transaction_elem in root.findall('transaction'):
            date = transaction_elem.find('Date').text
            description = transaction_elem.find('Description').text
            source = transaction_elem.find('Source').text
            account = transaction_elem.find('Account').text
            debit = float(transaction_elem.find('Debit').text)
            credit = float(transaction_elem.find('Credit').text)
            posted = transaction_elem.find('Posted').text
            authorized = transaction_elem.find('Authorized').text


            transactions.append({
                'Date': date,
                'Description': description,
                'Source': source,
                'Account': account,
                'Debit': debit,
                'Credit': credit,
                'Posted': posted,
                'Authorized': authorized
            })

        return transactions
    except FileNotFoundError:
        return []


def save_transactions(transactions):
    root = ET.Element('transactions')

    for transaction in transactions:
        transaction_elem = ET.SubElement(root, 'transaction')
        ET.SubElement(transaction_elem, 'Date').text = transaction['Date']
        ET.SubElement(transaction_elem, 'Description').text = transaction['Description']
        ET.SubElement(transaction_elem, 'Source').text = transaction['Source']
        ET.SubElement(transaction_elem, 'Account').text = transaction['Account']
        ET.SubElement(transaction_elem, 'Debit').text = str(transaction['Debit'])
        ET.SubElement(transaction_elem, 'Credit').text = str(transaction['Credit'])
        ET.SubElement(transaction_elem, 'Posted').text = transaction['Posted']
        ET.SubElement(transaction_elem, 'Authorized').text = transaction['Authorized']


    tree = ET.ElementTree(root)
    tree.write(TRANSACTIONS_FILE)


def load_accounts():
    try:
        tree = ET.parse(ACCOUNTS_FILE)
        root = tree.getroot()
        accounts = []

        for account_elem in root.findall('account'):
            name = account_elem.find('Name').text
            account_type = account_elem.find('Type').text
            status = account_elem.find('status').text

            accounts.append({
                'Name': name,
                'Type': account_type,
                'Status': status
            })

        return accounts
    except FileNotFoundError:
        return []


def save_accounts(accounts):
    root = ET.Element('accounts')

    for account in accounts:
        account_elem = ET.SubElement(root, 'account')
        ET.SubElement(account_elem, 'Name').text = account['Name']
        ET.SubElement(account_elem, 'Type').text = account['Type']
        ET.SubElement(account_elem, 'status').text = account['Status']

    tree = ET.ElementTree(root)

    # Convert the XML tree to a formatted string
    xml_str = ET.tostring(root, encoding='utf-8').decode()
    xml_str = '\n'.join([line for line in xml_str.split('\n') if line.strip()])

    # Write the formatted string to the file
    with open(ACCOUNTS_FILE, 'wb') as file:
        file.write(f'<?xml version="1.0" encoding="utf-8"?>\n{xml_str}'.encode())


def post_transaction(poster):
    def date_check():
        d = input('Enter the date (MM/DD/YYYY): ')

        def is_valid_date_format(date_string):
            try:
                datetime.strptime(date_string, '%m/%d/%Y')
                return True
            except ValueError:
                return False
        d_c = is_valid_date_format(d)
        if d_c:
            return d
        else:
            date_check()

    def account_exists(account_name):
        accounts = load_accounts()
        for acc in accounts:
            if acc['Name'] == account_name:
                return True
        return False

    def account_check_debit():
        debit_a = input("Enter Debit Account:")
        if not account_exists(debit_a):
            account_check_debit()
        if account_exists(debit_a):
            return debit_a

    def account_check_credit():
        credit_a = input("Enter Credit Account:")
        if not account_exists(credit_a):
            account_check_credit()
        if account_exists(credit_a):
            return credit_a

    list_accounts()
    date_1 = date_check()
    debit = account_check_debit()
    credit = account_check_credit()
    description = input('Enter any information for the record:')
    source = input('Supporting document:')
    amount_pt = input('Enter the transaction amount before tax: ')
    amount_pt = float(amount_pt) if amount_pt.strip() else 0.00
    amount_tax = input('Enter the transaction tax amount: ')
    amount_tax = float(amount_tax) if amount_tax.strip() else 0.00
    authorized = input('Who authorized the transaction: ')

    transactions = load_transactions()
    transactions.append({
        'Date': date_1,
        'Account': debit,
        'Description': description,
        'Source': source,
        'Debit': amount_pt + amount_tax,
        'Credit': 0,
        'Posted': poster,
        'Authorized': authorized
    })
    save_transactions(transactions)
    transactions.append({
        'Date': date_1,
        'Account': credit,
        'Description': description,
        'Source': source,
        'Debit': 0,
        'Credit': amount_pt + amount_tax,
        'Posted': poster,
        'Authorized': authorized
    })
    save_transactions(transactions)

    print('Transaction posted successfully.')


def add_account():
    name = input('Enter the account name: ')

    def type_account():
        account_t = input('Enter the account type (a for asset, l for liability, equ for equity, r for revenue, '
                             'ex for expense): ')
        if account_t in ('a', 'l', 'equ', 'r', 'ex'):
            pass
        else:
            type_account()
        return account_t

    account_type = type_account()
    if account_type == 'a':
        account_type = 'Asset'
    if account_type == 'l':
        account_type = 'Liability'
    if account_type == 'equ':
        account_type = 'Equity'
    if account_type == 'r':
        account_type = 'Revenue'
    if account_type == 'ex':
        account_type = 'Expense'

    accounts = load_accounts()
    accounts.append({
        'Name': name,
        'Type': account_type,
        'Status': 'Active'
    })
    save_accounts(accounts)
    print('Account added successfully.')


def change_account_status():
    list_accounts()
    account_name = input("What account's status would you like to change: ")
    tree = ET.parse(TRANSACTIONS_FILE)
    root = tree.getroot()

    accounts = load_accounts()
    accounts.sort(key=lambda acc: acc['name'])  # Sort accounts alphabetically by name
    for account in accounts:
        name = account['name']
        status = account['Status']

    if name == account_name:
        if status == 'Active':
            status = 'Inactive'
        else:
            pass
    # Write the changes back to the XML file
    tree.write(ACCOUNTS_FILE)


def get_account_balance(account, transactions):
    balance = 0
    for transaction in transactions:
        Account = transaction['Account']
        debit = transaction['Debit']
        credit = transaction['Credit']

        if Account == account:
            balance -= debit
            balance += credit
    return balance


def show_general_ledger():
    transactions = load_transactions()

    sorted_transactions = sorted(transactions, key=lambda t: datetime.strptime(t['Date'], '%m/%d/%Y'))

    print('General Ledger')
    print('Date\t\tAccount\t\tDebit\t\tCredit\tPosted\tAuthorized')

    for transaction in sorted_transactions:
        date = transaction['Date']
        account = transaction['Account']
        debit = transaction['Debit']
        credit = transaction['Credit']
        posted = transaction['Posted']
        authorized = transaction['Authorized']

        if debit > 0:
            print(f'{date}\t{account[:15]:<15}\t{round(debit,2)}\t\t\t\t{posted}\t\t{authorized}')
        else:
            print(f'\t\t\t\t{account[:15]:<15}\t\t{round(credit,2)}\t\t{posted}\t\t{authorized}')


def show_ledger(account):
    transactions = load_transactions()

    sorted_transactions = sorted(transactions, key=lambda t: datetime.strptime(t['Date'], '%m/%d/%Y'))

    print(f'Ledger for account: {account}')
    print('Date\t\tDescription\t\t\t\t\t\t\t\tDebit\t\tCredit\t\t\tBalance\t\tPosted\tAuthorized')

    balance = 0

    for transaction in sorted_transactions:
        date = transaction['Date']
        debit = transaction['Debit']
        credit = transaction['Credit']
        description = transaction['Description']
        account_1 = transaction['Account']
        account_type = get_account_type(account)
        posted = transaction['Posted']
        authorized = transaction['Authorized']

        if account_1 == account:
            if account_type == 'Liability' or account_type == 'Equity' or account_type == 'Revenue':
                if debit > 0:
                    balance -= debit
                    print(f'{date}\t{description[:25]:<25}\t\t\t\t{round(debit, 2):<15}\t\t\t\t{round(balance, 2):<15}'
                          f'\t{posted}\t\t{authorized}')
                else:
                    balance += credit
                    print(f'{date}\t{description[:25]:<25}\t\t\t\t\t\t\t{round(credit, 2):<15}\t{round(balance, 2):<15}'
                          f'\t{posted}\t\t{authorized}')
            elif account_type == 'Asset' or account_type == 'Expense':
                if debit > 0:
                    balance += debit
                    print(f'{date}\t{description[:25]:<25}\t\t\t\t{round(debit, 2):<15}\t\t\t\t{round(balance, 2):<15}'
                          f'\t{posted}\t\t{authorized}')
                else:
                    balance -= credit
                    print(f'{date}\t{description[:25]:<25}\t\t\t\t\t\t\t{round(credit, 2):<15}\t{round(balance, 2):<15}'
                          f'\t{posted}\t\t{authorized}')
        else:
            pass


def get_account_type(account):
    accounts = load_accounts()
    for acc in accounts:
        if acc['Name'] == account:
            return acc['Type']
    return 'Unknown'


def show_balance_sheet():
    transactions = load_transactions()
    accounts = load_accounts()
    print('Balance Sheet')

    print('-------------------------------------------')
    print('Assets:')
    print('Account\t\t\t\tBalance')
    print('-------------------------------------------')
    total_assets = total_assets_1 = 0

    for account in accounts:
        account_name = account['Name']
        account_type = account['Type']

        account_balance = get_account_balance(account_name, transactions)

        if account_type == 'Asset':
            total_assets_1 -= account_balance
        else:
            pass

    for account in accounts:
        account_name = account['Name']
        account_type = account['Type']

        account_balance = get_account_balance(account_name, transactions)

        if account_type == 'Asset':
            print(f'{account_name[:15]:<15}\t\t{str(-round(account_balance, 2))[:7]:>7}\t\t{- round((account_balance / total_assets_1) * 100, 2)}%')
            total_assets -= account_balance

        else:
            pass

    print('Liabilities:')
    print('Account\t\t\t\tBalance')
    print('-------------------------------------------')
    total_liabilities = total_liabilities_1 = 0

    for account in accounts:
        account_name = account['Name']
        account_type = account['Type']

        account_balance = get_account_balance(account_name, transactions)

        if account_type == 'Liability':
            total_liabilities_1 += account_balance
        else:
            pass

    for account in accounts:
        account_name = account['Name']
        account_type = account['Type']

        account_balance = get_account_balance(account_name, transactions)

        if account_type == 'Liability':
            print(
                f'{account_name[:15]:<15}\t\t{str(round(account_balance, 2))[:7]:>7}\t\t{ round((account_balance / total_assets_1) * 100, 2)}%')
            total_liabilities += account_balance

        else:
            pass

    print('Equity:')
    print('Account\t\t\t\tBalance')
    print('-------------------------------------------')
    total_equity = retained_earnings = 0

    for account in accounts:
        account_name = account['Name']
        account_type = account['Type']

        account_balance = get_account_balance(account_name, transactions)

        if account_type == 'Equity':
            print(f'{account_name[:15]:<15}\t\t{str(round(account_balance, 2))[:8]:>8}\t{ round((account_balance / total_assets_1) * 100, 2)}%')
            total_equity += account_balance
        if account_type == 'Revenue':
            total_equity += account_balance
            retained_earnings += account_balance
        if account_type == 'Expense':
            total_equity += account_balance
            retained_earnings += account_balance
        else:
            pass

    print(f'Retained Earnings\t{str(round(retained_earnings, 2))[:7]:>7}\t\t{ round((retained_earnings / total_assets_1) * 100, 2)}%')

    print('-------------------------------------------')
    print(f'Total Assets:\t\t\t{str(round(total_assets, 2))[:10]:>10}\t{round((total_assets / total_assets_1) * 100, 2)}%')
    print(f'Total Liabilities:\t\t{str(round(total_liabilities, 2))[:10]:>10}\t{round((total_liabilities / total_assets_1) * 100, 2)}%')
    print(f'Total Equity:\t\t\t{str(round(total_equity, 2))[:10]:>10}\t{round((total_equity / total_assets_1) * 100, 2)}%')
    print('-------------------------------------------')


def show_income_statement():
    transactions = load_transactions()
    accounts = load_accounts()
    print('Income Statement')
    print('-------------------------------------------')
    print('Revenue:')
    print('Account\t\tAmount')
    print('-------------------------------------------')
    total_revenue = 0

    for account in accounts:
        account_name = account['Name']
        account_type = account['Type']

        account_balance = abs(get_account_balance(account_name, transactions))

        if account_type == 'Revenue':
            print(f'{account_name[:15]:<15}\t\t{round(account_balance, 2)}')
            total_revenue += account_balance
        else:
            pass

    print('-------------------------------------------')
    try:
        print(f'Total Revenue:\t\t{round(total_revenue, 2)}\t\t{(total_revenue/total_revenue) * 100}%')
    except ZeroDivisionError:
        print(f'Total Revenue:\t\t{round(total_revenue, 2)}\t\t0%')
    print('-------------------------------------------')

    print('Expenses:')
    print('Account\t\tAmount')
    print('-------------------------------------------')
    total_expenses = 0

    for account in accounts:
        account_name = account['Name']
        account_type = account['Type']

        account_balance = abs(get_account_balance(account_name, transactions))

        if account_type == 'Expense':
            print(f'{account_name[:15]:<15}\t\t{round(account_balance, 2)}')
            total_expenses += account_balance
        else:
            pass

    print('-------------------------------------------')
    try:
        print(f'Total Expense:\t\t{round(total_expenses, 2)}\t\t{round((total_expenses / total_revenue) * 100, 2)}%')
    except ZeroDivisionError:
        print(f'Total Revenue:\t\t{round(total_expenses, 2)}\t\t0%')
    print('-------------------------------------------')

    net_income = total_revenue - total_expenses
    try:
        print(f'Net Income:\t\t\t{round(net_income, 2)}\t\t{round((net_income / total_revenue) * 100, 2)}%')
    except ZeroDivisionError:
        print(f'Net income:\t\t{round(net_income, 2)}\t\t0%')
    print('-------------------------------------------')


def list_accounts():
    accounts = load_accounts()
    accounts.sort(key=lambda acc: acc['Name'])  # Sort accounts alphabetically by name

    if [acc['Status'] for acc in accounts if acc['Status'] == 'Active']:
        print('Assets:')
        asset_accounts = [acc['Name'] for acc in accounts if acc['Type'] == 'Asset']
        print_accounts(asset_accounts)

        print('Liabilities:')
        liability_accounts = [acc['Name'] for acc in accounts if acc['Type'] == 'Liability']
        print_accounts(liability_accounts)

        print('Equity:')
        equity_accounts = [acc['Name'] for acc in accounts if acc['Type'] == 'Equity']
        print_accounts(equity_accounts)

        print('Revenue:')
        revenue_accounts = [acc['Name'] for acc in accounts if acc['Type'] == 'Revenue']
        print_accounts(revenue_accounts)

        print('Expense:')
        expense_accounts = [acc['Name'] for acc in accounts if acc['Type'] == 'Expense']
        print_accounts(expense_accounts)
    else:
        pass


def print_accounts(accounts):
    if accounts:
        print(' | '.join(accounts))
    else:
        print('(No accounts found)')


def end_of_month_post(poster):
    transactions = load_transactions()
    accounts = load_accounts()
    list_accounts()
    equity = input('What is the Equity Account Name: ')
    authorized = input('Who authorized the transaction(s): ')

    for account in accounts:
        account_name = account['Name']
        account_type = account['Type']

        account_balance = round(get_account_balance(account_name, transactions), 2)

        if account_balance == 0:
            pass
        else:
            if account_type == 'Revenue':
                date_2 = date.today() - timedelta(days=1)
                date_1 = date_2.strftime("%m/%d/%Y")
                account = account_name
                credit = 0
                description = 'End of Month Posting'
                source = ''
                debit = account_balance
                post_transaction_e(date_1, account, description, source, debit, credit, poster, authorized)
                post_transaction_e(date_1, equity, description, source, 0, debit, poster, authorized)
            if account_type == 'Expense':
                date_2 = date.today() - timedelta(days=1)
                date_1 = date_2.strftime("%m/%d/%Y")
                account = account_name
                description = 'End of Month Posting'
                source = ''
                credit = -account_balance
                post_transaction_e(date_1, equity, description, source, credit, 0, poster, authorized)
                post_transaction_e(date_1, account, description, source, 0, credit, poster, authorized)

        def post_transaction_e(date_1, account, description, source, debit, credit, poster, authorized):

            transactions = load_transactions()
            transactions.append({
                'Date': date_1,
                'Account': account,
                'Description': description,
                'Source': source,
                'Debit': debit,
                'Credit': credit,
                'Posted': poster,
                'Authorized': authorized
            })
            save_transactions(transactions)

            print('Transaction posted successfully.')


def main_menu():
    create_accounts_file()
    create_transactions_file()
    poster = input('What is you abbreviation: ')
    while True:
        print('========== Accounting Software ==========')
        print('1. Post Transaction')
        print('2. Add Account')
        print("3. Change Account's Status")
        print('4. Show General Ledger')
        print('5. Show Ledger for Account')
        print('6. Show Balance Sheet')
        print('7. Show Income Statement')
        print('8. End of Month Posting')
        print('9. Exit')

        choice = input('Enter your choice: ')

        if choice == '1':
            post_transaction(poster)
        elif choice == '2':
            add_account()
        elif choice == '3':
            change_account_status()
        elif choice == '4':
            show_general_ledger()
        elif choice == '5':
            list_accounts()
            account = input('Enter the account name: ')
            show_ledger(account)
        elif choice == '6':
            show_balance_sheet()
        elif choice == '7':
            show_income_statement()
        elif choice == '8':
            end_of_month_post(poster)
        elif choice == '9':
            break
        else:
            print('Invalid choice. Please try again.')


if __name__ == '__main__':
    main_menu()
