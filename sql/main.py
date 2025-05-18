import sqlite3

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

# Снос существующих
cursor.execute('DROP TABLE IF EXISTS tickets')
cursor.execute('DROP TABLE IF EXISTS clients')
cursor.execute('DROP TABLE IF EXISTS orders')

# Инит таблиц
cursor.execute('''
               CREATE TABLE tickets(
                ticket_id INTEGER PRIMARY KEY,
                ticket_client TEXT NOT NULL,
                csat INTEGER,
                text TEXT NOT NULL,
                date TEXT NOT NULL,
                ticket_order_id INTEGER NOT NULL
               )
               ''')

cursor.execute('''
               CREATE TABLE clients(
                client_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                city TEXT NOT NULL
               )
               ''')

cursor.execute('''
               CREATE TABLE orders(
                order_id INTEGER PRIMARY KEY,
                price INTEGER NOT NULL,
                order_client_id INTEGER NOT NULL,
                place TEXT NOT NULL
               )
               ''')

# Данные с тестового
tickets_data = [
    (None, 'Viahex', 5, 'Все отлично, спасибо!', '2024-06-19', 1),
    (None, 'Unandekou', 4, 'Заказ приехал позже', '2024-06-18', 2),
    (None, 'Qusynel', 1, 'Не доставили одну позицию', '2024-06-17', 3)
]

clients_data = [
    (None, 'Viahex', 'Антон', 19, 'Москва'),
    (None, 'Unandekou', 'Наталья', 25, 'Уфа'),
    (None, 'Qusynel', 'Виталий', 32, 'Краснодар')
]

orders_data = [
    (None, 1590, 1, 'Теремок'),
    (None, 3999, 2, 'Вкусно и точка'),
    (None, 580, 3, 'Евразия')
]

# заполнение по автоинкременты=у
cursor.executemany('''
                   INSERT INTO tickets 
                   VALUES (?, ?, ?, ?, ?, ?)
                   ''', tickets_data)

cursor.executemany('''
                   INSERT INTO clients 
                   VALUES (?, ?, ?, ?, ?)
                   ''', clients_data)

cursor.executemany('''
                   INSERT INTO orders 
                   VALUES (?, ?, ?, ?)
                   ''', orders_data)

# Выбор клов с ксатом < 3
cursor.execute('''
               SELECT ticket_client 
               FROM tickets 
               WHERE csat < 3
               ''')
print(cursor.fetchall())

# чаты с 'отлично' в тексте
cursor.execute('''
               SELECT ticket_id 
               FROM tickets 
               WHERE text LIKE '%отлично%' 
               ORDER BY csat DESC
               ''')
print("\n" * 3, cursor.fetchall())

# rich 😎 клиенты с заказами из теремка и вит
cursor.execute('''
               SELECT 
                    order_client_id AS frequent_customer,
               MAX(price) AS max_sum
               FROM orders
               WHERE 
                    place IN ('Теремок', 'Вкусно и точка')
               AND price BETWEEN 2000 AND 10000
               GROUP BY order_client_id
               HAVING COUNT(order_id) > 5
               ''')
print("\n" * 3, cursor.fetchall())

# Джоин таблиц с лимитом в 1к
cursor.execute('''
               SELECT *
               FROM orders
               LEFT JOIN clients ON orders.order_client_id = clients.client_id
               LEFT JOIN tickets ON orders.order_id = tickets.ticket_order_id
               LIMIT 1000
               ''')
print("\n" * 3, cursor.fetchall())

connection.commit()
connection.close()