import psycopg2
import json
import logging


class PostgreSQLProcessor:
    def __init__(self, hostName=None, dataBase=None, userName=None, pwd=None, portId=None, credFile=None):
        """
        Initialize the PostgreSQLProcessor class.
        Accepts either direct credentials or a JSON credential file path.
        """
        if credFile:
            self._load_credentials_from_file(credFile)
        else:
            self.hostName = hostName
            self.dataBase = dataBase
            self.userName = userName
            self.pwd = pwd
            self.portId = portId

        self._connect_to_database()

    def _load_credentials_from_file(self, credFile):
        """Load credentials from a JSON file."""
        try:
            with open(credFile, 'r') as file:
                data = json.load(file)
                self.hostName = data['hostName']
                self.dataBase = data['dataBase']
                self.userName = data['userName']
                self.pwd = data['pwd']
                self.portId = data['portId']
        except FileNotFoundError:
            logging.error(f"Credentials file not found: {credFile}")
            raise
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON in credentials file: {credFile}")
            raise

    def _connect_to_database(self):
        """Establish a connection to the PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(
                host=self.hostName,
                dbname=self.dataBase,
                user=self.userName,
                password=self.pwd,
                port=self.portId
            )
            self.cur = self.conn.cursor()
        except Exception as e:
            logging.error(f"Error connecting to the database: {e}")
            raise

    def sqlExecute(self, query):
        """Execute an SQL query without returning results."""
        self.cur.execute(query)
        self.conn.commit()

    def sqlFetch(self, query):
        """Fetch results from an SQL query."""
        self.cur.execute(query)
        return self.cur.fetchall()

    def sqlClose(self):
        """Close the database connection."""
        self.cur.close()
        self.conn.close()
