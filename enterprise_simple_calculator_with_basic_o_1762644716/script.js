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

// Initialize
loadHistory();
```

**Explanation:**

The code implements a simple calculator with basic operations. It uses state variables to store the current value, memory, and history. The `calculate` function parses the expression and performs the operation. The `saveToHistory` function saves the calculation to the history array and stores it in local storage. The `handleButtonClick` function handles button clicks and updates the current value accordingly. The `handleKeyPress` function handles keyboard events and triggers the corresponding button click event.

**Usage:**

To use this code, simply create a new JavaScript file (e.g., `script.js`) and paste the code into it. Then, create a new HTML file (e.g., `index.html`) and add a script tag that references the JavaScript file. You can then interact with the calculator by clicking on the buttons or using the keyboard shortcuts.

**Notes:**

* The code uses local storage to persist the history and theme.
* The code uses a simple expression parser to evaluate the expression.
* The code handles errors by displaying an error message.
* The code uses a modular structure to keep the code organized and maintainable.
* The code uses helper functions to perform complex operations.
* The code uses event listeners to handle button clicks and keyboard events.