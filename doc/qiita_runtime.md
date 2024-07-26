

## はじめに
Pythonのコードと入力データをサーバーに送信し、計算結果と実行時間を表示する簡単なWebインターフェースを設定しています。
Pythonコードは、AtCoderのPython提出コードの形式を想定しており、結果出力はprintで行います。

## templates/index.html
### HTMLの構造
ユーザーがPythonのコードと入力データを入力できるテキストエリアがあります。
ボタンをクリックすると、このデータがサーバーに送信されます。
計算結果および実行時間がページに表示されます。 

### JavaScriptの機能
sendRequest関数は、テキストエリアから入力データとPythonのコードを取得します。
```
function sendRequest() {
    const inputData = document.getElementById('inputData').value;
    const functionCode = document.getElementById('functionCode').value;
```
fetch APIを使用して、POSTリクエストでこのデータをサーバーに送信します。
```
fetch('/calculate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ inputData, functionCode })
})
```
サーバーからのレスポンスを受け取った後、HTMLを更新して入力データ、結果、実行時間、を表示します。
```
document.getElementById('inputDisplay').innerText = `Input:\n${data.inputData}`;
document.getElementById('result').innerText = `Result:\n${data.result}`;
document.getElementById('time').innerText = `Time: ${(data.process_time / 1000).toFixed(3)} sec`;
```
templates/index.html

## index.py
Flaskアプリケーションのコードは、Pythonのコードを実行し、その結果を返すAPIエンドポイントを設定しています。

### 主な機能
index エンドポイント
/ にアクセスすると index.html を返します。
```
@app.route('/')
def index():
    return render_template('index.html')
```
calculate エンドポイント
/calculate に対してPOSTリクエストが送信されると、以下の処理が行われます。
現在の時間を取得し、処理開始時間を記録します。
リクエストからinputData（入力データ）とfunctionCode（実行するPythonコード）を取得します。
```
@app.route('/calculate', methods=['POST'])
def calculate():
    start_time = time.time()
    data = request.json
    input_data = data['inputData']
    function_code = data['functionCode']
```    
タイムアウトのために9秒のアラームを設定します。
```
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(9)
```
sys.stdoutをリダイレクトして、printの出力をキャプチャします。
```
    captured_output = io.StringIO()
    sys.stdout = captured_output
```
io.StringIOを用いてinput_dataをシミュレートした標準入力を作成します。
```
    stdin = io.StringIO(input_data)
    global_context = {'sys': sys, 'input': stdin.readline}
```
exec関数を使って、受け取ったコードを実行します。
```
    exec(function_code, global_context)
```
結果をキャプチャし、sys.stdoutを元に戻します。
```
    result = captured_output.getvalue().strip()
    sys.stdout = sys.__stdout__
```
処理時間を計算し、JSON形式でレスポンスを返します。
```
    end_time = time.time()
    process_time = (end_time - start_time) * 1000  # in milliseconds
    return jsonify({'inputData': input_data, 'result': result, 'process_time': process_time})
```

## templates/index.html
```
<!DOCTYPE html>
<html>

<head>
    <title>Python Run Time Calculator</title>
</head>

<body>
    <h1>Python Run Time Calculator</h1>
    <p>Define your function:</p>
    <textarea id="functionCode" rows="10" cols="50">
n = int(input())
print(n*n)
    </textarea>
    <p>Enter your input (multiple lines allowed):</p>
    <textarea id="inputData" rows="5" cols="50" placeholder="Enter input data"></textarea>
    <button onclick="sendRequest()">Calculate</button><br><br>
    <div id="inputDisplay"></div>
    <div id="result"></div>
    <div id="time"></div>
    <div id="error" style="color: red;"></div>

    <script>
        function sendRequest() {
            const inputData = document.getElementById('inputData').value;
            const functionCode = document.getElementById('functionCode').value;
            fetch('/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ inputData, functionCode })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('error').innerText = `Error: ${data.error}`;
                    } else {
                        document.getElementById('inputDisplay').innerText = `Input:\n${data.inputData}`;
                        document.getElementById('result').innerText = `Result:\n${data.result}`;
                        document.getElementById('time').innerText = `Time: ${(data.process_time / 1000).toFixed(3)} sec`;
                        document.getElementById('error').innerText = '';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('error').innerText = `Error: ${error}`;
                });
        }
    </script>
</body>

</html>
```

## index.py
```
from flask import Flask, render_template, request, jsonify
import time
import traceback
import sys
import io
import signal

app = Flask(__name__)

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("処理が9秒を超えました")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    start_time = time.time()
    data = request.json
    input_data = data['inputData']
    function_code = data['functionCode']
    
    try:
        # 9秒のタイマーを設定
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(9)
        
        # Redirect stdout to capture print output
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # Simulate stdin
        stdin = io.StringIO(input_data)
        global_context = {'sys': sys, 'input': stdin.readline}
        
        # Execute the function code in the global context
        exec(function_code, global_context)
        
        # Get the captured output
        result = captured_output.getvalue().strip()
        
        # Reset stdout
        sys.stdout = sys.__stdout__
        
        # タイマーをリセット
        signal.alarm(0)

    except TimeoutException as e:
        # Reset stdout in case of a timeout
        sys.stdout = sys.__stdout__
        return jsonify({'error': str(e), 'result': '処理が9秒を超えたため強制終了しました', 'process_time': 9000}), 200

    except Exception as e:
        # Reset stdout in case of an exception
        sys.stdout = sys.__stdout__
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 400

    end_time = time.time()
    process_time = (end_time - start_time) * 1000  # in milliseconds
    return jsonify({'inputData': input_data, 'result': result, 'process_time': process_time})

if __name__ == '__main__':
    app.run()
```

```

```



