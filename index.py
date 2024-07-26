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