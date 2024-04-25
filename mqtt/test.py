from flask import Flask, render_template, jsonify, request
from datetime import datetime
import paho.mqtt.client as mqtt
import sqlite3 
import pymysql as ps 

app = Flask(__name__, template_folder='/home/user/AIoT/python/mqtt')

mqtt_messages = []

# MQTT 브로커 연결
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("cj/topic") 

# MQTT 메시지 수신
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    global mqtt_messages
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = msg.payload.decode()
    mqtt_messages.append({'timestamp': timestamp, 'message': message})
    # SQLite에 메시지 저장
    insert_to_sqlite(timestamp, message)
    insert_to_maria(timestamp, message)  # 수정: insert_to_maria 함수를 호출하도록 변경

# MQTT 클라이언트
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)

# SQLite3 데이터베이스 연결
def connect_to_sqlite3():
    conn = sqlite3.connect('/home/user/mqtttest.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS test (
                    time TEXT,
                    data TEXT,
                    PRIMARY KEY (time)  -- 수정: time 컬럼을 primary key로 설정하여 중복 삽입 방지
                 )''')
    conn.commit()
    conn.close()

# MariaDB 연결 함수
def maria_connection():
    return ps.connect(
        host='localhost',
        user='root',
        password='1234',
        database='flasktest',
        charset='utf8mb4',
        cursorclass=ps.cursors.DictCursor
    )

# MariaDB 연결
def connect_to_mariadb():
    conn = maria_connection()
    with conn.cursor() as cursor:
        cursor.execute('''CREATE TABLE IF NOT EXISTS test (
                            time TEXT,
                            data TEXT
                         )''')
    conn.commit()
    conn.close()

# 메시지를 SQLite 데이터베이스에 삽입하는 함수
def insert_to_sqlite(timestamp, message):
    conn = sqlite3.connect('/home/user/test.db')
    c = conn.cursor()
    c.execute("INSERT INTO test (time, data) VALUES (?, ?)", (timestamp, message))
    conn.commit()
    conn.close()

# 메시지를 MariaDB 데이터베이스에 삽입하는 함수
def insert_to_maria(timestamp, message):
    conn = maria_connection()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO test (time, data) VALUES (%s, %s)", (timestamp, message))
        conn.commit()
    conn.close()

# MariaDB에서 메시지 검색
def search_in_mariadb(keyword):
    conn = maria_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM test WHERE data LIKE %s", ('%' + keyword + '%',))
        results = cursor.fetchall()
    conn.close()
    return results

# Flask 루트
@app.route('/')
def index():
    return render_template('index.html')

# AJAX 엔드포인트
@app.route('/get_mqtt_messages')
def get_mqtt_messages():
    global mqtt_messages
    return jsonify({'messages': mqtt_messages})

@app.route('/search_messages')
def search_messages():
    keyword = request.args.get('keyword', '')
    results = search_in_mariadb(keyword)
    return jsonify({'results': results})

if __name__ == '__main__':
    connect_to_sqlite3()
    connect_to_mariadb()
    client.loop_start() 
    app.run(debug=True, host='0.0.0.0')

