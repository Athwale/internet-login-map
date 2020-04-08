from Database import Database
import os


def print_record(data):
    """

    :param data:
    :return:
    """
    pass


if __name__ == "__main__":
    database = Database(os.path.realpath(os.path.join('.', 'data.yml')))
    print(database.validate())
