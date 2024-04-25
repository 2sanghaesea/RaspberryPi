from flask import Flask, render_template, jsonify, request
from datetime import datetime
import pymysql as mariadb

app = Flask(__name__, template_folder='/home/user/AIoT/python/tcpip/http')

# 마리아DB 연결 정보
db_info = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'flasktest'
}

received_data = []

# 데이터베이스 연결 함수
def connect_to_database():
    try:
        conn = mariadb.connect(**db_info)
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return None

# POST 요청을 받아서 데이터를 처리하는 엔드포인트
@app.route('/receive_data', methods=['POST'])
def receive_data():
    data = request.json  # 전송된 JSON 데이터를 받아옴
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 현재 시간의 타임스탬프 생성
    data_with_timestamp = {'data': data, 'timestamp': timestamp}  # 타임스탬프와 데이터를 합침
    received_data.append(data_with_timestamp)  # 데이터를 리스트에 추가

    # 마리아DB에 데이터 추가
    conn = connect_to_database()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO lora (id, temp, humd, time) VALUES (?, ?, ?, ?)",
                        (data['id'], str(data['temperature']), str(data['humidity']), timestamp))
            conn.commit()
        except mariadb.Error as e:
            print(f"Error inserting data into MariaDB: {e}")
            conn.rollback()
        conn.close()
        
    js_command = f"addDataToCharts( {data['temperature']}, {data['humidity']}, '{timestamp}');"
    return jsonify({'success': True}), 200  # 성공 응답

# 웹 페이지에 리스트에 있는 데이터를 표시하는 엔드포인트
@app.route('/')
def index():
    return render_template('index.html', data=received_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

