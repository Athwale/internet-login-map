from Database import Database
import os

if __name__ == "__main__":
    database = Database(os.path.realpath(os.path.join('.', 'data.yml')))

