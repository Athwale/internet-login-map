from Database import Database
import os


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
            print(name)


if __name__ == "__main__":
    database = Database(os.path.realpath(os.path.join('.', 'data.yml')))
    if database.validate():
        print_message('Database OK')
    found = database.find('bear')
    print_record(found)
