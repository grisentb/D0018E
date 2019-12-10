from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import re
import admin
import hashlib


app = Flask(__name__)

app.secret_key = "secret"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'user'
app.config['MYSQL_PASSWORD'] = 'userhacker'
app.config['MYSQL_DB'] = 'shopDB'

mysql = MySQL(app)

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/', methods=['GET', 'POST'])
def homepage():
    return redirect(url_for('home'))

@app.route('/pythonlogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        # Display producs and price
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM products WHERE available = 1')
        products = cur.fetchall()
        cur.close()
        #print("PRODUCTS HOME:" + str(products))

        return render_template('home.html', username=session['username'], products=products)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    ##id = [0]
    ##username = [1]
    ##password = [2]
    ##email = [3]
    msg =''
    #Check if POST and if username and password is filled in.
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        # hash pwd with md5
        hashPwd = hashlib.sha256(password.encode())
        hash = hashPwd.hexdigest()
        #Check if in DB
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM accounts WHERE username = %s AND password = %s',
                    (username, hash))
        account = cur.fetchone()
        cur.close()
        #If account exists:
        if account:
            session['loggedin'] = True
            session['id'] = account[0] #ID
            session['username'] = account[1] #Username
            #redirect to homepage
            createBasket()
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username or password'
    return render_template('index.html', msg=msg)

@app.route('/pythonlogin/logout')
def logout():
    #remove session data to clear user
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    #redirect to login page
    return redirect(url_for('login'))

@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    msg=''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        #check if account exists in MySQL
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM accounts WHERE username = %s', [username])
        account = cur.fetchone()

        #error handling:
        if account:
            msg = 'Account already exist!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            #Account doesend exist and the form data is valid. insert new account to DB
            # hash pwd with sha256
            hashPwd = hashlib.sha256(password.encode())
            hash = hashPwd.hexdigest()
            cur.execute('INSERT INTO accounts (username, password, email) VALUES (%s,'
                        '%s,%s)', (username, hash, email))
            mysql.connection.commit()

            msg = 'You have successfully registered!'
        cur.close()
    elif request.method == 'POST':
        #empty form
        msg = 'Please fill out the form!'

    #display register-page
    return render_template('register.html', msg=msg)

@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM accounts WHERE memberID = %s', [session['id']])
        #print(session['id'])
        account = cur.fetchone()
        #print(account)
        cur.execute('SELECT transactionID,status FROM transactions WHERE memberID = %s',(session['id'],))
        transactions = cur.fetchall()
        cur.execute('SELECT oldBasketID,productID,quantity,status, reg_date FROM transactionOrders,'
                    'transactions WHERE (transactions.transactionID = transactionOrders.oldBasketID) AND ('
                    'transactions.memberID = %s);', (session['id'],))
        # Show the profile page with account info
        #Show previous transactions
        orders = cur.fetchall()
        #print("orders: ", str(orders))
        cur.close()
        return render_template('profile.html', account=account,transactions=transactions, orders=orders)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
@app.context_processor
def utility():
    def orderFetching(orderID):
        cur = mysql.connection.cursor()
        #cur.execute('SELECT * FROM transactionOrders WHERE oldBasketID = %s', (orderID,))
        cur.execute(
            'SELECT products.productName, products.price, transactionOrders.quantity FROM transactionOrders, products WHERE transactionOrders.productID = products.productID and transactionOrders.oldBasketID=%s',
            (orderID,))
        itemData = list(cur.fetchall())
        itemData = [list(itemD) for itemD in itemData]
        #print(str(itemData))
        for itemD in itemData:
            #print(str(itemD))
            itemD[1] = str(itemD[1]) + " KR"
            itemD[2] = "Bought " + str(itemD[2]) + " Pieces"
        cur.close()
        return itemData
    return dict(orderFetching=orderFetching)

@app.route('/pythonlogin/home/product', methods=['GET', 'POST'])
def product():
    id = request.args.__getitem__('productID')
    print("id = " + str(id))
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM products WHERE productID = %s', [id])
    product = cur.fetchone()
    print("Product: "+ str(product))
    cur.execute('SELECT * FROM comments WHERE productID = %s', [id])
    coms = cur.fetchall()

    cur.execute('SELECT AVG(ratings) FROM rating  WHERE productID = %s', [id])
    rate = cur.fetchone()
    rate = rate[0]
    print("type: " + str(type(rate)))
    if rate is None:
        pass
    else:
        rate = round(rate, 1)


    cur.close()
    print("avg rating: " + str(rate))
#    if request.method == 'POST' and request.form['add_to_chart'] == 'Add to chart':
#        addToBasket(id)
#    else:
#        print("Do not add to chart")
    print("product[4]" + str(product[4]))
    if request.method == 'POST' and 'comment' in request.form:
        comment = request.form['comment']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO comments(productID, username, comments) VALUES (%s,%s,%s)', (id, session['username'], comment))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('home'))

    if request.method == 'POST' and 'rating' in request.form:
        rating = request.form['rating']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO rating(productID, memberID, ratings) VALUES (%s,%s,%s)', (id, session['id'], rating))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('home'))

    return render_template(('product.html'), product=product, coms=coms, rate=rate)





@app.route('/pythonlogin/home/basket', methods=['GET', 'POST'])
def checkout():
    #Display how many items exists in shoppingcart aswell.
    username = session['username']
    id = session['id']
    cur = mysql.connection.cursor()
    cur.execute('SELECT basketID FROM basket WHERE memberID =%s', [id])
    basketID = cur.fetchone()
    cur.execute('SELECT * FROM basketOrders WHERE memberID = %s', [id])
    quantity = cur.fetchall()
    print("QUANTITY: " + str(quantity) + " :!!!!!!!")

    cur.execute('SELECT * FROM products WHERE productID IN (SELECT productID FROM basketOrders WHERE basketID = %s)', basketID)
    checkoutProducts = cur.fetchall()
    print("checkoutProducts: " + str(checkoutProducts))

    cur.execute('SELECT price, quantity FROM basketOrders INNER JOIN products ON basketOrders.productID=products.productID WHERE memberID=%s', (id, ))
    prods = cur.fetchall()
    cur.close()
    summa = 0
    for item in prods:
        summa += item[0]*item[1]
    print("PRODS: " + str(prods))
    print("SUMMA: " + str(summa))
    return render_template('basket.html', username=username, products=checkoutProducts, quantity=quantity, summa=summa)

@app.route('/addToBasket', methods=['GET', 'POST'])
def addToBasket():
    #If item already exists in basket
    #   Increase quantitycount by one
    #else:
    #   add item to basketOrdersID and link it to the users basket
    productID = request.args.__getitem__('productID')
    print("productID = " + str(productID))
    cur = mysql.connection.cursor()
    cur.execute('SELECT basketID FROM basket WHERE memberID = %s', (session['id'],))
    basketID = cur.fetchone()
    #Should return 1 for item exists and should be incremented,
    # or a 0 which means not existing and should thereby be added to the DB.
    cur.execute('SELECT EXISTS(SELECT * FROM basketOrders WHERE productID = %s AND basketID = %s)', (productID,
                                                                                                    basketID))
    state = cur.fetchone()
    print("STATE OF DB: " + str(state[0]))
    if(state[0]):
        print("true")
        cur.execute('UPDATE basketOrders SET quantity = quantity + 1 WHERE memberID = %s AND productID = %s',
                    (session['id'], productID))
    else:
        print("false")
        cur.execute(
            'INSERT INTO basketOrders (basketOrdersID,memberID,productID,basketID, quantity) VALUES (null ,%s,%s,%s,1)',
            (session['id'], productID, basketID,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('checkout'))

def createBasket():
    cur = mysql.connection.cursor()
    cur.execute('INSERT IGNORE INTO `basket` (`basketID`, `memberID`) VALUES (null, %s)', (session['id'],))
    mysql.connection.commit()
    cur.close()

@app.route('/decreaseFromBasket', methods=['GET', 'POST'])
def decreaseFromBasket():
    #If item already exists in basket
    #   Decrease quantitycount by one
    #else:
    #   remove item to basketOrdersID and link it to the users basket
    productID = request.args.__getitem__('productID')
    cur = mysql.connection.cursor()
    cur.execute('SELECT basketID FROM basket WHERE memberID = %s', (session['id'],))
    basketID = cur.fetchone()
    #Should return 1 for item exists and should be incremented,
    # or a 0 which means not existing and should thereby be added to the DB.
    cur.execute('SELECT quantity FROM basketOrders WHERE basketID = %s AND productID = %s', (basketID,productID))
    temp = cur.fetchone()
    quantities = temp[0]
    print("STATE OF DB: " + str(quantities))
    if(quantities > 1):
        print("true")
        cur.execute('UPDATE basketOrders SET quantity = quantity - 1 WHERE memberID = %s AND productID = %s',
                    (session['id'], productID))
    elif(quantities <= 1):
        print("Remove row from basketOrders")
        removeFromBasket(basketID,productID)
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('checkout'))

def removeFromBasket(basketID,productID):
    #simply remove whole row from basketOrders
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM basketOrders WHERE basketID = %s AND productID = %s', (basketID,productID))
    mysql.connection.commit()
    cur.close()
    return

@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    #make transaction
    #transfer basket to transactions.
    memberID = session['id']
    cur = mysql.connection.cursor()
    #if basketOrders = 0
    msg = ""
    cur.execute('SELECT count(*) FROM basketOrders WHERE memberID = %s', (session['id'],))
    status = cur.fetchone()
    print("status: " + str(status))
    if(status[0] != 0):
        cur.execute('START TRANSACTION; SELECT basketID INTO @baskID FROM basket WHERE memberID = %s; INSERT INTO '
                    'transactions(transactionID,memberID)SELECT * FROM basket WHERE basketID = @baskID;INSERT INTO '
                    'transactionOrders SELECT * FROM basketOrders WHERE basketID = @baskID; DELETE FROM basketOrders '
                    'WHERE basketID = @baskID; DELETE FROM basket WHERE basketID = @baskID; commit;',(memberID,))
        temp=cur.fetchall
        print("temp: " + str(temp))
    else:
        msg = "You do not have any products in your basket, please spend your money!"
    cur.close()
    createBasket()
    return render_template('basket.html', msg=msg)
@app.route('/admin', methods=['GET', 'POST'])
def loginAdmin():
    ##id = [0]
    ##username = [1]
    ##password = [2]
    ##email = [3]
    msg =''
    #Check if POST and if username and password is filled in.
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        print("login admin attempt")
        username = request.form['username']
        password = request.form['password']
        #Check if in DB on separate admin account.
        account = admin.loginAdmin(username, password)
        #If account exists:
        if account:
            session['loggedin'] = True
            session['id'] = account[0] #ID
            session['username'] = account[1] #Username
            #redirect to homepage
            return redirect(url_for('adminHome'))
        else:
            msg = 'Incorrect username or password'
    return render_template('admin.html', msg=msg)

@app.route('/admin/home/product', methods=['GET', 'POST'])
def adminHome():

    # Check if admin is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        # Display producs and price
        products=admin.adminHome()
        # print("PRODUCTS HOME:" + str(products))

        return render_template('adminPage.html', username=session['username'], products=products)
    # User is not loggedin redirect to login page
    return redirect(url_for('loginAdmin'))

@app.route('/admin/home/Orders', methods=['GET', 'POST'])
def adminOrders():
    temp = admin.adminOrders()
    lens = 0
    return render_template('adminOrders.html',transactions=temp, lens=lens)

@app.route('/admin/home/AddProduct', methods=['GET', 'POST'])
def adminAddProducts():
    if(request.method == 'POST' and 'productName' in request.form and 'description' in request.form and 'price' in request.form):
        print(request.form)
        productname = request.form['productName']
        description = request.form['description']
        price = request.form['price']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO products(productName, description, price) VALUES (%s,%s,%s)', (productname, description, price))
        mysql.connection.commit()
        cur.close()
    return render_template('adminAddProduct.html')

@app.route('/admin/home/RemoveProduct', methods=['GET', 'POST'])
def adminRemoveProduct():
    #remove row from products
    productID = request.args.__getitem__('productID')
    cur = mysql.connection.cursor()
    cur.execute('UPDATE products SET available = !available WHERE productID = %s',
                (productID,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('adminHome'))


@app.route('/admin/home/ChangeStatus', methods=['GET', 'POST'])
def adminChangeStatus():
    basketID =  request.args.__getitem__('basketID')
    cur = mysql.connection.cursor()
    cur.execute('UPDATE transactions SET status = "cancel" WHERE transactionID = %s',
                (basketID,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('adminOrders'))




@app.route('/admin/home/sale', methods=['GET', 'POST'])
def adminToggleSale():
    productID = request.args.__getitem__('productID')
    cur = mysql.connection.cursor()
    cur.execute('UPDATE products SET saleBool = !saleBool WHERE productID = %s', (productID,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('adminHome'))


@app.route('/admin/home/updatesale', methods=['GET','POST'])
def updateSalePrice():
    productID = request.args.__getitem__('productID')
    if request.method == 'POST' and 'salePrice' in request.form:
        salePrice = request.form['salePrice']
        cur = mysql.connection.cursor()
        cur.execute('UPDATE products SET salesPrice = %s WHERE productID = %s', (salePrice, productID))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('adminHome'))



