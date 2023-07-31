import psycopg2
from flask import Flask, jsonify, request
import  database_connection

cursor = database_connection.connection.cursor()

app = Flask(__name__)

@app.post('/customers')
def addCustomer():
    cursor.execute("insert into customers values(%s, %s, %s, %s)",
                   (request.json['cedula'],
                    request.json['name'],
                    request.json['whatsapp'],
                    request.json['email']))

    database_connection.connection.commit()
    return jsonify({'message' : 'cliente agregado correctamente'})

@app.put('/customers/<string:customerCedula>')
def modifyCustomer(customerCedula):
    cursor.execute('update customers set name = %s, whatsapp = %s, email = %s where cedula = %s',
                   (request.json['name'],
                    request.json['whatsapp'],
                    request.json['email'],
                    customerCedula.lower()))

    database_connection.connection.commit()
    return jsonify({'message': 'cliente modificado correctamente'})

@app.get('/customers')
def getCustomers():
    cursor.execute("SELECT row_to_json(row) FROM (SELECT * FROM customers) as row")
    customers = cursor.fetchall()
    return jsonify({"message" : "Customers"}, customers)

@app.post('/orders')
def addOrder():

    quantity = request.json['quantity']
    payment_method = request.json['payment_method'].lower()
    remarks = request.json['remarks'].lower()
    city = request.json['city'].lower()
    municipality = request.json['municipality'].lower()
    cedula = request.json['cedula']

    if not(payment_method in ['efectivo', 'reserve', 'pago movil']):
        return jsonify({"message" : "El metodo de pago ingresado no se encuentra disponible "
                                    "(reserve, pago movil y efectivo)"})

    delivery_amount = 0 if municipality == "maneiro" else 2

    cursor.execute("insert into orders (quantity, payment_method, remarks, city, municipality,"
                   "cedula, total_amount, status, delivery_amount, datetime) "
                   "values(%s, %s, %s, %s, %s, %s, %s, 'pendiente', %s, current_timestamp)",
                   (quantity,
                    payment_method,
                    remarks,
                    city,
                    municipality,
                    cedula,
                    (quantity * 5) + delivery_amount,
                    delivery_amount))

    database_connection.connection.commit()
    cursor.execute("select row_to_json(row) from (select * from orders order by order_number desc limit 1)as row")
    new_order = cursor.fetchone()
    return jsonify({'message': 'Orden agregada correctamente', "order": new_order})

@app.patch('/orders/<string:orderNumber>/status')
def updateStatus(orderNumber):
    newStatus = request.json['status'].lower()

    if not (newStatus in ("en progreso", "despachado", "completado")):
        return jsonify({"message" : "El status ingresado no se encuentra entre las opciones pre-establecidas"})

    cursor.execute("update orders set status = %s where order_number = %s", (newStatus, orderNumber))
    database_connection.connection.commit()
    return jsonify({"message" : "Status modificado correctamente"})

@app.post('/orders/<string:orderNumber>/payment-screenshot')
def addScreenshot(orderNumber):
    screenshotFile = request.files['screenshot']
    screenshot = screenshotFile.read()
    cursor.execute("update orders set payment_screenshot = %s where order_number = %s", (psycopg2.Binary(screenshot), orderNumber))
    database_connection.connection.commit()
    return jsonify({"message" : "Screenshot agregada correctamente"})

@app.get('/orders')
def getOrders():
    date = request.args.get('date')
    status = request.args.get('status')
    cedula = request.args.get('cedula')

    orders = executeGetOrderQuery(date, status, cedula)
    return jsonify({"message" : "orders"}, orders)

def executeGetOrderQuery(date, status, cedula):

    if not(date == None) and status == None and cedula == None:
        cursor.execute("select row_to_json(row) from (select order_number, quantity, payment_method, "
                       "remarks, city, municipality, cedula, total_amount,substring(payment_screenshot,1,10) as paymet_screenshot,"
                       "status, delivery_amount, datetime from orders where date(datetime) = %s ) as row", (date,))
        return cursor.fetchall()

    elif not(date == None) and not(status == None) and cedula == None:
        cursor.execute("select row_to_json(row) from (select order_number, quantity, payment_method, "
                       "remarks, city, municipality, cedula, total_amount,substring(payment_screenshot,1,10) as paymet_screenshot,"
                       "status, delivery_amount, datetime from orders where date(datetime) = %s "
                       "and status = %s) as row", (date, status))
        return cursor.fetchall()

    elif not(date == None) and status == None and not(cedula == None):
        cursor.execute("select row_to_json(row) from (select order_number, quantity, payment_method, "
                       "remarks, city, municipality, cedula, total_amount,substring(payment_screenshot,1,10) as paymet_screenshot,"
                       "status, delivery_amount, datetime from orders where date(datetime) = %s "
                       "and cedula = %s) as row", (date, cedula))
        return cursor.fetchall()

    elif not(date == None) and not(status == None) and not(cedula == None):
        cursor.execute("select row_to_json(row) from (select order_number, quantity, payment_method, "
                       "remarks, city, municipality, cedula, total_amount,substring(payment_screenshot,1,10) as paymet_screenshot,"
                       "status, delivery_amount, datetime from orders where date(datetime) = %s "
                       "and status = %s and cedula = %s) as row", (date, status, cedula))
        return cursor.fetchall()

    elif date == None and not(status == None) and cedula == None:
        cursor.execute("select row_to_json(row) from (select order_number, quantity, payment_method, "
                       "remarks, city, municipality, cedula, total_amount,substring(payment_screenshot,1,10) as paymet_screenshot,"
                       "status, delivery_amount, datetime from orders where status = %s) as row", (status,))
        return cursor.fetchall()

    elif date == None and status == None and not(cedula == None):
        cursor.execute("select row_to_json(row) from (select order_number, quantity, payment_method, "
                       "remarks, city, municipality, cedula, total_amount,substring(payment_screenshot,1,10) as paymet_screenshot,"
                       "status, delivery_amount, datetime from orders where cedula = %s) as row", (cedula,))
        return cursor.fetchall()

    elif date == None and not(status == None) and not(cedula == None):
        cursor.execute("select row_to_json(row) from (select order_number, quantity, payment_method, "
                       "remarks, city, municipality, cedula, total_amount,substring(payment_screenshot,1,10) as paymet_screenshot,"
                       "status, delivery_amount, datetime from orders where"
                       "status = %s and cedula = %s) as row", (status, cedula))
        return cursor.fetchall()

    else:
        cursor.execute("select row_to_json(row) from (select order_number, quantity, payment_method, "
                       "remarks, city, municipality, cedula, total_amount,substring(payment_screenshot,1,10) as paymet_screenshot,"
                       "status, delivery_amount, datetime from orders) as row")
        return cursor.fetchall()


if __name__ == "__main__":
    app.run(debug = True, port = 4000)
