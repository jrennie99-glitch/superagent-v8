// State variables
let currentValue = '0';
let previousValue = null;
let operator = null;
let memory = 0;
let history = [];
let decimalPlaces = 2;
let isLightTheme = true;

// DOM element references (These will need to be defined in HTML)
let display = null; // document.getElementById('display');
let historyDisplay = null; // document.getElementById('history'); //optional element, but allows to print history
let buttons = []; // Array.from(document.querySelectorAll('button'));

// localStorage keys
const HISTORY_KEY = 'calculator_history';
const THEME_KEY = 'calculator_theme';
const DECIMAL_PLACES_KEY = 'calculator_decimal_places';

// Initialization
function initialize() {
    display = document.getElementById('display');
    historyDisplay = document.getElementById('history');
    buttons = Array.from(document.querySelectorAll('button'));

    loadSettings();
    loadHistory();

    buttons.forEach(button => {
        button.addEventListener('click', handleButtonClick);
    });

    document.addEventListener('keydown', handleKeyPress);
}

// Load settings from localStorage
function loadSettings() {
    const storedTheme = localStorage.getItem(THEME_KEY);
    if (storedTheme) {
        isLightTheme = storedTheme === 'light';
        setTheme(); // Assume setTheme function exists to set the actual theme
    }

    const storedDecimalPlaces = localStorage.getItem(DECIMAL_PLACES_KEY);
    if (storedDecimalPlaces) {
        decimalPlaces = parseInt(storedDecimalPlaces, 10);
    }
}

// Save settings to localStorage
function saveSettings() {
    localStorage.setItem(THEME_KEY, isLightTheme ? 'light' : 'dark');
    localStorage.setItem(DECIMAL_PLACES_KEY, decimalPlaces.toString());
}

// Load history from localStorage
function loadHistory() {
    try {
        const storedHistory = localStorage.getItem(HISTORY_KEY);
        if (storedHistory) {
            history = JSON.parse(storedHistory);
            renderHistory();
        }
    } catch (error) {
        console.error("Error loading history:", error);
        history = []; // Reset history if loading fails.
    }
}

// Save history to localStorage
function saveHistory() {
    try {
        localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    } catch (error) {
        console.error("Error saving history:", error);
    }
}

// Event handlers
function handleButtonClick(e) {
    const value = e.target.textContent;
    processInput(value);
}

function handleKeyPress(e) {
    let key = e.key;
    if (key === '*') key = '×';
    if (key === '/') key = '÷';
    if (key === 'Enter') key = '=';
    if (key === 'Escape') key = 'AC';
    if (key === 'Backspace') key = '⌫';

    if (/[0-9+\-×÷=.AC⌫%]/.test(key)) {
        processInput(key);
    }
}

// Main processing function
function processInput(value) {
    try {
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
                handleNumberInput(value);
                break;
            case '.':
                handleDecimalInput();
                break;
            case '+':
            case '-':
            case '×':
            case '÷':
                handleOperatorInput(value);
                break;
            case '=':
                handleEquals();
                break;
            case 'AC':
                handleClearAll();
                break;
            case '⌫':
                handleBackspace();
                break;
            case '+/-':
                handleSignChange();
                break;
            case '%':
                handlePercent();
                break;
            case '√':
                handleSquareRoot();
                break;
            case 'x²':
                handleSquare();
                break;
            case '1/x':
                handleReciprocal();
                break;
            case 'sin':
                handleSine();
                break;
            case 'cos':
                handleCosine();
                break;
            case 'tan':
                handleTangent();
                break;
            case 'log':
                handleLog();
                break;
            case 'ln':
                handleNaturalLog();
                break;
            case 'e':
                handleE();
                break;
            case 'π':
                handlePi();
                break;
            case 'MS':
                handleMemoryStore();
                break;
            case 'MC':
                handleMemoryClear();
                break;
            case 'MR':
                handleMemoryRecall();
                break;
            case 'M+':
                handleMemoryAdd();
                break;
            case 'M-':
                handleMemorySubtract();
                break;
            default:
                console.warn('Unknown input:', value);
        }
    } catch (error) {
        display.value = 'Error';
        console.error('Calculation error:', error);
        currentValue = '0';
        previousValue = null;
        operator = null;
    }
}

// Input handlers
function handleNumberInput(number) {
    if (currentValue === '0' || currentValue === null) {
        currentValue = number;
    } else {
        currentValue += number;
    }
    updateDisplay();
}

function handleDecimalInput() {
    if (!currentValue.includes('.')) {
        currentValue += '.';
        updateDisplay();
    }
}

function handleOperatorInput(op) {
    if (previousValue === null) {
        previousValue = parseFloat(currentValue);
    } else if (operator) {
        previousValue = calculate(previousValue, parseFloat(currentValue), operator);
    }

    operator = op;
    currentValue = '0';
    updateDisplay();
}

function handleEquals() {
    if (previousValue !== null && operator) {
        const secondOperand = parseFloat(currentValue);
        const result = calculate(previousValue, secondOperand, operator);
        saveToHistory(`${previousValue} ${operator} ${secondOperand} = ${result}`);
        currentValue = result.toString();
        previousValue = null;
        operator = null;
        updateDisplay();
    }
}

function handleClearAll() {
    currentValue = '0';
    previousValue = null;
    operator = null;
    updateDisplay();
}

function handleBackspace() {
    currentValue = currentValue.slice(0, -1);
    if (currentValue === '') {
        currentValue = '0';
    }
    updateDisplay();
}

function handleSignChange() {
    currentValue = (parseFloat(currentValue) * -1).toString();
    updateDisplay();
}

function handlePercent() {
  currentValue = (parseFloat(currentValue) / 100).toString();
  updateDisplay();
}

function handleSquareRoot() {
    currentValue = Math.sqrt(parseFloat(currentValue)).toString();
    updateDisplay();
}

function handleSquare() {
    currentValue = Math.pow(parseFloat(currentValue), 2).toString();
    updateDisplay();
}

function handleReciprocal() {
  if(parseFloat(currentValue) === 0){
    currentValue = "Error";
  } else {
    currentValue = (1 / parseFloat(currentValue)).toString();
  }
    updateDisplay();
}

function handleSine() {
    currentValue = Math.sin(parseFloat(currentValue)).toString();
    updateDisplay();
}

function handleCosine() {
    currentValue = Math.cos(parseFloat(currentValue)).toString();
    updateDisplay();
}

function handleTangent() {
    currentValue = Math.tan(parseFloat(currentValue)).toString();
    updateDisplay();
}

function handleLog() {
    currentValue = Math.log10(parseFloat(currentValue)).toString();
    updateDisplay();
}

function handleNaturalLog() {
    currentValue = Math.log(parseFloat(currentValue)).toString();
    updateDisplay();
}

function handleE() {
    currentValue = Math.E.toString();
    updateDisplay();
}

function handlePi() {
    currentValue = Math.PI.toString();
    updateDisplay();
}

// Memory functions
function handleMemoryStore() {
    memory = parseFloat(currentValue);
}

function handleMemoryClear() {
    memory = 0;
}

function handleMemoryRecall() {
    currentValue = memory.toString();
    updateDisplay();
}

function handleMemoryAdd() {
    memory += parseFloat(currentValue);
}

function handleMemorySubtract() {
    memory -= parseFloat(currentValue);
}

// Calculation function with operator precedence
function calculate(num1, num2, op) {
    switch (op) {
        case '+':
            return num1 + num2;
        case '-':
            return num1 - num2;
        case '×':
            return num1 * num2;
        case '÷':
            if (num2 === 0) {
                throw new Error("Division by zero");
            }
            return num1 / num2;
        default:
            throw new Error('Invalid operator');
    }
}

// Helper functions
function formatNumber(number) {
    return parseFloat(number).toFixed(decimalPlaces);
}

// Update display
function updateDisplay() {
    display.value = currentValue;
}

// History functions
function saveToHistory(calc) {
    history.push(calc);
    if (history.length > 10) {
        history.shift(); // Limit to last 10 calculations
    }
    saveHistory();
    renderHistory();
}

function renderHistory() {
  if (!historyDisplay) return;

  historyDisplay.innerHTML = '';
  history.forEach(item => {
    const p = document.createElement('p');
    p.textContent = item;
    historyDisplay.appendChild(p);
  });
}

// Theme Toggle Function
function toggleTheme() {
    isLightTheme = !isLightTheme;
    setTheme();
    saveSettings();
}

function setTheme() {
    // Placeholder: This would be implemented with CSS classes.
    if (isLightTheme) {
      document.body.classList.remove('dark-theme');
      document.body.classList.add('light-theme');
    } else {
      document.body.classList.remove('light-theme');
      document.body.classList.add('dark-theme');
    }
}

//Decimal Settings
function setDecimalPlaces(places){
  decimalPlaces = places;
  saveSettings();
}

// Initialize the calculator when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', initialize);