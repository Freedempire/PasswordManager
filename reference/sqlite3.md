# sqlite3 — DB-API 2.0 interface for SQLite databases

From: <https://docs.python.org/3/library/sqlite3.html>

SQLite is a C library that provides a lightweight disk-based database that doesn’t require a separate server process and allows accessing the database using a nonstandard variant of the SQL query language. Some applications can *use SQLite for internal data storage*. It’s also possible to *prototype an application using SQLite and then port the code to a larger database such as PostgreSQL or Oracle*.

> See also
<https://www.sqlite.org>
The SQLite web page; the documentation describes the syntax and the available data types for the supported SQL dialect.
<https://www.w3schools.com/sql/>
Tutorial, reference and examples for learning SQL syntax.
PEP 249 - Database API Specification 2.0
PEP written by Marc-André Lemburg.

## Tutorial

1. Create a new database and open a database connection to allow sqlite3 to work with it. Call `sqlite3.connect()` to to create a connection to the database `tutorial.db` in the current working directory, implicitly creating it if it does not exist:

    ```python
    import sqlite3
    con = sqlite3.connect("tutorial.db")
    ```

    The returned `Connection` object `con` represents the connection to the on-disk database.

2. In order to execute SQL statements and fetch results from SQL queries, we will need to use a database **cursor**.

    > A database cursor is a mechanism that enables traversal over the records in a database. Cursors facilitate subsequent processing in conjunction with the traversal, such as retrieval, addition and removal of database records. The database cursor characteristic of traversal makes cursors akin to the programming language concept of *iterator*.
    >
    > Cursors are used by database programmers to process individual rows returned by database system queries. The cursor can only reference one row at a time, but can move to other rows of the result set as needed.
    >
    > In SQL procedures, a cursor makes it possible to define a result set (a set of data rows) and perform complex logic on a row by row basis. By using the same mechanics, a SQL procedure can also define a result set and return it directly to the caller of the SQL procedure or to a client application.

    Call `con.cursor()` to create the Cursor:

    ```python
    cur = con.cursor()
    ```

3. Create a database table `movie` with columns for title, release year, and review score. For simplicity, we can just use column names in the table declaration – thanks to the *flexible typing* feature of SQLite, specifying the data types is optional. Execute the `CREATE TABLE` statement by calling `cur.execute(...)`:

    ```python
    cur.execute("CREATE TABLE movie(title, year, score)")
    ```

    We can verify that the new table has been created by querying the `sqlite_master` table built-in to SQLite, which should now contain an entry for the movie table definition. Execute that query by calling `cur.execute(...)`, assign the result to `res`, and call `res.fetchone()` to fetch the resulting row:

    ```sh
    >>> res = cur.execute("SELECT name FROM sqlite_master")
    >>> res.fetchone()
    ('movie',)
    ```

    The query returns a tuple containing the table’s name. If we query `sqlite_master` for a non-existent table `spam`, `res.fetchone()` will return `None`:

    ```sh
    >>> res = cur.execute("SELECT name FROM sqlite_master WHERE name='spam'")
    >>> res.fetchone() is None
    True
    ```

4. Add two rows of data supplied as SQL literals by executing an `INSERT` statement, once again by calling `cur.execute(...)`:

    ```python
    cur.execute("""
        INSERT INTO movie VALUES
            ('Monty Python and the Holy Grail', 1975, 8.2),
            ('And Now for Something Completely Different', 1971, 7.5)
    """)
    ```

    The `INSERT` statement implicitly opens a **transaction**, which needs to be committed before changes are saved in the database.

    > A transaction is a single unit of logic or work, sometimes made up of multiple operations. Any logical calculation done in a consistent mode in a database is known as a transaction. One example is a transfer from one bank account to another: the complete transaction requires subtracting the amount to be transferred from one account and adding that same amount to the other.
    >
    > A database transaction, by definition, must be:
    >
    > - atomic: it must either be complete in its entirety or have no effect whatsoever
    > - consistent: it must conform to existing constraints in the database
    > - isolated: it must not affect other transactions
    > - durable: it must get written to persistent storage
    >
    > Database practitioners often refer to these properties of database transactions using the acronym ACID.

    Call `con.commit()` on the *connection object* to commit the transaction:

    ```python
    con.commit()
    ```

    We can verify that the data was inserted correctly by executing a `SELECT` query. Use `cur.execute(...)` to assign the result to `res`, and call `res.fetchall()` to return all resulting rows:

    ```sh
    >>> res = cur.execute("SELECT score FROM movie")
    >>> res.fetchall()
    [(8.2,), (7.5,)]
    ```

    The result is a list of two tuples, one per row, each containing that row’s `score` value.

5. Insert three more rows by calling `cur.executemany(...)`:

    ```python
    data = [
        ("Monty Python Live at the Hollywood Bowl", 1982, 7.9),
        ("Monty Python's The Meaning of Life", 1983, 7.5),
        ("Monty Python's Life of Brian", 1979, 8.0),
    ]
    cur.executemany("INSERT INTO movie VALUES(?, ?, ?)", data)
    con.commit()  # Remember to commit the transaction after executing INSERT.
    ```

    Notice that `?` placeholders are used to bind data to the query. Always use placeholders instead of string formatting to bind Python values to SQL statements, to avoid *SQL injection attacks*.

    We can verify that the new rows were inserted by executing a `SELECT` query, this time iterating over the results of the query:

    ```sh
    >>> for row in cur.execute("SELECT year, title FROM movie ORDER BY year"):
    ...     print(row)
    (1971, 'And Now for Something Completely Different')
    (1975, 'Monty Python and the Holy Grail')
    (1979, "Monty Python's Life of Brian")
    (1982, 'Monty Python Live at the Hollywood Bowl')
    (1983, "Monty Python's The Meaning of Life")
    ```

    Each row is a two-item tuple of `(year, title)`, matching the columns selected in the query.

6. Verify that the database has been written to disk by calling `con.close()` to close the existing connection, opening a new one, creating a new cursor, then querying the database:

    ```sh
    >>> con.close()
    >>> new_con = sqlite3.connect("tutorial.db")
    >>> new_cur = new_con.cursor()
    >>> res = new_cur.execute("SELECT title, year FROM movie ORDER BY score DESC")
    >>> title, year = res.fetchone()
    >>> print(f'The highest scoring Monty Python movie is {title!r}, released in {year}')
    The highest scoring Monty Python movie is 'Monty Python and the Holy Grail', released in 1975
    ```

## Reference

### SQLite and Python types

SQLite natively supports the following types: `NULL`, `INTEGER`, `REAL`, `TEXT`, `BLOB`.

The following Python types can thus be sent to SQLite without any problem:

|Python type|SQLite type|
|---|---|
|`None`|`NULL`|
|int|`INTEGER`|
|float|`REAL`|
|str|`TEXT`|
|bytes|`BLOB`|

This is how SQLite types are converted to Python types by default:
|SQLite type|Python type|
|---|---|
|`NULL`|`None`|
|`INTEGER`|int|
|`REAL`|float|
|`TEXT`|depends on text_factory, str by default|
|`BLOB`|bytes|

The type system of the sqlite3 module is extensible in two ways: you can store additional Python types in an SQLite database via object adapters, and you can let the sqlite3 module convert SQLite types to Python types via converters.

## How-to guides

### How to use connection shortcut methods

Using the `execute()`, `executemany()`, and `executescript()` methods of the `Connection` class, your code can be written more concisely because you don’t have to create the (often superfluous) `Cursor` objects explicitly. Instead, the `Cursor` objects are created implicitly and these shortcut methods return the `Cursor` objects. This way, you can execute a `SELECT` statement and iterate over it directly using only a single call on the `Connection` object.

```python
# Create and fill the table.
con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE lang(name, first_appeared)")
data = [
    ("C++", 1985),
    ("Objective-C", 1984),
]
con.executemany("INSERT INTO lang(name, first_appeared) VALUES(?, ?)", data)

# Print the table contents
for row in con.execute("SELECT name, first_appeared FROM lang"):
    print(row)

print("I just deleted", con.execute("DELETE FROM lang").rowcount, "rows")

# close() is not a shortcut method and it's not called automatically;
# the connection object should be closed manually
con.close()
```

### How to use the connection context manager

A `Connection` object can be used as a context manager that automatically *commits* or *rolls back* open *transactions* when leaving the body of the context manager. If the body of the `with` statement finishes without exceptions, the transaction is committed. If this commit fails, or if the body of the with statement raises an uncaught exception, the transaction is rolled back.

If there is no open transaction upon leaving the body of the `with` statement, the context manager is a no-op.

> NOP or NOOP is short for no operation, common assembly language instruction. An instruction or operation that has no effect; a null operation.

Note The context manager neither implicitly opens a new transaction nor closes the connection.

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
