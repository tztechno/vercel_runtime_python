# flaskを用いて、計算式もfrontから入力してbackでの計算に用いる

## はじめに
これまでfrontで入力した値をAjax通信を利用してbackで計算させるアプリを作ってきましたが、アプリ使用時、backに記載された計算式は固定で変えられないという宿命がありました。
今回flaskを用いて、計算式もfrontから入力してbackでの計算に用いることに挑戦しました。
入力する計算式のコードはPython限定です。AtCoderの提出コードの形式がそのまま使えるようにしています。
したがって入力値を受け取るコード、結果はprintで出力が必要です。


## templates/index.html
```
<!DOCTYPE html>
<html>

<head>
    <title>Python Run Time Calculator</title>
    <style>
        .container {
            display: flex;
        }

        .left-panel {
            flex: 1;
            padding-right: 20px;
        }

        .right-panel {
            flex: 1;
            border-left: 1px solid #ccc;
            padding-left: 20px;
            max-height: 80vh;
            overflow-y: auto;
        }
    </style>
</head>

<body>
    <h1>Python Run Time Calculator</h1>
    <div class="container">
        <div class="left-panel">
            <p>Define your function:</p>
            <textarea id="functionCode" rows="10" cols="50">
def fibonacci(n):
  if n <= 1: 
    return n 
  else: 
    return fibonacci(n-1) + fibonacci(n-2) 

n=int(input()) 
print(fibonacci(n))
            </textarea>
            <p>Enter your input (multiple lines allowed):</p>
            <textarea id="inputData" rows="5" cols="50" placeholder="Enter input data">10</textarea>
            <button onclick="sendRequest()">Calculate</button><br><br>
            <div id="currentResult"></div>
            <div id="error" style="color: red;"></div>
        </div>
        <div class="right-panel">
            <h2>Calculation History</h2>
            <div id="history">
                {% for item in history|reverse %}
                <div class="history-item">
                    <h3>Calculation #{{ loop.revindex }}</h3>
                    <h4>Input Data:</h4>
                    <pre>{{ item.input_data }}</pre>
                    <h4>Function Code:</h4>
                    <pre>{{ item.function_code }}</pre>
                    <h4>Result:</h4>
                    <pre>{{ item.result }}</pre>
                    <h4>Process Time:</h4>
                    <pre>{{ item.process_time }} ms</pre>
                    <hr>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

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
                        const current = data.current_result;
                        document.getElementById('currentResult').innerHTML = `
                        <h3>Current Result:</h3>
                        <pre>Input Data: ${current.input_data}</pre>
                        <pre>Result: ${current.result}</pre>
                        <pre>Process Time: ${current.process_time} ms</pre>
                    `;
                        document.getElementById('error').innerText = '';

                        // Update history
                        const historyHtml = data.history.reverse().map((item, index) => `
                        <div class="history-item">
                            <h3>Calculation #${data.history.length - index}</h3>
                            <h4>Input Data:</h4>
                            <pre>${item.input_data}</pre>
                            <h4>Function Code:</h4>
                            <pre>${item.function_code}</pre>
                            <h4>Result:</h4>
                            <pre>${item.result}</pre>
                            <h4>Process Time:</h4>
                            <pre>${item.process_time} ms</pre>
                            <hr>
                        </div>
                    `).join('');
                        document.getElementById('history').innerHTML = historyHtml;
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
from flask import Flask, render_template, request, jsonify, session
import time
import traceback
import sys
import io
import signal

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("処理が9秒を超えました")

@app.route('/')
def index():
    if 'history' not in session:
        session['history'] = []
    return render_template('index.html', history=session['history'])

@app.route('/calculate', methods=['POST'])
def calculate():
    start_time = time.time()
    data = request.json
    input_data = data['inputData']
    function_code = data['functionCode']
    
    try:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(9)
        
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        stdin = io.StringIO(input_data)
        global_context = {'sys': sys, 'input': stdin.readline}
        
        exec(function_code, global_context)
        
        result = captured_output.getvalue().strip()
        
        sys.stdout = sys.__stdout__
        
        signal.alarm(0)
        
        end_time = time.time()
        process_time = (end_time - start_time) * 1000  # in milliseconds
        
    except TimeoutException as e:
        sys.stdout = sys.__stdout__
        result = '処理が9秒を超えたため強制終了しました'
        process_time = 9000
        
    except Exception as e:
        sys.stdout = sys.__stdout__
        result = str(e)
        process_time = (time.time() - start_time) * 1000
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 400

    # 新しい計算結果を履歴に追加
    if 'history' not in session:
        session['history'] = []
    session['history'].append({
        'input_data': input_data,
        'function_code': function_code,
        'result': result,
        'process_time': process_time
    })
    session.modified = True

    return jsonify({
        'current_result': {
            'input_data': input_data,
            'function_code': function_code,
            'result': result,
            'process_time': process_time
        },
        'history': session['history']
    })

if __name__ == '__main__':
    app.run(debug=True)
```


## 終わりに
完成品はVercelにアップしました。
https://vercel-runtime-python.vercel.app/
フロントの右側に計算結果のHistoryがスクロール表示させる機能が付いています。
Vercelの実行制限時間範囲内で終了させるため、処理が9秒を超えたた場合は強制終了となります。


