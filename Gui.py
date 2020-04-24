import os
import shutil
from os import system

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

    def main_loop(self) -> None:
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
    def format_records(records) -> str:
        """
        Return a nice string version of the record list passed into the method for display in GUI.
        :param records: List of yaml records
        :return: str, formatted string version of the records.
        """
        string = ''
        for record in records:
            for name, values in record.items():
                string += '\n' + str(name) + '\n'
                for attribute, content in values.items():
                    if attribute in ['email', 'linkto']:
                        if attribute == 'email':
                            if content:
                                string += ' e-mails:\n'
                            else:
                                string += ' e-mails: -\n'
                        else:
                            if content:
                                string += ' link to:\n'
                            else:
                                string += ' link to: -\n'
                        if content:
                            for item in content:
                                string += '    ' + str(item) + '\n'
                    else:
                        string += ' ' + str(attribute) + ': ' + (
                            '-\n' if not content else str(content) + '\n')
        return string

    def menu_find(self, dialog) -> None:
        """
        Handle Find option from menu. Get input from user, find the records in database and display them.
        :param dialog: Dialog object that displays Gui in terminal.
        :return: None
        """


    def menu_add(self, dialog) -> None:
        """

        :param dialog:
        :return:
        """

    def menu_delete(self, dialog) -> None:
        """

        :param dialog:
        :return:
        """

    def menu_graph(self, dialog) -> None:
        """

        :param dialog:
        :return:
        """


if __name__ == "__main__":
    data = 'data.yml'
    gui = Gui(data)
    gui.main_loop()

