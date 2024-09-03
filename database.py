# database.py
import sqlite3

def create_database():
    """
    Creates the comparison database table if it doesn't already exist.
    """
    try:
        conn = sqlite3.connect('comparison.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS comparisons (
                        product_id TEXT,
                        timestamp DATETIME,
                        price REAL
                     )''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while creating the database: {e}")
    finally:
        conn.close()

def insert_comparison(product_id, price):
    """
    Inserts a new comparison entry into the comparisons table.
    
    :param product_id: The ID of the product.
    :param price: The price of the product at the current time.
    """
    try:
        conn = sqlite3.connect('comparison.db')
        c = conn.cursor()
        c.execute('INSERT INTO comparisons (product_id, timestamp, price) VALUES (?, datetime("now"), ?)',
                  (product_id, price))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while inserting a comparison entry: {e}")
    finally:
        conn.close()

# Initialize database
if __name__ == "__main__":
    create_database()
