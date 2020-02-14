from os import getenv

import mysql.connector


class MySQL:

    def __init__(self):
        self.__connection = None
        self.__cursor = None

    async def connect(self, prepared):
        try:
            cnx = mysql.connector.connect(
                host=getenv("DB_HOST"),
                user=getenv("DB_USERNAME"),
                passwd=getenv("DB_PASSWORD"),
                database=getenv("DB_DATABASE")
            )
            self.__connection = cnx
            self.__cursor = cnx.cursor(prepared=prepared)
        except mysql.connector.errors.Error as ex:
            print(ex)

        print('(MySQL) Connection established!')

    def close(self):
        self.__connection.close()
        self.__cursor.close()

        print('(MySQL) Connection closed!')

    @property
    def connection(self):
        return self.__connection

    @property
    def cursor(self):
        return self.__cursor
