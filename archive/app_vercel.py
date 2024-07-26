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
