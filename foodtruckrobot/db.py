import sqlite3

def create(name):
    con = sqlite3.connect(name)

    # Orders
    con.execute("CREATE TABLE IF NOT EXISTS orders (date text, content text, user text)")

    # Numbers
    con.execute('DROP TABLE IF EXISTS numbers')
    con.execute("CREATE TABLE numbers (name text, avatar text, number text, pending_messages integer)")
    con.execute("INSERT INTO numbers VALUES ('Thibault', 'avatar-thibault.png', '0626945671', 8)")

    # Foodtrucks
    con.execute('DROP TABLE IF EXISTS foodtrucks')
    con.execute("CREATE TABLE foodtrucks (name text, day integer, enable boolean)")
    con.execute("INSERT INTO foodtrucks VALUES ('West Corner', 2, true)")
    con.execute("INSERT INTO foodtrucks VALUES ('Tofu', 2, true)")

    con.execute("INSERT INTO foodtrucks VALUES ('Test 1', 0, true)")
    con.execute("INSERT INTO foodtrucks VALUES ('Test 2', 0, true)")

    # Menus
    con.execute('DROP TABLE IF EXISTS menus')
    con.execute("CREATE TABLE menus (foodtruck text, name text, description text, value real)")

    con.execute("INSERT INTO menus VALUES ('West Corner', 'Le californien', 'aaaaaa', 10)")
    con.execute("INSERT INTO menus VALUES ('West Corner', 'Lautre', 'aaa', 9)")

    con.execute("INSERT INTO menus VALUES ('Test 1', 'Le californien', 'aaaaaa', 10)")
    con.execute("INSERT INTO menus VALUES ('Test 1', 'Lautre', 'aaa', 9)")

    # Menus parameters

    con.commit()
    con.close()