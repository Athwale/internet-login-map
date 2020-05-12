# internet-login-map
Website login database capable of drawing a graph of user's presence on the net.

Example data can be found in data.yml

### Usage:
Usage: ./Cli.py  -a | -g | -l | -d ID | -s STRING [-f FILE] 
Examples:
./Cli.py -a
./Cli.py -g
./Cli.py -d 42
./Cli.py -s bear
./Cli.py -s bear -f database.yml
./Cli.py -l

Options:
  -h, --help            show this help message and exit
  -a, --add             Run the process of adding a record into database
  -d DELETE_ID, --delete=DELETE_ID
                        Delete a database record with the passed ID
  -f DATABASE_FILE, --file=DATABASE_FILE
                        Open database in the file, if empty the first yaml
                        file in the directory is used
  -g, --graph           Create a graph of the database
  -l, --list            List all records in database
  -s SEARCH_STRING, --search=SEARCH_STRING
                        Search for this string in the database, if empty all
                        records are printed
