// State variables
let currentValue = '0';
let previousValue = '';
let currentOperator = null;
let memoryValue = 0;
let history = [];
let decimalPlaces = 2; // Default decimal places
let isDarkMode = false; // Default theme

// DOM element references (Assumed to be present in HTML)
const display = document.getElementById('display');
const historyDisplay = document.getElementById('history'); // Assumed to be present
const buttons = document.querySelectorAll('.calculator button'); // Assumed to be present

// Initialize calculator on load
window.onload = () => {
  loadSettings();
  loadHistory();
  updateDisplay();
  updateHistoryDisplay();
  applyTheme();
};

// Event listeners for buttons
buttons.forEach(button => {
  button.addEventListener('click', handleButtonClick);
});

// Event listener for keyboard support
document.addEventListener('keydown', handleKeyPress);

// Helper Functions

// Format number to a specific decimal places
function formatNumber(number) {
  return parseFloat(number).toFixed(decimalPlaces);
}

// Apply Theme (Dark/Light)
function applyTheme() {
  document.body.classList.toggle('dark-mode', isDarkMode);
}

// Toggle theme
function toggleTheme() {
  isDarkMode = !isDarkMode;
  applyTheme();
  saveSettings();
}

// Reset Calculator State
function clearCalculator() {
  currentValue = '0';
  previousValue = '';
  currentOperator = null;
  updateDisplay();
}

// Delete Last Character
function deleteLastCharacter() {
    currentValue = currentValue.slice(0, -1);
    if (currentValue === '') {
        currentValue = '0';
    }
    updateDisplay();
}

// Add number to current value
function appendNumber(number) {
  if (currentValue === '0') {
    currentValue = number;
  } else {
    currentValue += number;
  }
  updateDisplay();
}

// Add decimal point
function appendDecimal() {
  if (!currentValue.includes('.')) {
    currentValue += '.';
    updateDisplay();
  }
}

// Handle Operator Input
function handleOperator(operator) {
  if (currentOperator && previousValue) {
    calculate();
  }
  previousValue = currentValue;
  currentValue = '0';
  currentOperator = operator;
}

// Perform calculation based on operator
function calculate() {
  let result;
  const prev = parseFloat(previousValue);
  const current = parseFloat(currentValue);

  if (isNaN(prev) || isNaN(current)) return;

  try {
    switch (currentOperator) {
      case '+':
        result = prev + current;
        break;
      case '-':
        result = prev - current;
        break;
      case '*':
        result = prev * current;
        break;
      case '/':
        if (current === 0) {
          throw new Error("Division by zero");
        }
        result = prev / current;
        break;
      default:
        return;
    }

    result = formatNumber(result);
    currentValue = result.toString();
    previousValue = '';
    currentOperator = null;
    updateDisplay();
    saveToHistory(`${prev} ${currentOperator} ${current} = ${result}`);

  } catch (error) {
    currentValue = "Error";
    updateDisplay();
    console.error("Calculation Error: ", error.message);
  }
}

// Memory Functions
function memoryAdd() {
  memoryValue += parseFloat(currentValue) || 0;
  localStorage.setItem('memoryValue', memoryValue.toString());
}

function memorySubtract() {
  memoryValue -= parseFloat(currentValue) || 0;
  localStorage.setItem('memoryValue', memoryValue.toString());
}

function memoryRecall() {
  currentValue = memoryValue.toString();
  updateDisplay();
}

function memoryClear() {
  memoryValue = 0;
  localStorage.setItem('memoryValue', '0');
}

function memoryStore() {
    memoryValue = parseFloat(currentValue) || 0;
    localStorage.setItem('memoryValue', memoryValue.toString());
}


// History functions
function saveToHistory(calculation) {
  history.push(calculation);
  if (history.length > 10) {
    history.shift(); // Limit history to 10 entries
  }
  localStorage.setItem('history', JSON.stringify(history));
  updateHistoryDisplay();
}

function clearHistory() {
    history = [];
    localStorage.removeItem('history');
    updateHistoryDisplay();
}

function updateHistoryDisplay() {
  if (historyDisplay) {
    historyDisplay.innerHTML = ''; // Clear previous history
    history.forEach(item => {
      const p = document.createElement('p');
      p.textContent = item;
      historyDisplay.appendChild(p);
    });
  }
}

function loadHistory() {
  const storedHistory = localStorage.getItem('history');
  if (storedHistory) {
    history = JSON.parse(storedHistory);
  }
  updateHistoryDisplay();
}

// Settings functions
function setDecimalPlaces(places) {
  decimalPlaces = places;
  saveSettings();
  updateDisplay();
}

function saveSettings() {
  const settings = {
    decimalPlaces: decimalPlaces,
    isDarkMode: isDarkMode
  };
  localStorage.setItem('settings', JSON.stringify(settings));
}

function loadSettings() {
  const storedSettings = localStorage.getItem('settings');
  if (storedSettings) {
    const settings = JSON.parse(storedSettings);
    decimalPlaces = settings.decimalPlaces;
    isDarkMode = settings.isDarkMode;
  }
}


// Update the display with the current value
function updateDisplay() {
  if (display) {
    display.textContent = currentValue;
  }
}

// Event Handlers
function handleButtonClick(e) {
  const buttonValue = e.target.textContent;
  const buttonType = e.target.dataset.type;

  switch (buttonType) {
    case 'number':
      appendNumber(buttonValue);
      break;
    case 'operator':
      handleOperator(buttonValue);
      break;
    case 'decimal':
      appendDecimal();
      break;
    case 'equal':
      calculate();
      break;
    case 'clear':
      clearCalculator();
      break;
    case 'delete':
        deleteLastCharacter();
        break;
    case 'memory-add':
      memoryAdd();
      break;
    case 'memory-subtract':
      memorySubtract();
      break;
    case 'memory-recall':
      memoryRecall();
      break;
    case 'memory-clear':
      memoryClear();
      break;
    case 'memory-store':
        memoryStore();
        break;
    case 'toggle-theme':
      toggleTheme();
      break;
    case 'clear-history':
        clearHistory();
        break;
    default:
      console.warn('Unknown button type:', buttonType);
  }
}

function handleKeyPress(e) {
    const key = e.key;

    if (/[0-9]/.test(key)) {
        appendNumber(key);
    } else if (['+', '-', '*', '/'].includes(key)) {
        handleOperator(key);
    } else if (key === '.') {
        appendDecimal();
    } else if (key === 'Enter') {
        calculate();
    } else if (key === 'Escape') {
        clearCalculator();
    } else if (key === 'Backspace') {
        deleteLastCharacter();
    }
}