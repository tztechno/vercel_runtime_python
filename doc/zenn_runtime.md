# フロントから入力した値と計算式を用いてバックエンドで計算させるアプリ

## はじめに
フロントから入力した値と計算式を用いてバックエンドで計算させるflaskアプリを作成しました。

## 機能
フロントから値と計算式を入力して、ボタンを押すと計算結果、計算時間が表示される(Current Result)。
入力する計算式はPython限定で、AtCoder問題の入力値、提出コードの形式がそのまま使える。
繰り返し実行すると、結果履歴がスクロール表示されます(Calculation History)。
処理が9秒を超えたた場合は強制終了となります(Vercelの実行制限時間範囲内で終了させるため)。

## 入出力サンプル
サンプル計算式
```
def fibonacci(n):
  if n <= 1: 
    return n 
  else: 
    return fibonacci(n-1) + fibonacci(n-2) 

n=int(input()) 
print(fibonacci(n))
```
サンプル入力値
```
10
```
サンプル結果
```
Current Result:
Input Data: 10
Result: 55
Process Time: 0.3268718719482422 ms
```

```
Calculation History
Calculation #1

Input Data:
10

Function Code:
def fibonacci(n):
  if n <= 1: 
    return n 
  else: 
    return fibonacci(n-1) + fibonacci(n-2) 

n=int(input()) 
print(fibonacci(n))
            
Result:
55

Process Time:
0.3268718719482422 ms

```
## templates/index.html

Flaskを使ってPythonコードの実行時間を計測し、結果を表示するウェブアプリケーションのフロントです。

### 機能概要

#### HTMLとCSS

- **レイアウト**: Flexboxで左右のパネルに分かれています。

#### 左パネル

- **関数定義**:
  - Pythonの関数コードを入力するためのテキストエリア（初期設定はフィボナッチ関数）。

- **入力データ**:
  - 関数に渡す入力値を入力するテキストエリア。

- **計算ボタン**:
  - 計算を行うためのボタン。

- **結果表示**:
  - 現在の計算結果やエラーを表示する領域。

#### 右パネル

- **計算履歴**:
  - 過去の計算結果を表示。入力データ、関数コード、結果、処理時間が含まれる。
  - テンプレート構文でサーバーから動的に履歴を表示。

#### JavaScript機能

- **`sendRequest()`**:
  - Fetch APIで`/calculate`にPOSTリクエストを送り、計算を実行。
  - 結果やエラーを更新し、履歴を表示。

ユーザーはPython関数を定義し、データを入力して計算を実行し、履歴として結果を確認できます。
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

Flaskを使ってPythonコードの実行時間を計測し、結果を表示するウェブアプリケーションのバックエンドです。

### 機能概要

#### 初期設定

- **Flaskアプリケーションの初期化**:
  - `app = Flask(__name__)`
  - セッションのためのシークレットキーを設定。

#### タイムアウト処理

- **`TimeoutException`クラス**:
  - 9秒を超えた処理を中断するための例外。

- **`timeout_handler`関数**:
  - タイムアウトが発生した場合に`TimeoutException`を発生させる。

#### ルーティング

- **`/`エンドポイント**:
  - 初期ページを表示し、セッションに履歴がなければ新規作成。

- **`/calculate`エンドポイント**:
  - POSTリクエストで受け取ったPythonコードを実行。

#### 計算処理

1. **タイムアウト設定**:
   - `signal.signal`と`signal.alarm`を使って9秒のタイムアウトを設定。

2. **コード実行**:
   - `io.StringIO`で標準出力をキャプチャし、`exec`を使ってコードを実行。

3. **結果取得**:
   - キャプチャした出力を結果として取得。

4. **例外処理**:
   - タイムアウトや他の例外をキャッチし、適切に処理。

5. **履歴更新**:
   - 新しい計算結果をセッションの履歴に追加。

#### JSONレスポンス

- **現在の結果と履歴**をJSON形式で返す。

#### アプリケーション実行

- `app.run(debug=True)`でデバッグモードでアプリを実行。

このコードは、ユーザーが送信したPythonコードをサーバーで実行し、その結果と処理時間をフロントエンドに返します。また、セッションを使用して計算履歴を管理します。

```
from flask import Flask, render_template, request, jsonify, session
import time
import traceback
import sys
import io
import os
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
Vercelにアップしました。
https://vercel-runtime-python.vercel.app/



