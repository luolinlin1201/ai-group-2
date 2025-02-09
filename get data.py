import mysql.connector
import yfinance as yf
import pandas as pd
from datetime import datetime

def connect_to_database():
    connection = mysql.connector.connect(
        host='localhost',        
        user='root',    
        password='200707UVAuva$',  
        database='financial_data' 
    )
    return connection

def check_if_data_exists(ticker, timestamp):
    conn = connect_to_database()
    cursor = conn.cursor()

    query = "SELECT * FROM stock_data WHERE ticker = %s AND timestamp = %s"
    cursor.execute(query, (ticker, timestamp)) 

    result = cursor.fetchone()  
    conn.close()

    return result is not None

def fetch_stock_data(ticker, period="1d", interval="1m"):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=interval)  

    data_tuples = []
    for index, row in data.iterrows():
        timestamp_str = index.strftime('%Y-%m-%d %H:%M:%S')

        open_price = round(float(row['Open']), 2)
        high_price = round(float(row['High']), 2)
        low_price = round(float(row['Low']), 2)
        close_price = round(float(row['Close']), 2)
        volume = int(row['Volume']) 

        data_tuples.append((ticker, timestamp_str, open_price, high_price, low_price, close_price, volume))

    return data_tuples

def insert_stock_data(data_tuples):
    conn = connect_to_database()
    cursor = conn.cursor()

    query = """
    INSERT INTO stock_data (ticker, timestamp, open_price, high_price, low_price, close_price, volume)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    open_price = VALUES(open_price),
    high_price = VALUES(high_price),
    low_price = VALUES(low_price),
    close_price = VALUES(close_price),
    volume = VALUES(volume)
    """
    
    cursor.executemany(query, data_tuples)
    conn.commit()
    conn.close()

def fetch_and_store_data(ticker, period="1d", interval="1m"):
    data_tuples = fetch_stock_data(ticker, period, interval)

    for data in data_tuples:
        timestamp = data[1]  
        if not check_if_data_exists(ticker, timestamp):
            insert_stock_data([data])  

fetch_and_store_data('AAPL', period="1d", interval="1m")