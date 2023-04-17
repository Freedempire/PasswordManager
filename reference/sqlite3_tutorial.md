# Python SQLite3 tutorial (Database programming)

From: <https://likegeeks.com/python-sqlite3-tutorial/>

Also check: <https://www.sqlite.org/lang.html>

SQLite in general is a server-less database that you can use within almost all programming languages including Python. Server-less means there is no need to install a separate server to work with SQLite so you can connect directly with the database.

SQLite is a lightweight database that can provide a relational database management system with zero-configuration because there is no need to configure or set up anything to use it.

We will use SQLite version 3 or SQLite3, so let’s get started.

## Create Connection

To use SQLite3 in Python, first of all, you will have to import the `sqlite3` module and then create a `Connection` object which will connect to the database and will let us execute the SQL statements.

You can a connection object using the `connect()` function:

```python
import sqlite3
con = sqlite3.connect('mydatabase.db')
```

That will create a new file with the name 'mydatabase.db'.

## SQLite3 Cursor

To execute SQLite statements in Python, you need a `Cursor` object. A `Cursor` object represents a database cursor which is used to execute SQL statements, and manage the context of a fetch operation. Cursors are created using `Connection.cursor()`, or by using any of the connection shortcut methods.

To execute the SQLite3 statements, you should establish a connection at first and then create a cursor using the `Connection` object as follows:

```python
con = sqlite3.connect('mydatabase.db')
cursor = con.cursor()
```

Now we can use the `Cursor` object to call the `execute()` method to execute any SQL queries.

Cursor objects are iterators, meaning that if you `execute()` a 'SELECT' query, you can simply iterate over the cursor to fetch the resulting rows:

```python
for row in cur.execute("SELECT t FROM data"):
    print(row)
```

## Connection shortcut methods

You can also use connection shortcut methods: the `execute()`, `executemany()`, `executescript()` methods of `Connection` class. Your code can be written more concisely because you don’t have to create the (often superfluous) `Cursor` objects explicitly. Instead, the `Cursor` objects are created implicitly and these shortcut methods return the `Cursor` objects. This way, you can execute a 'SELECT' statement and iterate over it directly using only a single call on the `Connection` object, because `Cursor` objects are iterators.

```python
# Create and fill the table.
con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE lang(name, first_appeared)")
data = [
    ("C++", 1985),
    ("Objective-C", 1984),
]
con.executemany("INSERT INTO lang(name, first_appeared) VALUES(?, ?)", data)
# con.commit() # if not committed, the following SELECT statement still provides the data expected, but the data is not actually stored in the database

# Print the table contents, ieterate cursor directly
for row in con.execute("SELECT name, first_appeared FROM lang"):
    print(row)

print("I just deleted", con.execute("DELETE FROM lang").rowcount, "rows")
# con.commit() # same as above, if not committed, the data is not actually deleted from the database

# close() is not a shortcut method and it's not called automatically;
# the connection object should be closed manually
con.close()
```

## Create Database

When you create a connection with SQLite, that will create a database file automatically if it doesn’t already exist. This database file is created on disk; we can also create a database in RAM by using `:memory:` with the connect function. This database is called *in-memory* database.

Consider the code below in which we have created a database with a `try`, `except` and `finally` blocks to handle any exceptions:

```python
import sqlite3
from sqlite3 import Error
def sql_connection():
    try:
        con = sqlite3.connect(':memory:')
        print("Connection is established: Database is created in memory")
    except Error:
        print(Error)
    finally:
        con.close()
sql_connection()
```

First, we import the `sqlite3` module, then we define a function `sql_connection`. Inside this function, we have a `try` block where the `connect()` function is returning a `Connection` object after establishing the connection.

Then we have `except` block, which in case of any exceptions prints the error message. If there are no errors, the connection will be established and will display a message indicating a successful connection.

After that, we have closed our connection in the `finally` block. Closing a connection is optional, but it is a good programming practice, so you free the memory from any unused resources.

## Create Table

To create a table in SQLite3, you can use the 'CREATE TABLE' query in the `execute()` method. Consider the following steps:

1. Create a connection object.
2. From the connection object, create a cursor object.
3. Using the cursor object, call the execute method with 'CREATE TABLE' query as the parameter.

Let’s create employees with the following attributes:

```txt
employees (id, name, salary, department, position, hireDate)
```

The code will be like this:

```python
import sqlite3
from sqlite3 import Error

def sql_connection():
    try:
        con = sqlite3.connect('mydatabase.db')
        return con
    except Error:
        print(Error)

def sql_table(con):
    cursor = con.cursor()
    cursor.execute('''
        CREATE TABLE employees(
            id INTEGER PRIMARY KEY,
            name TEXT,
            salary REAL,
            department TEXT,
            position TEXT,
            hireDate REAL
        )
    ''')
    con.commit()

con = sql_connection()
sql_table(con)
```

In the above code, we have defined two functions, the first one establishes a connection and the second one creates a cursor to execute the 'CREATE TABLE' statement.

The `commit()` method saves all the changes we make. In the end, both functions are called.

To check if our table is created, you can use the [DB browser for SQLite](https://github.com/sqlitebrowser/sqlitebrowser) to view your table.

## Insert in Table

To insert data in a table, we use the 'INSERT INTO' statement. Consider the following line of code:

```python
cursor.execute("INSERT INTO employees VALUES(1, 'John', 700, 'HR', 'Manager', '2017-01-04')")
con.commit()
```

We can also pass values/arguments to an 'INSERT' statement in the `execute()` method. You can use the question mark (`?`) as a placeholder for each value. The syntax will be like the following:

```python
cursor.execute('''
    INSERT INTO employees(
        id, name, salary, department, position, hireDate
    ) VALUES(?, ?, ?, ?, ?, ?)
    ''', entities
)
```

Where `entities` contain the values for the placeholders as follows:

```python
entities = (2, 'Andrew', 800, 'IT', 'Tech', '2018-02-06')
```

The entire code is as follows:

```python
import sqlite3
con = sqlite3.connect('mydatabase.db')
def sql_insert(con, entities):
    cursor = con.cursor()   
    cursor.execute('INSERT INTO employees(id, name, salary, department, position, hireDate) VALUES(?, ?, ?, ?, ?, ?)', entities)   
    con.commit()
entities = (2, 'Andrew', 800, 'IT', 'Tech', '2018-02-06')
sql_insert(con, entities)
```

## Update Table

To update the table, simply create a connection, then create a cursor using the connection and finally use the 'UPDATE' statement in the `execute()` method.

Suppose that we want to update the name of the employee whose id equals 2. For updating, we will use the 'UPDATE' statement, and for the employee whose id equals 2, we will use the 'WHERE' clause as a condition to select this employee.

Consider the following code:

```python
import sqlite3
con = sqlite3.connect('mydatabase.db')
def sql_update(con):
    cursor = con.cursor()
    cursor.execute('UPDATE employees SET name = "Rogers" where id = 2')
    con.commit()
sql_update(con)
```

## Select statement

You can use the 'SELECT' statement to select data from a particular table. If you want to select all the columns of the data from a table, you can use the asterisk (`*`). The syntax for this will be as follows:

```python
select * from table_name
```

In SQLite3, the 'SELECT' statement is executed in the `execute` method of the `Cursor` object. For example, select all the columns of the employees table, run the following code:

```python
cursor.execute('SELECT * FROM employees')
```

If you want to select a few columns from a table, then specify the columns like the following:

```python
select column1, column2 from tables_name
```

For example,

```python
cursor.execute('SELECT id, name FROM employees')
```

## Fetch all data

To fetch the data from a database, we will execute the 'SELECT' statement and then use the `fetchall()` method of the cursor object to store the values into a variable. After that, we will loop through the variable and print all values.

The code will be like this:

```python
import sqlite3
con = sqlite3.connect('mydatabase.db')
def sql_fetch(con):
    cursor = con.cursor()
    cursor.execute('SELECT * FROM employees')
    rows = cursor.fetchall()
    for row in rows:
        print(row)
sql_fetch(con)
```

If you want to fetch specific data from the database, you can use the 'WHERE' clause. For example, we want to fetch the ids and names of those employees whose salary is greater than 800.

```python
import sqlite3
con = sqlite3.connect('mydatabase.db')
def sql_fetch(con):
    cursor = con.cursor()
    cursor.execute('SELECT id, name FROM employees WHERE salary > 800.0')
    rows = cursor.fetchall()
    for row in rows:
        print(row)
sql_fetch(con)
```

In the above 'SELECT' statement, instead of using the asterisk (`*`), we specified the id and name attributes.

## SQLite3 rowcount

The SQLite3 rowcount is used to return the number of rows that are affected or selected by the latest executed SQL query.

It is a read-only attribute that provides the number of modified rows for 'INSERT', 'UPDATE', 'DELETE', and 'REPLACE' statements; is `-1` for other statements, including CTE (common table expression) queries. It is only updated by the `execute()` and `executemany()` methods.

When we use `rowcount` with the 'SELECT' statement, `-1` will be returned. Therefore, you need to fetch all the data, and then get the length of the result:

```python
rows = cursor.fetchall()
print(len(rows))
```

When you use the 'DELETE' statement without any condition (a 'WHERE' clause), that will delete all the rows in the table, and it will return the total number of deleted rows in `rowcount`. If no row is deleted, it will return `0`.

## List tables

To list all tables in an SQLite3 database, you should query the `sqlite_master` table and then use `fetchall()` to fetch the results from the 'SELECT' statement.

The `sqlite_master` is the master table in SQLite3, which stores all tables.

```python
import sqlite3
con = sqlite3.connect('mydatabase.db')
def sql_fetch(con):
    cursor = con.cursor()
    cursor.execute('SELECT name from sqlite_master where type = "table"')
    print(cursor.fetchall())
sql_fetch(con)
```

## Check if a table exists or not

When creating a table, we should make sure that the table is not already existed. Similarly, when removing/ deleting a table, the table should exist.

To check if the table doesn’t already exist, we use 'IF NOT EXISTS' with the 'CREATE TABLE' statement as follows:

```txt
create table if not exists table_name (column1, column2, …, columnN)
```

For example:

```python
import sqlite3
con = sqlite3.connect('mydatabase.db')
def sql_fetch(con):
    cursor = con.cursor()
    cursor.execute('create table if not exists projects(id integer, name text)')
    con.commit()
sql_fetch(con)
```

Similarly, to check if the table exists when deleting, we use 'IF EXISTS' with the 'DROP TABLE' statement as follows:

```txt
drop table if exists table_name
```

For example,

```python
cursor.execute('drop table if exists projects')
```

We can also check if the table we want to access exists or not by executing the following query:

```python
cursor.execute('SELECT name from sqlite_master WHERE type = "table" AND name = "employees"')
print(cursor.fetchall())
```

If the `employees` table exists, it will return its name.

If the table name we specified doesn’t exist, an empty array will be returned.

## Drop table

You can drop/delete a table using the 'DROP' statement. The syntax of the 'DROP' statement is as follows:

```txt
drop table table_name
```

To drop a table, the table should exist in the database. Therefore, it is recommended to use 'IF EXISTS' with the 'DROP' statement.

For example:

```python
import sqlite3
con = sqlite3.connect('mydatabase.db')
def sql_fetch(con):
    cursor = con.cursor()
    cursor.execute('DROP TABLE IF EXISTS employees')
    con.commit()
sql_fetch(con)
```

## SQLite3 exceptions

Exceptions are run time errors. In Python programming, all exceptions are the instances of class derived from `BaseException`.

In SQLite3, we have the following exceptions:

- `DatabaseError`: Any error related to the database raises the `DatabaseError`.
- `IntegrityError`: `IntegrityError` is a subclass of `DatabaseError` and is raised when there is a data integrity issue. For example, foreign data isn’t updated in all tables resulting in the inconsistency of the data.
- `ProgrammingError`: The exception `ProgrammingError` raises when there are syntax errors or table is not found or function is called with the wrong number of parameters/ arguments.
- `OperationalError`: This exception is raised when the database operations are failed, for example, unusual disconnection. This is not the fault of the programmers.
- `NotSupportedError`: When you use some methods that aren’t defined or supported by the database, that will raise the `NotSupportedError` exception.

## SQLite3 executemany

`executemany(sql, parameters, /)`: For every item in `parameters`, repeatedly execute the parameterized SQL statement `sql`. `sql` (str) is a single SQL DML (data manipulation language) statement.

You can use `executemany()` to *insert* multiple rows at once.

Consider the following code:

```python
import sqlite3
con = sqlite3.connect('mydatabase.db')
cursor = con.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS projects(id INTEGER, name TEXT)')
data = [(1, "Ridesharing"), (2, "Water Purifying"), (3, "Forensics"), (4, "Botany")]
cursor.executemany("INSERT INTO projects VALUES(?, ?)", data)
con.commit()
```

Here we created a table with two columns, and `data` has four values for each column. We pass the variable to `executemany()` method along with the query.

Note that we have used the placeholder (`?`) to bind the values.

## SQLite3 executescript

`executescript(sql_script, /)`: Execute the SQL statements in `sql_script`. If there is a pending transaction, an implicit 'COMMIT' statement is executed first. No other implicit transaction control is performed; any transaction control must be added to `sql_script`. `sql_script` must be a string.

Example:

```python
# cur is an sqlite3.Cursor object
cur.executescript("""
    BEGIN;
    CREATE TABLE person(firstname, lastname, age);
    CREATE TABLE book(title, author, published);
    CREATE TABLE publisher(name, address);
    COMMIT;
""")
```

## How to use the connection context manager

A `Connection` object can be used as a context manager that automatically commits or rolls back open transactions when leaving the body of the context manager. If the body of the `with` statement finishes without exceptions, the transaction is committed. If this commit fails, or if the body of the `with` statement raises an uncaught exception, the transaction is rolled back.

If there is no open transaction upon leaving the body of the `with` statement, the context manager is a no-op.

> Note The context manager neither implicitly opens a new transaction nor closes the connection.

```python
con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE lang(id INTEGER PRIMARY KEY, name VARCHAR UNIQUE)")

# Successful, con.commit() is called automatically afterwards
with con:
    con.execute("INSERT INTO lang(name) VALUES(?)", ("Python",))

# con.rollback() is called after the with block finishes with an exception,
# the exception is still raised and must be caught
try:
    with con:
        con.execute("INSERT INTO lang(name) VALUES(?)", ("Python",))
except sqlite3.IntegrityError:
    print("couldn't add Python twice")

# Connection object used as context manager only commits or rollbacks transactions,
# so the connection object should be closed manually
con.close()
```

## Close Connection

Once you are done with your database, it is a good practice to close the connection. You can close the connection by using the `close()` method.

```python
con = sqlite3.connect('mydatabase.db')
#program statements
con.close()
```

## SQLite3 datetime

In the Python SQLite3 database, we can easily store date or time by importing the datatime module. The following formats are the most common formats you can use for datetime:

```txt
YYYY-MM-DD
YYYY-MM-DD HH:MM
YYYY-MM-DD HH:MM:SS
YYYY-MM-DD HH:MM:SS.SSS
HH:MM
HH:MM:SS
HH:MM:SS.SSS
now
```

Consider the following code:

```python
import sqlite3
import datetime
con = sqlite3.connect('mydatabase.db')
cursor = con.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS assignments(id INTEGER, name TEXT, date TEXT)')
data = [(1, "Ridesharing", datetime.date(2017, 1, 2)), (2, "Water Purifying", datetime.date(2018, 3, 4))]
cursor.executemany("INSERT INTO assignments VALUES(?, ?, ?)", data)
con.commit()
```

In this code, we imported the `datetime` module first, and we have created a table named `assignments` with three columns.

To insert the date in the column, we have used `datetime.date()`. Similarly, we can use `datetime.time()` to handle time.

The great flexibility and mobility of the SQLite3 database make it the first choice for any developer to use it and ship it with any product he works with.

You can use SQLite3 databases in Windows, Linux, Mac OS, Android, and iOS projects due to their awesome portability. So you ship one file with your project and that’s it.
