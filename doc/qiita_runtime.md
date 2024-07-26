
Pythonのコードと入力データをサーバーに送信し、結果や実行時間を表示する簡単なWebインターフェースを設定しています。
Pythonコードは、AtCoderのPython提出コードの形式を想定しており、結果出力はprintで行います。

templates/index.html
HTMLの構造
ユーザーがPythonのコードと入力データを入力できるテキストエリアがあります。
ボタンをクリックすると、このデータがサーバーに送信されます。
計算結果および実行時間がページに表示されます。 

JavaScriptの機能
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

index.py
Flaskアプリケーションのコードは、Pythonのコードを実行し、その結果を返すAPIエンドポイントを設定しています。

主な機能
index エンドポイント
/ にアクセスすると index.html を返します。

@app.route('/')
def index():
    return render_template('index.html')

calculate エンドポイント
/calculate に対してPOSTリクエストが送信されると、以下の処理が行われます。
現在の時間を取得し、処理開始時間を記録します。
リクエストからinputData（入力データ）とfunctionCode（実行するPythonコード）を取得します。

@app.route('/calculate', methods=['POST'])
def calculate():
    start_time = time.time()
    data = request.json
    input_data = data['inputData']
    function_code = data['functionCode']
    
タイムアウトのために9秒のアラームを設定します。
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(9)
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



```

```



