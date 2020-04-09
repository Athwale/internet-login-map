from Database import Database
from colorama import Fore, Style
import os
from colorama import Fore


def print_message(message: str):
    """
    Print a nice looking message on the screen.
    :param message:
    :return: None
    """
    print('## ' + str(message) + '\n')


def print_record(records):
    """
    Nice print the passed list of records.
    :param records: List of yaml records
    :return: None
    """
    for record in records:
        for name, values in record.items():
            print('\n' + Fore.GREEN + str(name) + Fore.RESET)
            if '@' in name:
                print('\t' + 'login: ' + Fore.LIGHTBLUE_EX + name.split('@')[0] + Fore.RESET)
            for attribute, content in values.items():
                if attribute in ['email', 'linkto']:
                    if attribute == 'email':
                        if content:
                            print('\t' + 'e-mails:')
                        else:
                            print('\t' + 'e-mails: -')
                    else:
                        if content:
                            print('\t' + 'link to:')
                        else:
                            print('\t' + 'link to: -')
                    if content:
                        for item in content:
                            print('\t\t' + Fore.YELLOW + str(item) + Fore.RESET)
                else:
                    print('\t' + str(attribute) + ': ' + ('-' if not content else Fore.LIGHTBLUE_EX + str(content) + Fore.RESET))


if __name__ == "__main__":
    database = Database(os.path.realpath(os.path.join('.', 'data.yml')))
    if database.validate():
        print_message('Database OK')
    found = database.find('bear')
    print_record(found)
