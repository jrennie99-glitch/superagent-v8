"""
Simple Template-Based HTML Generator
Works without AI APIs - generates apps from templates
"""

def generate_app_from_template(instruction: str, build_type: str = "full") -> str:
    """
    Generate a simple HTML app based on keywords in the instruction
    This works WITHOUT needing AI APIs
    """
    instruction_lower = instruction.lower()
    
    # Detect app type from instruction
    if any(word in instruction_lower for word in ["calculator", "calc", "math"]):
        return generate_calculator(build_type)
    elif any(word in instruction_lower for word in ["todo", "task", "list"]):
        return generate_todo_app(build_type)
    elif any(word in instruction_lower for word in ["hello", "world", "simple", "basic"]):
        return generate_hello_world(build_type)
    elif any(word in instruction_lower for word in ["counter", "count", "click"]):
        return generate_counter(build_type)
    elif any(word in instruction_lower for word in ["timer", "stopwatch", "clock"]):
        return generate_timer(build_type)
    else:
        # Default: create a generic app
        return generate_generic_app(instruction, build_type)


def generate_calculator(build_type: str) -> str:
    """Generate a calculator app"""
    if build_type == "design":
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .calculator {
            background: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .display {
            background: #f0f0f0;
            padding: 20px;
            border-radius: 10px;
            text-align: right;
            font-size: 32px;
            margin-bottom: 20px;
            min-height: 60px;
        }
        .buttons {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
        }
        button {
            padding: 20px;
            font-size: 20px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            background: #f0f0f0;
            transition: all 0.2s;
        }
        button:hover { background: #e0e0e0; transform: scale(1.05); }
        button:active { transform: scale(0.95); }
        .operator { background: #667eea; color: white; }
        .operator:hover { background: #5568d3; }
        .equals { background: #764ba2; color: white; grid-column: span 2; }
        .equals:hover { background: #653a8a; }
    </style>
</head>
<body>
    <div class="calculator">
        <div class="display">0</div>
        <div class="buttons">
            <button>7</button>
            <button>8</button>
            <button>9</button>
            <button class="operator">÷</button>
            <button>4</button>
            <button>5</button>
            <button>6</button>
            <button class="operator">×</button>
            <button>1</button>
            <button>2</button>
            <button>3</button>
            <button class="operator">−</button>
            <button>0</button>
            <button>.</button>
            <button class="operator">+</button>
            <button class="operator">C</button>
            <button class="equals">=</button>
        </div>
    </div>
</body>
</html>"""
    
    # Full functional calculator
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .calculator {
            background: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .display {
            background: #f0f0f0;
            padding: 20px;
            border-radius: 10px;
            text-align: right;
            font-size: 32px;
            margin-bottom: 20px;
            min-height: 60px;
            word-wrap: break-word;
        }
        .buttons {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
        }
        button {
            padding: 20px;
            font-size: 20px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            background: #f0f0f0;
            transition: all 0.2s;
        }
        button:hover { background: #e0e0e0; transform: scale(1.05); }
        button:active { transform: scale(0.95); }
        .operator { background: #667eea; color: white; }
        .operator:hover { background: #5568d3; }
        .equals { background: #764ba2; color: white; grid-column: span 2; }
        .equals:hover { background: #653a8a; }
    </style>
</head>
<body>
    <div class="calculator">
        <div class="display" id="display">0</div>
        <div class="buttons">
            <button onclick="appendNumber('7')">7</button>
            <button onclick="appendNumber('8')">8</button>
            <button onclick="appendNumber('9')">9</button>
            <button class="operator" onclick="setOperator('/')">÷</button>
            <button onclick="appendNumber('4')">4</button>
            <button onclick="appendNumber('5')">5</button>
            <button onclick="appendNumber('6')">6</button>
            <button class="operator" onclick="setOperator('*')">×</button>
            <button onclick="appendNumber('1')">1</button>
            <button onclick="appendNumber('2')">2</button>
            <button onclick="appendNumber('3')">3</button>
            <button class="operator" onclick="setOperator('-')">−</button>
            <button onclick="appendNumber('0')">0</button>
            <button onclick="appendNumber('.')">.</button>
            <button class="operator" onclick="setOperator('+')">+</button>
            <button class="operator" onclick="clear()">C</button>
            <button class="equals" onclick="calculate()">=</button>
        </div>
    </div>
    <script>
        let currentValue = '0';
        let previousValue = '';
        let operator = '';
        
        function updateDisplay() {
            document.getElementById('display').textContent = currentValue;
        }
        
        function appendNumber(num) {
            if (currentValue === '0' && num !== '.') {
                currentValue = num;
            } else if (num === '.' && currentValue.includes('.')) {
                return;
            } else {
                currentValue += num;
            }
            updateDisplay();
        }
        
        function setOperator(op) {
            if (operator && previousValue) {
                calculate();
            }
            operator = op;
            previousValue = currentValue;
            currentValue = '0';
        }
        
        function calculate() {
            if (!operator || !previousValue) return;
            const prev = parseFloat(previousValue);
            const current = parseFloat(currentValue);
            let result;
            switch(operator) {
                case '+': result = prev + current; break;
                case '-': result = prev - current; break;
                case '*': result = prev * current; break;
                case '/': result = prev / current; break;
            }
            currentValue = result.toString();
            operator = '';
            previousValue = '';
            updateDisplay();
        }
        
        function clear() {
            currentValue = '0';
            previousValue = '';
            operator = '';
            updateDisplay();
        }
    </script>
</body>
</html>"""


def generate_todo_app(build_type: str) -> str:
    """Generate a todo list app"""
    # Similar implementation...
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Todo List</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { color: #667eea; margin-bottom: 30px; }
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        input {
            flex: 1;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
        }
        button {
            padding: 15px 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover { background: #5568d3; }
        .todo-item {
            padding: 15px;
            background: #f8f8f8;
            margin-bottom: 10px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .todo-item.completed { text-decoration: line-through; opacity: 0.6; }
        .delete-btn {
            background: #e74c3c;
            padding: 8px 15px;
            font-size: 14px;
        }
        .delete-btn:hover { background: #c0392b; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 My Todo List</h1>
        <div class="input-group">
            <input type="text" id="todoInput" placeholder="Add a new task...">
            <button onclick="addTodo()">Add</button>
        </div>
        <div id="todoList"></div>
    </div>
    <script>
        let todos = JSON.parse(localStorage.getItem('todos') || '[]');
        
        function render() {
            const list = document.getElementById('todoList');
            list.innerHTML = todos.map((todo, i) => `
                <div class="todo-item ${todo.completed ? 'completed' : ''}">
                    <span onclick="toggleTodo(${i})" style="cursor:pointer;">${todo.text}</span>
                    <button class="delete-btn" onclick="deleteTodo(${i})">Delete</button>
                </div>
            `).join('');
        }
        
        function addTodo() {
            const input = document.getElementById('todoInput');
            if (input.value.trim()) {
                todos.push({ text: input.value, completed: false });
                input.value = '';
                save();
            }
        }
        
        function toggleTodo(i) {
            todos[i].completed = !todos[i].completed;
            save();
        }
        
        function deleteTodo(i) {
            todos.splice(i, 1);
            save();
        }
        
        function save() {
            localStorage.setItem('todos', JSON.stringify(todos));
            render();
        }
        
        render();
    </script>
</body>
</html>"""


def generate_hello_world(build_type: str) -> str:
    """Generate a simple hello world page"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hello World</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            text-align: center;
            background: white;
            padding: 60px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            font-size: 48px;
            color: #667eea;
            margin-bottom: 20px;
        }
        p {
            font-size: 20px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>👋 Hello World!</h1>
        <p>Welcome to your new app built by SuperAgent v8</p>
    </div>
</body>
</html>"""


def generate_counter(build_type: str) -> str:
    """Generate a counter app"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Counter</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            text-align: center;
            background: white;
            padding: 60px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        #count {
            font-size: 72px;
            color: #667eea;
            margin: 30px 0;
        }
        button {
            padding: 15px 30px;
            margin: 10px;
            font-size: 18px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .increment { background: #667eea; color: white; }
        .decrement { background: #764ba2; color: white; }
        .reset { background: #e74c3c; color: white; }
        button:hover { transform: scale(1.05); }
    </style>
</head>
<body>
    <div class="container">
        <h1>Counter App</h1>
        <div id="count">0</div>
        <button class="increment" onclick="increment()">+</button>
        <button class="decrement" onclick="decrement()">-</button>
        <button class="reset" onclick="reset()">Reset</button>
    </div>
    <script>
        let count = 0;
        function updateDisplay() {
            document.getElementById('count').textContent = count;
        }
        function increment() { count++; updateDisplay(); }
        function decrement() { count--; updateDisplay(); }
        function reset() { count = 0; updateDisplay(); }
    </script>
</body>
</html>"""


def generate_timer(build_type: str) -> str:
    """Generate a timer/stopwatch app"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stopwatch</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            text-align: center;
            background: white;
            padding: 60px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        #time {
            font-size: 64px;
            color: #667eea;
            margin: 30px 0;
            font-family: 'Courier New', monospace;
        }
        button {
            padding: 15px 30px;
            margin: 10px;
            font-size: 18px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s;
            color: white;
        }
        .start { background: #27ae60; }
        .stop { background: #e74c3c; }
        .reset { background: #764ba2; }
        button:hover { transform: scale(1.05); }
    </style>
</head>
<body>
    <div class="container">
        <h1>⏱️ Stopwatch</h1>
        <div id="time">00:00:00</div>
        <button class="start" onclick="start()">Start</button>
        <button class="stop" onclick="stop()">Stop</button>
        <button class="reset" onclick="reset()">Reset</button>
    </div>
    <script>
        let seconds = 0;
        let interval = null;
        
        function updateDisplay() {
            const hrs = Math.floor(seconds / 3600);
            const mins = Math.floor((seconds % 3600) / 60);
            const secs = seconds % 60;
            document.getElementById('time').textContent = 
                `${String(hrs).padStart(2,'0')}:${String(mins).padStart(2,'0')}:${String(secs).padStart(2,'0')}`;
        }
        
        function start() {
            if (!interval) {
                interval = setInterval(() => {
                    seconds++;
                    updateDisplay();
                }, 1000);
            }
        }
        
        function stop() {
            clearInterval(interval);
            interval = null;
        }
        
        function reset() {
            stop();
            seconds = 0;
            updateDisplay();
        }
    </script>
</body>
</html>"""


def generate_generic_app(instruction: str, build_type: str) -> str:
    """Generate a generic app based on the instruction"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>App</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 800px;
            width: 100%;
        }}
        h1 {{
            color: #667eea;
            margin-bottom: 20px;
        }}
        p {{
            color: #666;
            line-height: 1.6;
            margin-bottom: 20px;
        }}
        button {{
            padding: 15px 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.2s;
        }}
        button:hover {{
            background: #5568d3;
            transform: scale(1.05);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Your App</h1>
        <p><strong>Request:</strong> {instruction}</p>
        <p>This is a template-generated app. For AI-powered custom apps, please ensure API keys are configured.</p>
        <button onclick="alert('App is working!')">Click Me!</button>
    </div>
</body>
</html>"""
