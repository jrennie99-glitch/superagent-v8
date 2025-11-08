// Enterprise Calculator Pro 2025 - FIXED VERSION
document.addEventListener('DOMContentLoaded', function() {
    // State Management
    const state = {
        currentValue: '0',
        expression: '',
        previousValue: null,
        operator: null,
        memory: 0,
        history: [],
        mode: 'basic',
        theme: 'light',
        waitingForOperand: false,
        settings: {
            decimalPlaces: 10,
            angleUnit: 'deg',
            soundEnabled: false,
            animationsEnabled: true
        }
    };

    // DOM Elements
    const elements = {
        result: document.getElementById('result'),
        expression: document.getElementById('expression'),
        historyList: document.getElementById('historyList'),
        memoryIndicators: document.getElementById('memoryIndicators'),
        graphCanvas: document.getElementById('graphCanvas'),
        modeBtns: document.querySelectorAll('.mode-btn'),
        modes: document.querySelectorAll('.calculator-mode'),
        tabs: document.querySelectorAll('.tab'),
        tabContents: document.querySelectorAll('.tab-content')
    };

    // Initialize
    loadState();
    setupEventListeners();
    updateDisplay();
    renderHistory();
    setupConverter();

    // Event Listeners Setup
    function setupEventListeners() {
        // Calculator buttons
        document.querySelectorAll('[data-value]').forEach(btn => {
            btn.addEventListener('click', () => handleInput(btn.dataset.value));
        });

        document.querySelectorAll('[data-action]').forEach(btn => {
            btn.addEventListener('click', () => handleAction(btn.dataset.action));
        });

        // Mode switching
        elements.modeBtns.forEach(btn => {
            btn.addEventListener('click', () => switchMode(btn.dataset.mode));
        });

        // Tab switching
        elements.tabs.forEach(tab => {
            tab.addEventListener('click', () => switchTab(tab.dataset.tab));
        });

        // Theme toggle
        document.getElementById('themeToggle').addEventListener('click', toggleTheme);

        // Modal controls
        document.getElementById('helpBtn').addEventListener('click', () => openModal('helpModal'));
        document.getElementById('settingsBtn').addEventListener('click', () => openModal('settingsModal'));
        
        document.querySelectorAll('[data-close]').forEach(btn => {
            btn.addEventListener('click', () => closeModal(btn.dataset.close));
        });

        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) closeModal(modal.id);
            });
        });

        // History controls
        document.getElementById('clearHistory').addEventListener('click', clearHistory);
        document.getElementById('exportHistory').addEventListener('click', exportHistory);
        document.getElementById('historySearch').addEventListener('input', filterHistory);

        // Graph controls
        document.getElementById('plotGraph').addEventListener('click', plotGraph);

        // Converter
        document.getElementById('unitType').addEventListener('change', updateConverterUnits);
        document.getElementById('fromValue').addEventListener('input', convert);
        document.getElementById('fromUnit').addEventListener('change', convert);
        document.getElementById('toUnit').addEventListener('change', convert);
        document.getElementById('swapUnits').addEventListener('click', swapUnits);

        // Settings
        document.getElementById('decimalPlaces').addEventListener('change', (e) => {
            state.settings.decimalPlaces = parseInt(e.target.value);
            saveState();
        });
        document.getElementById('angleUnit').addEventListener('change', (e) => {
            state.settings.angleUnit = e.target.value;
            saveState();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', handleKeyboard);
    }

    // Input Handling - FIXED to properly handle all operations
    function handleInput(value) {
        playSound();
        
        // Handle numbers
        if (!isNaN(value)) {
            if (state.waitingForOperand || state.currentValue === '0') {
                state.currentValue = value;
                state.waitingForOperand = false;
            } else {
                state.currentValue += value;
            }
            updateDisplay();
            return;
        }

        // Handle decimal point
        if (value === '.') {
            if (state.waitingForOperand) {
                state.currentValue = '0.';
                state.waitingForOperand = false;
            } else if (!state.currentValue.includes('.')) {
                state.currentValue += '.';
            }
            updateDisplay();
            return;
        }

        // Handle basic operators
        if (['+', '-', '*', '/'].includes(value)) {
            const currentNumber = parseFloat(state.currentValue);
            
            if (state.previousValue === null) {
                state.previousValue = currentNumber;
            } else if (state.operator) {
                const result = performCalculation();
                state.currentValue = String(result);
                state.previousValue = result;
            }
            
            state.operator = value;
            state.waitingForOperand = true;
            state.expression = `${state.previousValue} ${value}`;
            updateDisplay();
            return;
        }

        // Handle special functions
        const num = parseFloat(state.currentValue);
        let result;

        switch(value) {
            case '+/-':
                result = num * -1;
                break;
            case '%':
                result = num / 100;
                break;
            case '1/x':
                result = 1 / num;
                break;
            case 'x²':
                result = Math.pow(num, 2);
                addToHistory(`${num}² = ${result}`);
                break;
            case 'x³':
                result = Math.pow(num, 3);
                addToHistory(`${num}³ = ${result}`);
                break;
            case '√':
                result = Math.sqrt(num);
                addToHistory(`√${num} = ${result}`);
                break;
            case '∛':
                result = Math.cbrt(num);
                addToHistory(`∛${num} = ${result}`);
                break;
            case 'sin':
                result = Math.sin(toRadians(num));
                addToHistory(`sin(${num}) = ${result}`);
                break;
            case 'cos':
                result = Math.cos(toRadians(num));
                addToHistory(`cos(${num}) = ${result}`);
                break;
            case 'tan':
                result = Math.tan(toRadians(num));
                addToHistory(`tan(${num}) = ${result}`);
                break;
            case 'asin':
                result = fromRadians(Math.asin(num));
                addToHistory(`asin(${num}) = ${result}`);
                break;
            case 'acos':
                result = fromRadians(Math.acos(num));
                addToHistory(`acos(${num}) = ${result}`);
                break;
            case 'atan':
                result = fromRadians(Math.atan(num));
                addToHistory(`atan(${num}) = ${result}`);
                break;
            case 'log':
                result = Math.log10(num);
                addToHistory(`log(${num}) = ${result}`);
                break;
            case 'ln':
                result = Math.log(num);
                addToHistory(`ln(${num}) = ${result}`);
                break;
            case 'exp':
                result = Math.exp(num);
                addToHistory(`exp(${num}) = ${result}`);
                break;
            case 'n!':
                result = factorial(Math.floor(num));
                addToHistory(`${Math.floor(num)}! = ${result}`);
                break;
            case 'π':
                result = Math.PI;
                break;
            case 'e':
                result = Math.E;
                break;
            case 'xʸ':
                // FIXED: Properly handle power operator
                state.previousValue = num;
                state.operator = '^';
                state.waitingForOperand = true;
                state.expression = `${num} ^`;
                updateDisplay();
                return;
            case '(':
            case ')':
                // For future enhancement with expression parser
                return;
        }

        if (result !== undefined) {
            state.currentValue = String(formatNumber(result));
            state.waitingForOperand = true;
        }
        
        updateDisplay();
    }

    // FIXED: Calculation function that properly handles all operators
    function performCalculation() {
        const prev = state.previousValue;
        const current = parseFloat(state.currentValue);

        let result;
        switch(state.operator) {
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
                result = prev / current;
                break;
            case '^':
                result = Math.pow(prev, current);
                break;
            default:
                return current;
        }

        return formatNumber(result);
    }

    function formatNumber(num) {
        if (isNaN(num) || !isFinite(num)) return 'Error';
        
        const rounded = Math.round(num * Math.pow(10, state.settings.decimalPlaces)) / Math.pow(10, state.settings.decimalPlaces);
        
        // Remove unnecessary trailing zeros
        return parseFloat(rounded.toPrecision(12));
    }

    // Action Handling
    function handleAction(action) {
        playSound();
        
        switch(action) {
            case 'equals':
                calculate();
                break;
            case 'clear':
                state.currentValue = '0';
                state.expression = '';
                state.previousValue = null;
                state.operator = null;
                state.waitingForOperand = false;
                updateDisplay();
                break;
            case 'ce':
                state.currentValue = '0';
                state.waitingForOperand = false;
                updateDisplay();
                break;
            case 'backspace':
                if (state.currentValue.length > 1) {
                    state.currentValue = state.currentValue.slice(0, -1);
                } else {
                    state.currentValue = '0';
                }
                updateDisplay();
                break;
            case 'mc':
                state.memory = 0;
                updateMemoryIndicators();
                break;
            case 'mr':
                state.currentValue = String(state.memory);
                state.waitingForOperand = true;
                updateDisplay();
                break;
            case 'm+':
                state.memory += parseFloat(state.currentValue);
                updateMemoryIndicators();
                break;
            case 'm-':
                state.memory -= parseFloat(state.currentValue);
                updateMemoryIndicators();
                break;
        }
    }

    // Calculate - FIXED to properly show calculation in history
    function calculate() {
        if (state.operator && state.previousValue !== null) {
            const result = performCalculation();
            const fullExpression = `${state.previousValue} ${state.operator} ${state.currentValue}`;
            
            // Add to history
            addToHistory(`${fullExpression} = ${result}`);
            
            state.currentValue = String(result);
            state.previousValue = null;
            state.operator = null;
            state.expression = '';
            state.waitingForOperand = true;
            
            updateDisplay();
            saveState();
        }
    }

    // Helper Functions
    function factorial(n) {
        if (n < 0) return NaN;
        if (n === 0 || n === 1) return 1;
        if (n > 170) return Infinity; // Prevent overflow
        let result = 1;
        for (let i = 2; i <= n; i++) result *= i;
        return result;
    }

    function toRadians(degrees) {
        return state.settings.angleUnit === 'deg' ? degrees * Math.PI / 180 : degrees;
    }

    function fromRadians(radians) {
        return state.settings.angleUnit === 'deg' ? radians * 180 / Math.PI : radians;
    }

    // Display Updates
    function updateDisplay() {
        elements.result.textContent = state.currentValue;
        elements.expression.textContent = state.expression;
        
        if (state.settings.animationsEnabled) {
            elements.result.style.animation = 'none';
            setTimeout(() => elements.result.style.animation = '', 10);
        }
    }

    function updateMemoryIndicators() {
        if (state.memory !== 0) {
            elements.memoryIndicators.innerHTML = `<span class="memory-badge">M: ${formatNumber(state.memory)}</span>`;
        } else {
            elements.memoryIndicators.innerHTML = '';
        }
    }

    // History Management
    function addToHistory(text) {
        state.history.unshift({
            expression: text,
            result: state.currentValue,
            timestamp: new Date().toISOString()
        });
        
        if (state.history.length > 100) state.history.pop();
        renderHistory();
        saveState();
    }

    function renderHistory() {
        const searchTerm = document.getElementById('historySearch').value.toLowerCase();
        const filtered = state.history.filter(item => 
            item.expression.toLowerCase().includes(searchTerm)
        );
        
        elements.historyList.innerHTML = filtered.map((item, index) => `
            <div class="history-item" onclick="window.recallHistory(${index})">
                <div class="history-expression">${escapeHtml(item.expression)}</div>
                <div class="history-result">${new Date(item.timestamp).toLocaleString()}</div>
            </div>
        `).join('') || '<p style="text-align: center; color: var(--text-secondary); padding: 2rem;">No history yet</p>';
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    window.recallHistory = function(index) {
        const item = state.history[index];
        if (item && item.result) {
            state.currentValue = item.result;
            state.waitingForOperand = true;
            updateDisplay();
        }
    };

    function clearHistory() {
        if (confirm('Clear all history?')) {
            state.history = [];
            renderHistory();
            saveState();
        }
    }

    function exportHistory() {
        const csv = 'Calculation,Timestamp\n' + 
            state.history.map(item => 
                `"${item.expression}","${new Date(item.timestamp).toLocaleString()}"`
            ).join('\n');
        
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `calculator-history-${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    }

    function filterHistory() {
        renderHistory();
    }

    // Mode Switching - FIXED: Hide programmer mode for now
    function switchMode(mode) {
        // Programmer mode not yet implemented - redirect to scientific
        if (mode === 'programmer') {
            alert('Programmer mode coming soon! Switching to Scientific mode.');
            mode = 'scientific';
        }

        state.mode = mode;
        
        elements.modeBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === mode);
        });
        
        elements.modes.forEach(modeEl => {
            modeEl.classList.toggle('active', modeEl.id === mode + 'Mode');
        });
        
        saveState();
    }

    // Tab Switching
    function switchTab(tab) {
        elements.tabs.forEach(t => {
            t.classList.toggle('active', t.dataset.tab === tab);
        });
        
        elements.tabContents.forEach(content => {
            content.classList.toggle('active', content.id === tab + 'Tab');
        });
    }

    // Theme Toggle
    function toggleTheme() {
        state.theme = state.theme === 'light' ? 'dark' : 'light';
        document.body.setAttribute('data-theme', state.theme);
        
        const icon = document.querySelector('#themeToggle i');
        icon.className = state.theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        
        saveState();
    }

    // Modal Management
    function openModal(modalId) {
        document.getElementById(modalId).classList.add('active');
    }

    function closeModal(modalId) {
        document.getElementById(modalId).classList.remove('active');
    }

    // Graphing - Enhanced
    function plotGraph() {
        const funcStr = document.getElementById('graphFunction').value.trim();
        if (!funcStr) {
            alert('Please enter a function to plot (e.g., sin(x), x^2, sqrt(x))');
            return;
        }

        const canvas = elements.graphCanvas;
        const ctx = canvas.getContext('2d');
        
        // Set canvas size
        canvas.width = canvas.offsetWidth * 2; // Retina display
        canvas.height = canvas.offsetHeight * 2;
        ctx.scale(2, 2);
        
        const width = canvas.width / 2;
        const height = canvas.height / 2;
        
        // Clear canvas
        const bgColor = getComputedStyle(document.body).getPropertyValue('--bg-tertiary').trim();
        ctx.fillStyle = bgColor;
        ctx.fillRect(0, 0, width, height);
        
        // Draw grid
        ctx.strokeStyle = getComputedStyle(document.body).getPropertyValue('--text-secondary').trim();
        ctx.lineWidth = 0.5;
        const gridSize = 50;
        
        for (let i = 0; i < width; i += gridSize) {
            ctx.beginPath();
            ctx.moveTo(i, 0);
            ctx.lineTo(i, height);
            ctx.stroke();
        }
        for (let i = 0; i < height; i += gridSize) {
            ctx.beginPath();
            ctx.moveTo(0, i);
            ctx.lineTo(width, i);
            ctx.stroke();
        }
        
        // Draw axes
        ctx.strokeStyle = getComputedStyle(document.body).getPropertyValue('--text-primary').trim();
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, height / 2);
        ctx.lineTo(width, height / 2);
        ctx.moveTo(width / 2, 0);
        ctx.lineTo(width / 2, height);
        ctx.stroke();
        
        // Plot function
        ctx.strokeStyle = getComputedStyle(document.body).getPropertyValue('--accent-primary').trim();
        ctx.lineWidth = 3;
        ctx.beginPath();
        
        const scale = 50;
        let started = false;
        
        for (let px = 0; px < width; px++) {
            const x = (px - width / 2) / scale;
            try {
                const y = evaluateMathExpression(funcStr, x);
                const py = height / 2 - y * scale;
                
                if (!isNaN(y) && isFinite(y) && py >= 0 && py <= height) {
                    if (!started) {
                        ctx.moveTo(px, py);
                        started = true;
                    } else {
                        ctx.lineTo(px, py);
                    }
                } else {
                    started = false;
                }
            } catch (e) {
                started = false;
            }
        }
        ctx.stroke();
    }

    function evaluateMathExpression(expr, x) {
        // Replace common math functions
        expr = expr.toLowerCase()
            .replace(/x/g, `(${x})`)
            .replace(/sin/g, 'Math.sin')
            .replace(/cos/g, 'Math.cos')
            .replace(/tan/g, 'Math.tan')
            .replace(/sqrt/g, 'Math.sqrt')
            .replace(/log/g, 'Math.log10')
            .replace(/ln/g, 'Math.log')
            .replace(/exp/g, 'Math.exp')
            .replace(/abs/g, 'Math.abs')
            .replace(/\^/g, '**')
            .replace(/pi/g, 'Math.PI')
            .replace(/e(?![a-z])/g, 'Math.E');
        
        return Function('"use strict"; return (' + expr + ')')();
    }

    // Unit Converter
    const conversions = {
        length: {
            units: ['Meters', 'Kilometers', 'Miles', 'Feet', 'Inches', 'Centimeters'],
            toBase: { Meters: 1, Kilometers: 1000, Miles: 1609.34, Feet: 0.3048, Inches: 0.0254, Centimeters: 0.01 }
        },
        temperature: {
            units: ['Celsius', 'Fahrenheit', 'Kelvin'],
            special: true
        },
        weight: {
            units: ['Kilograms', 'Grams', 'Pounds', 'Ounces', 'Tons'],
            toBase: { Kilograms: 1, Grams: 0.001, Pounds: 0.453592, Ounces: 0.0283495, Tons: 1000 }
        },
        currency: {
            units: ['USD', 'EUR', 'GBP', 'JPY', 'CNY'],
            toBase: { USD: 1, EUR: 0.92, GBP: 0.79, JPY: 149.50, CNY: 7.24 }
        }
    };

    function setupConverter() {
        updateConverterUnits();
    }

    function updateConverterUnits() {
        const type = document.getElementById('unitType').value;
        const units = conversions[type].units;
        
        const fromSelect = document.getElementById('fromUnit');
        const toSelect = document.getElementById('toUnit');
        
        fromSelect.innerHTML = units.map(u => `<option value="${u}">${u}</option>`).join('');
        toSelect.innerHTML = units.map(u => `<option value="${u}">${u}</option>`).join('');
        
        if (units.length > 1) toSelect.selectedIndex = 1;
        convert();
    }

    function convert() {
        const type = document.getElementById('unitType').value;
        const from = document.getElementById('fromUnit').value;
        const to = document.getElementById('toUnit').value;
        const value = parseFloat(document.getElementById('fromValue').value) || 0;
        
        let result;
        
        if (conversions[type].special && type === 'temperature') {
            result = convertTemperature(value, from, to);
        } else {
            const baseValue = value * conversions[type].toBase[from];
            result = baseValue / conversions[type].toBase[to];
        }
        
        document.getElementById('toValue').value = result.toFixed(6);
    }

    function convertTemperature(value, from, to) {
        let celsius;
        if (from === 'Celsius') celsius = value;
        else if (from === 'Fahrenheit') celsius = (value - 32) * 5/9;
        else celsius = value - 273.15;
        
        if (to === 'Celsius') return celsius;
        if (to === 'Fahrenheit') return celsius * 9/5 + 32;
        return celsius + 273.15;
    }

    function swapUnits() {
        const fromUnit = document.getElementById('fromUnit').value;
        const toUnit = document.getElementById('toUnit').value;
        const fromValue = document.getElementById('fromValue').value;
        const toValue = document.getElementById('toValue').value;
        
        document.getElementById('fromUnit').value = toUnit;
        document.getElementById('toUnit').value = fromUnit;
        document.getElementById('fromValue').value = toValue;
        
        convert();
    }

    // Keyboard Handling
    function handleKeyboard(e) {
        if (e.key >= '0' && e.key <= '9') handleInput(e.key);
        else if (e.key === '.') handleInput('.');
        else if (e.key === '+') handleInput('+');
        else if (e.key === '-') handleInput('-');
        else if (e.key === '*') handleInput('*');
        else if (e.key === '/') { e.preventDefault(); handleInput('/'); }
        else if (e.key === 'Enter' || e.key === '=') { e.preventDefault(); calculate(); }
        else if (e.key === 'Escape') handleAction('clear');
        else if (e.key === 'Backspace' && !e.target.matches('input')) { e.preventDefault(); handleAction('backspace'); }
        else if (e.ctrlKey && e.key === 't') { e.preventDefault(); toggleTheme(); }
        else if (e.ctrlKey && e.key === ',') { e.preventDefault(); openModal('settingsModal'); }
        else if (e.key === 'F1') { e.preventDefault(); openModal('helpModal'); }
    }

    // Sound Effects
    function playSound() {
        if (!state.settings.soundEnabled) return;
        
        try {
            const audio = new AudioContext();
            const oscillator = audio.createOscillator();
            const gain = audio.createGain();
            
            oscillator.connect(gain);
            gain.connect(audio.destination);
            
            oscillator.frequency.value = 800;
            gain.gain.value = 0.05;
            
            oscillator.start();
            oscillator.stop(audio.currentTime + 0.03);
        } catch (e) {
            // Ignore audio errors
        }
    }

    // State Persistence
    function saveState() {
        try {
            localStorage.setItem('calculatorProState', JSON.stringify({
                memory: state.memory,
                history: state.history.slice(0, 50), // Save last 50
                mode: state.mode,
                theme: state.theme,
                settings: state.settings
            }));
        } catch (e) {
            console.warn('Could not save state:', e);
        }
    }

    function loadState() {
        try {
            const saved = localStorage.getItem('calculatorProState');
            if (saved) {
                const loaded = JSON.parse(saved);
                state.memory = loaded.memory || 0;
                state.history = loaded.history || [];
                state.mode = loaded.mode || 'basic';
                state.theme = loaded.theme || 'light';
                state.settings = { ...state.settings, ...loaded.settings };
                
                // Apply loaded settings
                document.body.setAttribute('data-theme', state.theme);
                document.getElementById('decimalPlaces').value = state.settings.decimalPlaces;
                document.getElementById('angleUnit').value = state.settings.angleUnit;
                document.getElementById('soundEnabled').checked = state.settings.soundEnabled;
                document.getElementById('animationsEnabled').checked = state.settings.animationsEnabled;
                
                const icon = document.querySelector('#themeToggle i');
                icon.className = state.theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
                
                updateMemoryIndicators();
            }
        } catch (e) {
            console.warn('Could not load state:', e);
        }
    }
});
