import os
import shutil

from colorama import Fore
from dialog import Dialog
from os import system

from Database import Database


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
                    print('\t' + str(attribute) + ': ' + (
                        '-' if not content else Fore.LIGHTBLUE_EX + str(content) + Fore.RESET))


def menu_find(dialog):
    """

    :param dialog:
    :return:
    """
    code, string = dialog.inputbox('Find')
    if code != 'ok':
        return


def menu_add(dialog):
    """

    :param dialog:
    :return:
    """


def menu_delete(dialog):
    """

    :param dialog:
    :return:
    """


def menu_graph(dialog):
    """

    :param dialog:
    :return:
    """


if __name__ == "__main__":
    data = 'data.yml'
    shutil.copyfile(data, 'workCopy.yml')
    database = Database()
    if database.load(os.path.realpath(os.path.join('.', 'workCopy.yml'))):
        print_message('Database OK')

    # Create text based gui
    d = Dialog(dialog="dialog")
    while True:
        selection = d.radiolist("Menu", choices=[('Find', 'Find database records', True),
                                                 ('Add', 'Add a new record', False),
                                                 ('Delete', 'Remove database record', False),
                                                 ('Graph', 'Create database graph', False)])
        if selection[0] == 'ok':
            command = selection[1]
            if command == 'Find':
                menu_find(d)
            elif command == 'Add':
                menu_add(d)
            elif command == 'Delete':
                menu_delete(d)
            else:
                menu_graph(d)
        else:
            break
    system('clear')

