from flask import Flask, render_template, jsonify, request
from datetime import datetime

app = Flask(__name__, template_folder='/home/user/AIoT/python/tcpip')

received_data = []

# POST 요청을 받아서 데이터를 처리하는 엔드포인트
@app.route('/receive_data', methods=['POST'])
def receive_data():
    data = request.json  # 전송된 JSON 데이터를 받아옴
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 현재 시간의 타임스탬프 생성
    data_with_timestamp = {'timestamp': timestamp, 'data': data}  # 타임스탬프와 데이터를 합침
    received_data.append(data_with_timestamp)  # 데이터를 리스트에 추가
    return jsonify({'success': True}), 200  # 성공 응답


# 웹 페이지에 리스트에 있는 데이터를 표시하는 엔드포인트
@app.route('/')
def index():
    return render_template('index.html', data=received_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

