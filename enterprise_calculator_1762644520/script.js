<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Calculator</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="calculator-container">
        <div class="calculator-header">
            <h1>Advanced Calculator</h1>
            <button id="settings-btn">Settings</button>
        </div>
        <div class="calculator-display">
            <input type="text" id="display" readonly>
        </div>
        <div class="calculator-keys">
            <button id="clear-btn">C</button>
            <button id="backspace-btn">&lt;</button>
            <button id="divide-btn">÷</button>
            <button id="multiply-btn">×</button>
            <button id="seven-btn">7</button>
            <button id="eight-btn">8</button>
            <button id="nine-btn">9</button>
            <button id="subtract-btn">−</button>
            <button id="four-btn">4</button>
            <button id="five-btn">5</button>
            <button id="six-btn">6</button>
            <button id="add-btn">+</button>
            <button id="one-btn">1</button>
            <button id="two-btn">2</button>
            <button id="three-btn">3</button>
            <button id="equals-btn">=</button>
            <button id="zero-btn">0</button>
            <button id="decimal-btn">.</button>
            <button id="sqrt-btn">√</button>
            <button id="pi-btn">π</button>
            <button id="power-btn">²</button>
            <button id="cube-btn">³</button>
        </div>
        <div class="calculator-settings">
            <h2>Settings</h2>
            <label>
                <input type="checkbox" id="dark-mode-checkbox">
                Dark Mode
            </label>
            <label>
                <input type="checkbox" id="sound-effects-checkbox">
                Sound Effects
            </label>
            <button id="save-settings-btn">Save</button>
        </div>
    </div>
    <script>
        const display = document.getElementById('display');
        const settingsBtn = document.getElementById('settings-btn');
        const settingsContainer = document.querySelector('.calculator-settings');
        const darkModeCheckbox = document.getElementById('dark-mode-checkbox');
        const soundEffectsCheckbox = document.getElementById('sound-effects-checkbox');
        const saveSettingsBtn = document.getElementById('save-settings-btn');
        const clearBtn = document.getElementById('clear-btn');
        const backspaceBtn = document.getElementById('backspace-btn');
        const divideBtn = document.getElementById('divide-btn');
        const multiplyBtn = document.getElementById('multiply-btn');
        const subtractBtn = document.getElementById('subtract-btn');
        const addBtn = document.getElementById('add-btn');
        const equalsBtn = document.getElementById('equals-btn');
        const zeroBtn = document.getElementById('zero-btn');
        const oneBtn = document.getElementById('one-btn');
        const twoBtn = document.getElementById('two-btn');
        const threeBtn = document.getElementById('three-btn');
        const fourBtn = document.getElementById('four-btn');
        const fiveBtn = document.getElementById('five-btn');
        const sixBtn = document.getElementById('six-btn');
        const sevenBtn = document.getElementById('seven-btn');
        const eightBtn = document.getElementById('eight-btn');
        const nineBtn = document.getElementById('nine-btn');
        const decimalBtn = document.getElementById('decimal-btn');
        const sqrtBtn = document.getElementById('sqrt-btn');
        const piBtn = document.getElementById('pi-btn');
        const powerBtn = document.getElementById('power-btn');
        const cubeBtn = document.getElementById('cube-btn');

        let currentExpression = '';
        let history = [];
        let currentIndex = -1;

        function updateDisplay() {
            display.value = currentExpression;
        }

        function handleNumberPress(number) {
            currentExpression += number;
            updateDisplay();
        }

        function handleOperatorPress(operator) {
            currentExpression += operator;
            updateDisplay();
        }

        function handleEqualsPress() {
            try {
                const result = eval(currentExpression);
                history.push(currentExpression + ' = ' + result);
                currentIndex = history.length - 1;
                currentExpression = result.toString();
                updateDisplay();
            } catch (error) {
                currentExpression = 'Error';
                updateDisplay();
            }
        }

        function handleClearPress() {
            currentExpression = '';
            updateDisplay();
        }

        function handleBackspacePress() {
            currentExpression = currentExpression.slice(0, -1);
            updateDisplay();
        }

        function handleUndoPress() {
            if (currentIndex > 0) {
                currentIndex--;
                currentExpression = history[currentIndex].split(' = ')[0];
                updateDisplay();
            }
        }

        function handleRedoPress() {
            if (currentIndex < history.length - 1) {
                currentIndex++;
                currentExpression = history[currentIndex].split(' = ')[0];
                updateDisplay();
            }
        }

        function handleSettingsPress() {
            settingsContainer.classList.toggle('show');
        }

        function handleSaveSettingsPress() {
            const darkMode = darkModeCheckbox.checked;
            const soundEffects = soundEffectsCheckbox.checked;
            localStorage.setItem('darkMode', darkMode);
            localStorage.setItem('soundEffects', soundEffects);
        }

        function init() {
            settingsBtn.addEventListener('click', handleSettingsPress);
            saveSettingsBtn.addEventListener('click', handleSaveSettingsPress);
            clearBtn.addEventListener('click', handleClearPress);
            backspaceBtn.addEventListener('click', handleBackspacePress);
            divideBtn.addEventListener('click', () => handleOperatorPress(' / '));
            multiplyBtn.addEventListener('click', () => handleOperatorPress(' * '));
            subtractBtn.addEventListener('click', () => handleOperatorPress(' - '));
            addBtn.addEventListener('click', () => handleOperatorPress(' + '));
            equalsBtn.addEventListener('click', handleEqualsPress);
            zeroBtn.addEventListener('click', () => handleNumberPress('0'));
            oneBtn.addEventListener('click', () => handleNumberPress('1'));
            twoBtn.addEventListener('click', () => handleNumberPress('2'));
            threeBtn.addEventListener('click', () => handleNumberPress('3'));
            fourBtn.addEventListener('click', () => handleNumberPress('4'));
            fiveBtn.addEventListener('click', () => handleNumberPress('5'));
            sixBtn.addEventListener('click', () => handleNumberPress('6'));
            sevenBtn.addEventListener('click', () => handleNumberPress('7'));
            eightBtn.addEventListener('click', () => handleNumberPress('8'));
            nineBtn.addEventListener('click', () => handleNumberPress('9'));
            decimalBtn.addEventListener('click', () => handleNumberPress('.'));
            sqrtBtn.addEventListener('click', () => handleOperatorPress('Math.sqrt('));
            piBtn.addEventListener('click', () => handleNumberPress(Math.PI));
            powerBtn.addEventListener('click', () => handleOperatorPress(' ** '));
            cubeBtn.addEventListener('click', () => handleOperatorPress(' ** 3'));
            document.addEventListener('keydown', (event) => {
                if (event.key === 'Enter') {
                    handleEqualsPress();
                } else if (event.key === 'Backspace') {
                    handleBackspacePress();
                } else if (event.key === 'c' || event.key === 'C') {
                    handleClearPress();
                }
            });
        }

        init();
    </script>
</body>
</html>