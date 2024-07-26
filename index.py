from flask import Flask, render_template, request, jsonify, session
import time
import traceback
import sys
import io
import signal

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # セッションのために必要。実際の使用時は安全な値に変更してください。

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("処理が9秒を超えました")

@app.route('/')
def index():
    return render_template('index.html', session=session)  # セッション情報をテンプレートに渡す

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
        
        end_time = time.time()
        process_time = (end_time - start_time) * 1000  # in milliseconds
        
        # セッションに情報を保存
        session['input_data'] = input_data
        session['function_code'] = function_code
        session['result'] = result
        session['process_time'] = process_time
        
    except TimeoutException as e:
        # Reset stdout in case of a timeout
        sys.stdout = sys.__stdout__
        session['result'] = '処理が9秒を超えたため強制終了しました'
        session['process_time'] = 9000
        return jsonify(session), 200
        
    except Exception as e:
        # Reset stdout in case of an exception
        sys.stdout = sys.__stdout__
        session['result'] = str(e)
        session['process_time'] = (time.time() - start_time) * 1000
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 400

    return jsonify(session)

if __name__ == '__main__':
    app.run(debug=True)  # デバッグモードを有効にする。本番環境では無効にしてください。