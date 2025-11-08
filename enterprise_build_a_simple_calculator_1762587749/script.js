// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
  // Calculator State
  let display = document.getElementById('display');
  let currentValue = '0';
  let previousValue = null;
  let operation = null;
  let history = [];

  // Update display
  function updateDisplay(value = currentValue) {
    display.textContent = value || '0';
  }

  // Calculator functions
  function clear() {
    currentValue = '0';
    previousValue = null;
    operation = null;
    updateDisplay();
  }

  function backspace() {
    currentValue = currentValue.slice(0, -1) || '0';
    updateDisplay();
  }

  function appendNumber(num) {
    if (currentValue === '0') {
      currentValue = num;
    } else {
      currentValue += num;
    }
    updateDisplay();
  }

  function appendOperator(op) {
    if (operation && previousValue !== null) {
      calculate();
    }
    previousValue = currentValue;
    operation = op;
    currentValue = '0';
  }

  function calculate() {
    let result;
    const prev = parseFloat(previousValue);
    const current = parseFloat(currentValue);
    
    switch (operation) {
      case '+':
        result = prev + current;
        break;
      case '−':
        result = prev - current;
        break;
      case '×':
        result = prev * current;
        break;
      case '÷':
        result = prev / current;
        break;
      case '√':
        result = Math.sqrt(current);
        break;
      default:
        return;
    }
    
    // Add to history
    const calculation = `${previousValue} ${operation} ${currentValue} = ${result}`;
    addToHistory(calculation);
    
    currentValue = result.toString();
    operation = null;
    previousValue = null;
    updateDisplay();
  }

  function sqrt() {
    const result = Math.sqrt(parseFloat(currentValue));
    addToHistory(`√${currentValue} = ${result}`);
    currentValue = result.toString();
    updateDisplay();
  }

  function square() {
    const result = Math.pow(parseFloat(currentValue), 2);
    addToHistory(`${currentValue}² = ${result}`);
    currentValue = result.toString();
    updateDisplay();
  }

  function cube() {
    const result = Math.pow(parseFloat(currentValue), 3);
    addToHistory(`${currentValue}³ = ${result}`);
    currentValue = result.toString();
    updateDisplay();
  }

  function pi() {
    currentValue = Math.PI.toString();
    updateDisplay();
  }

  function addToHistory(text) {
    history.unshift(text);
    const historyList = document.getElementById('history-list');
    const li = document.createElement('li');
    li.textContent = text;
    historyList.insertBefore(li, historyList.firstChild);
    
    // Keep only last 10
    if (history.length > 10) {
      history.pop();
      historyList.removeChild(historyList.lastChild);
    }
  }

  // Event listeners
  document.getElementById('clear').addEventListener('click', clear);
  document.getElementById('backspace').addEventListener('click', backspace);
  document.getElementById('divide').addEventListener('click', () => appendOperator('÷'));
  document.getElementById('multiply').addEventListener('click', () => appendOperator('×'));
  document.getElementById('subtract').addEventListener('click', () => appendOperator('−'));
  document.getElementById('add').addEventListener('click', () => appendOperator('+'));
  document.getElementById('equals').addEventListener('click', calculate);
  document.getElementById('sqrt').addEventListener('click', sqrt);
  document.getElementById('square').addEventListener('click', square);
  document.getElementById('cube').addEventListener('click', cube);
  document.getElementById('pi').addEventListener('click', pi);

  // Number buttons
  ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'].forEach((id, index) => {
    document.getElementById(id).addEventListener('click', () => appendNumber(index.toString()));
  });

  document.getElementById('point').addEventListener('click', () => {
    if (!currentValue.includes('.')) {
      currentValue += '.';
      updateDisplay();
    }
  });

  // Keyboard support
  document.addEventListener('keydown', (e) => {
    if (e.key >= '0' && e.key <= '9') appendNumber(e.key);
    if (e.key === '.') document.getElementById('point').click();
    if (e.key === '+') appendOperator('+');
    if (e.key === '-') appendOperator('−');
    if (e.key === '*') appendOperator('×');
    if (e.key === '/') { e.preventDefault(); appendOperator('÷'); }
    if (e.key === 'Enter' || e.key === '=') { e.preventDefault(); calculate(); }
    if (e.key === 'Escape' || e.key === 'c' || e.key === 'C') clear();
    if (e.key === 'Backspace') { e.preventDefault(); backspace(); }
  });

  // Initialize
  updateDisplay();
});
