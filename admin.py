from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import re
import hashlib

app = Flask(__name__)

app.secret_key = "secret"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'hackerman'
app.config['MYSQL_DB'] = 'shopDB'

mysql = MySQL(app)

def loginAdmin(username, password):
    # hash pwd with md5
    hashPwd = hashlib.sha256(password.encode())
    hash = hashPwd.hexdigest()
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM adminAccounts WHERE adminUsername = %s AND password = '
                '%s', (username, hash))
    account = cur.fetchone()
    cur.close()
    return account

def adminHome():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM products')
    products = cur.fetchall()
    cur.close()
    return products

def adminOrders():
    #Get all placed orders.
    #fetch transaction data
    #Fetch username
    data = []
    prods = 0
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM transactions')
    transactions = cur.fetchall()
    for item in transactions:
        temp = []
        cur.execute('SELECT products.productName, products.price, products.available, transactionOrders.quantity FROM transactionOrders, products WHERE transactionOrders.productID = products.productID and transactionOrders.oldBasketID=%s', (item[0],))
        itemData = list(cur.fetchall())
        itemData = [list(itemD) for itemD in itemData]
        #print(str(itemData))
        for itemD in itemData:
            #print(str(itemD))
            itemD[1] = str(itemD[1]) + " KR"
            itemD[2] = "Availability: " + str(itemD[2])
            itemD[3] = "Bought " + str(itemD[3]) + " Pieces"
        temp.append(item)
        temp.append(itemData)
        data.append(temp)
    cur.close()
    return data
