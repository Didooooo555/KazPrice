from flask import Flask, render_template, jsonify, request, url_for, redirect, session
import mysql.connector
import requests
import bcrypt

app = Flask(__name__)
app.secret_key = "rieirvoirbvoejnkjwrbohbkjewpjvrbtl"


@app.route('/')
def index():
    return render_template('glav.html')


@app.route('/regis', methods=['GET', 'POST'])
def regis():
    message = ""  

    if request.method == 'POST':
        name = request.form['name']
        gmail = request.form['gmail']
        password = request.form['password']

        con = mysql.connector.connect(
            host='localhost',
            user='root',
            password='didar09k',
            database='shop'
        )
        cursor = con.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS user (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            gmail VARCHAR(255) UNIQUE,
            password VARBINARY(255)
        )''')

        
        cursor.execute("SELECT gmail FROM user WHERE gmail=%s", (gmail,))
        if cursor.fetchone():
            message = "Этот email уже зарегистрирован!"
            cursor.close()
            con.close()
            return render_template('regis.html', message=message)

       
        hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor.execute("INSERT INTO user (name, gmail, password) VALUES (%s, %s, %s)",
                       (name, gmail, hashed_pass))
        con.commit()
        cursor.close()
        con.close()

        message = "Регистрация прошла успешно!"
        return render_template('voi.html', message=message)

    return render_template('regis.html', message=message)


@app.route('/voi', methods=['GET', 'POST'])
def voi():
    message = ""  

    if request.method == 'POST':
        gmail = request.form['gmail']
        password = request.form['password']

        con = mysql.connector.connect(
            host='localhost',
            user='root',
            password='didar09k',
            database='shop'
        )
        cursor = con.cursor()
        cursor.execute("SELECT id, name, password FROM user WHERE gmail=%s", (gmail,))
        user = cursor.fetchone()
        cursor.close()
        con.close()

        if user:
            user_id, name, hashed_password = user
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                session['user_id'] = user_id
                session['name'] = name
                return redirect(url_for('osnov'))
            else:
                message = "Неверный пароль!"
        else:
            message = "Пользователь с таким email не найден!"

    return render_template('voi.html', message=message)


@app.route('/osnov')
def osnov():
    if 'user_id' not in session:
        return redirect(url_for('voi'))
    return render_template('osnov.html', name=session.get('name'))


@app.route('/zak')
def zak():
    if 'user_id' not in session:
        return redirect(url_for('voi'))
    return render_template('zak.html')


@app.route('/pot')
def pot():
    if 'user_id' not in session:
        return redirect(url_for('voi'))
    return render_template('pot.html')


@app.route('/api/rates')
def api_rates():
    try:
        # Попробуем первый источник
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            rates = data.get("rates", {})
            
            usd_to_kzt = rates.get("KZT")
            usd_to_rub = rates.get("RUB") 
            usd_to_cny = rates.get("CNY")
            
            if all([usd_to_kzt, usd_to_rub, usd_to_cny]):
                result = {
                    "USD": round(usd_to_kzt, 2),
                    "RUB": round(usd_to_kzt / usd_to_rub, 2),
                    "CNY": round(usd_to_kzt / usd_to_cny, 2)
                }
                return jsonify(result)
        
        # Если первый источник не сработал, попробуем альтернативный
        url = "https://api.frankfurter.app/latest?from=USD"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            rates = data.get("rates", {})
            
            # Используем фиксированные курсы для KZT если API не возвращает
            usd_to_kzt = rates.get("KZT", 450.0)  # примерный курс
            usd_to_rub = rates.get("RUB", 90.0)
            usd_to_cny = rates.get("CNY", 7.2)
            
            result = {
                "USD": round(usd_to_kzt, 2),
                "RUB": round(usd_to_kzt / usd_to_rub, 2),
                "CNY": round(usd_to_kzt / usd_to_cny, 2)
            }
            return jsonify(result)
        
        # Если оба API не работают, вернем тестовые данные
        result = {
            "USD": 450.0,
            "RUB": 5.0,
            "CNY": 62.5
        }
        return jsonify(result)

    except Exception as e:
        # В случае ошибки вернем тестовые данные
        result = {
            "USD": 450.0,
            "RUB": 5.0, 
            "CNY": 62.5
        }
        return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)