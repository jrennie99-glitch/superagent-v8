// State variables
let currentValue = '0';
let memory = 0;
let history = [];
let theme = 'light';
let decimalPlaces = 2;

// Helper functions
function add(num1, num2) {
  return parseFloat(num1) + parseFloat(num2);
}

function subtract(num1, num2) {
  return parseFloat(num1) - parseFloat(num2);
}

function multiply(num1, num2) {
  return parseFloat(num1) * parseFloat(num2);
}

function divide(num1, num2) {
  if (num2 === '0') {
    throw new Error('Cannot divide by zero');
  }
  return parseFloat(num1) / parseFloat(num2);
}

function calculate(expression) {
  try {
    // Simple expression parser for operator precedence
    const operators = {
      '+': add,
      '-': subtract,
      '*': multiply,
      '/': divide,
    };

    const tokens = expression.split(' ');
    let result = parseFloat(tokens[0]);

    for (let i = 1; i < tokens.length; i += 2) {
      const operator = tokens[i];
      const operand = tokens[i + 1];
      result = operators[operator](result.toString(), operand);
    }

    return result.toFixed(decimalPlaces);
  } catch (error) {
    return 'Error';
  }
}

function saveToHistory(calc) {
  history.push(calc);
  localStorage.setItem('history', JSON.stringify(history));
}

function loadHistory() {
  const storedHistory = localStorage.getItem('history');
  if (storedHistory) {
    history = JSON.parse(storedHistory);
  }
}

function clearHistory() {
  history = [];
  localStorage.removeItem('history');
}

function toggleTheme() {
  theme = theme === 'light' ? 'dark' : 'light';
  localStorage.setItem('theme', theme);
}

function updateDecimalPlaces(value) {
  decimalPlaces = parseInt(value);
  localStorage.setItem('decimalPlaces', decimalPlaces);
}

// Event listeners
document.addEventListener('keydown', handleKeyPress);

function handleKeyPress(e) {
  switch (e.key) {
    case '0':
    case '1':
    case '2':
    case '3':
    case '4':
    case '5':
    case '6':
    case '7':
    case '8':
    case '9':
      handleButtonClick({ target: { dataset: { value: e.key } } });
      break;
    case '+':
    case '-':
    case '*':
    case '/':
      handleButtonClick({ target: { dataset: { value: e.key } } });
      break;
    case 'Enter':
      handleButtonClick({ target: { dataset: { value: '=' } } });
      break;
    case 'Escape':
      handleButtonClick({ target: { dataset: { value: 'C' } } });
      break;
    case 'Backspace':
      handleButtonClick({ target: { dataset: { value: 'Del' } } });
      break;
    default:
      break;
  }
}

function handleButtonClick(e) {
  const value = e.target.dataset.value;

  switch (value) {
    case '0':
    case '1':
    case '2':
    case '3':
    case '4':
    case '5':
    case '6':
    case '7':
    case '8':
    case '9':
      if (currentValue === '0') {
        currentValue = value;
      } else {
        currentValue += value;
      }
      break;
    case '+':
    case '-':
    case '*':
    case '/':
      if (currentValue !== '' && currentValue !== '0') {
        currentValue += ' ' + value + ' ';
      }
      break;
    case '=':
      try {
        const result = calculate(currentValue);
        if (result !== 'Error') {
          saveToHistory(`${currentValue} = ${result}`);
          currentValue = result;
        } else {
          currentValue = result;
        }
      } catch (error) {
        currentValue = 'Error';
      }
      break;
    case 'C':
      currentValue = '0';
      memory = 0;
      break;
    case 'Del':
      if (currentValue.length > 1) {
        currentValue = currentValue.slice(0, -1);
      } else {
        currentValue = '0';
      }
      break;
    case 'M+':
      memory += parseFloat(currentValue);
      break;
    case 'M-':
      memory -= parseFloat(currentValue);
      break;
    case 'MR':
      currentValue = memory.toString();
      break;
    case 'MC':
      memory = 0;
      break;
    case 'MS':
      memory = parseFloat(currentValue);
      break;
    default:
      break;
  }
}

// Attach button click listeners
function initializeCalculator() {
  const display = document.getElementById('display');
  
  // Number buttons
  document.getElementById('zero').addEventListener('click', () => appendNumber('0'));
  document.getElementById('one').addEventListener('click', () => appendNumber('1'));
  document.getElementById('two').addEventListener('click', () => appendNumber('2'));
  document.getElementById('three').addEventListener('click', () => appendNumber('3'));
  document.getElementById('four').addEventListener('click', () => appendNumber('4'));
  document.getElementById('five').addEventListener('click', () => appendNumber('5'));
  document.getElementById('six').addEventListener('click', () => appendNumber('6'));
  document.getElementById('seven').addEventListener('click', () => appendNumber('7'));
  document.getElementById('eight').addEventListener('click', () => appendNumber('8'));
  document.getElementById('nine').addEventListener('click', () => appendNumber('9'));
  
  // Operation buttons
  document.getElementById('add').addEventListener('click', () => appendOperator('+'));
  document.getElementById('subtract').addEventListener('click', () => appendOperator('-'));
  document.getElementById('multiply').addEventListener('click', () => appendOperator('*'));
  document.getElementById('divide').addEventListener('click', () => appendOperator('/'));
  
  // Special buttons
  document.getElementById('decimal').addEventListener('click', () => appendDecimal());
  document.getElementById('equals').addEventListener('click', () => calculateResult());
  document.getElementById('clear').addEventListener('click', () => clearDisplay());
  document.getElementById('backspace').addEventListener('click', () => backspace());
  
  // Scientific functions
  document.getElementById('sqrt').addEventListener('click', () => calculateSqrt());
  document.getElementById('pi').addEventListener('click', () => appendPi());
  document.getElementById('square').addEventListener('click', () => calculateSquare());
  document.getElementById('cube').addEventListener('click', () => calculateCube());
  
  updateDisplay();
}

// Display functions
function updateDisplay() {
  const display = document.getElementById('display');
  display.value = currentValue;
}

function appendNumber(num) {
  if (currentValue === '0' || currentValue === 'Error') {
    currentValue = num;
  } else {
    currentValue += num;
  }
  updateDisplay();
}

function appendOperator(op) {
  if (currentValue !== '' && currentValue !== '0' && currentValue !== 'Error') {
    // Don't add operator if last character is already an operator
    const lastChar = currentValue.trim().slice(-1);
    if (!['+', '-', '*', '/'].includes(lastChar)) {
      currentValue += ' ' + op + ' ';
      updateDisplay();
    }
  }
}

function appendDecimal() {
  const parts = currentValue.split(' ');
  const lastPart = parts[parts.length - 1];
  if (!lastPart.includes('.')) {
    currentValue += '.';
    updateDisplay();
  }
}

function clearDisplay() {
  currentValue = '0';
  memory = 0;
  updateDisplay();
}

function backspace() {
  if (currentValue.length > 1 && currentValue !== 'Error') {
    currentValue = currentValue.slice(0, -1);
  } else {
    currentValue = '0';
  }
  updateDisplay();
}

function calculateResult() {
  try {
    const result = calculate(currentValue);
    if (result !== 'Error') {
      saveToHistory(`${currentValue} = ${result}`);
      updateHistoryDisplay();
      currentValue = result;
    } else {
      currentValue = 'Error';
    }
    updateDisplay();
  } catch (error) {
    currentValue = 'Error';
    updateDisplay();
  }
}

function calculateSqrt() {
  try {
    const num = parseFloat(currentValue);
    if (!isNaN(num)) {
      currentValue = Math.sqrt(num).toFixed(decimalPlaces);
      updateDisplay();
    }
  } catch (error) {
    currentValue = 'Error';
    updateDisplay();
  }
}

function calculateSquare() {
  try {
    const num = parseFloat(currentValue);
    if (!isNaN(num)) {
      currentValue = Math.pow(num, 2).toFixed(decimalPlaces);
      updateDisplay();
    }
  } catch (error) {
    currentValue = 'Error';
    updateDisplay();
  }
}

function calculateCube() {
  try {
    const num = parseFloat(currentValue);
    if (!isNaN(num)) {
      currentValue = Math.pow(num, 3).toFixed(decimalPlaces);
      updateDisplay();
    }
  } catch (error) {
    currentValue = 'Error';
    updateDisplay();
  }
}

function appendPi() {
  if (currentValue === '0' || currentValue === 'Error') {
    currentValue = Math.PI.toFixed(decimalPlaces);
  } else {
    currentValue += Math.PI.toFixed(decimalPlaces);
  }
  updateDisplay();
}

function updateHistoryDisplay() {
  const historyList = document.getElementById('history-list');
  historyList.innerHTML = '';
  history.slice(-10).reverse().forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;
    historyList.appendChild(li);
  });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  loadHistory();
  initializeCalculator();
  updateHistoryDisplay();
});