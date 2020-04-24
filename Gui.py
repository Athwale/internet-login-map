import os
import shutil
from os import system

from colorama import Fore
from dialog import Dialog

from Database import Database


class Gui:

    def __init__(self, database_file):
        """
        Gui class constructor. Initialize database file name and database object.
        :param database_file:
        """
        self._database_file = database_file
        self._database = Database()

    def main_loop(self):
        """
        Main Gui function to display console text based gui and handle inputs.
        :return: None
        """
        d = Dialog(dialog="dialog")
        shutil.copyfile(self._database_file, 'workCopy.yml')
        if self._database.load(os.path.realpath(os.path.join('.', 'workCopy.yml'))):
            d.msgbox('Database file load OK:\n' + str(self._database_file))

        while True:
            selection = d.radiolist("Menu", choices=[('Find', 'Find database records', True),
                                                     ('Add', 'Add a new record', False),
                                                     ('Delete', 'Remove database record', False),
                                                     ('Graph', 'Create database graph', False)])
            if selection[0] == 'ok':
                command = selection[1]
                if command == 'Find':
                    self.menu_find(d)
                elif command == 'Add':
                    self.menu_add(d)
                elif command == 'Delete':
                    self.menu_delete(d)
                else:
                    self.menu_graph(d)
            else:
                break
        system('clear')

    @staticmethod
    def format_records(records):

        """
        Nice print the passed list of records.
        :param records: List of yaml records
        :return: None
        """
        string = ''
        for record in records:
            for name, values in record.items():
                string += '\n' + Fore.GREEN + str(name) + Fore.RESET
                for attribute, content in values.items():
                    if attribute in ['email', 'linkto']:
                        if attribute == 'email':
                            if content:
                                string += '\t' + 'e-mails:'
                            else:
                                string += '\t' + 'e-mails: -'
                        else:
                            if content:
                                string += '\t' + 'link to:'
                            else:
                                string += '\t' + 'link to: -'
                        if content:
                            for item in content:
                                string += '\t\t' + Fore.YELLOW + str(item) + Fore.RESET
                    else:
                        string += '\t' + str(attribute) + ': ' + (
                            '-' if not content else Fore.LIGHTBLUE_EX + str(content) + Fore.RESET)

    def menu_find(self, dialog):
        """

        :param dialog:
        :return:
        """
        code, string = dialog.inputbox('Find')
        if code != 'ok':
            return
        dialog.msgbox('text')

    def menu_add(self, dialog):
        """

        :param dialog:
        :return:
        """

    def menu_delete(self, dialog):
        """

        :param dialog:
        :return:
        """

    def menu_graph(self, dialog):
        """

        :param dialog:
        :return:
        """


if __name__ == "__main__":
    data = 'data.yml'
    gui = Gui(data)
    gui.main_loop()

