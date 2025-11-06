/**
 * Plan Confirmation Flow - Replit-style
 * Shows plan before building, asks for confirmation
 */

let currentPlan = null;
let currentBuildId = null;
let progressInterval = null;

// App states
const AppState = {
  IDLE: 'idle',
  ANALYZING: 'analyzing',
  CONFIRMING: 'confirming',
  BUILDING: 'building',
  COMPLETE: 'complete',
  ERROR: 'error'
};

let currentState = AppState.IDLE;

/**
 * Step 1: User clicks "Build My App"
 * Analyze requirements and show plan
 */
async function startBuild() {
  const userInput = document.getElementById('userInput').value.trim();
  if (!userInput) {
    alert('Please describe what you want to build!');
    return;
  }

  // Change to analyzing state
  setState(AppState.ANALYZING);
  
  // Update UI
  const buildBtn = document.getElementById('buildBtn');
  buildBtn.disabled = true;
  buildBtn.innerHTML = '<span class="spinner"></span> Analyzing...';
  
  // Clear progress
  document.getElementById('progressContent').innerHTML = '';
  document.getElementById('buildStatus').innerHTML = '<span class="spinner"></span> Analyzing...';

  try {
    // Call plan analyzer API
    const response = await fetch('/api/v1/analyze-and-plan', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ instruction: userInput })
    });

    if (!response.ok) {
      throw new Error('Failed to analyze requirements');
    }

    const plan = await response.json();
    currentPlan = plan;
    
    // Show plan confirmation
    showPlanConfirmation(plan);
    setState(AppState.CONFIRMING);
    
    // Re-enable build button
    buildBtn.disabled = false;
    buildBtn.innerHTML = '✨ Build My App';

  } catch (error) {
    console.error('Analysis error:', error);
    showError('Failed to analyze requirements', error.message);
    buildBtn.disabled = false;
    buildBtn.innerHTML = '✨ Build My App';
    setState(AppState.ERROR);
  }
}

/**
 * Step 2: Show plan confirmation UI
 */
function showPlanConfirmation(plan) {
  const progressContent = document.getElementById('progressContent');
  
  const html = `
    <div class="plan-confirmation">
      <div class="plan-header">
        <h3>📋 Plan for Your App</h3>
        <p class="plan-subtitle">Review the plan before building</p>
      </div>

      <div class="plan-section">
        <h4>${plan.title}</h4>
        <p class="plan-description">${plan.description}</p>
        <div class="complexity-badge complexity-${plan.complexity}">${plan.complexity.toUpperCase()}</div>
      </div>

      <div class="plan-section">
        <h4>✨ Components</h4>
        <ul class="component-list">
          ${plan.components.map(c => `<li>✓ ${c}</li>`).join('')}
        </ul>
      </div>

      <div class="plan-section">
        <h4>🛠️ Tech Stack</h4>
        <div class="tech-stack">
          ${Object.entries(plan.tech_stack).map(([key, value]) => `
            <div class="tech-item">
              <span class="tech-label">${key}:</span>
              <span class="tech-value">${value}</span>
            </div>
          `).join('')}
        </div>
      </div>

      <div class="plan-section">
        <h4>⏱️ Estimated Time</h4>
        <div class="time-estimates">
          <div class="time-item">
            <span>Design Only:</span>
            <span class="time-badge">${plan.estimated_time.design_only}</span>
          </div>
          <div class="time-item">
            <span>Full Build:</span>
            <span class="time-badge">${plan.estimated_time.full_build}</span>
          </div>
        </div>
      </div>

      <div class="plan-section">
        <h4>🎯 Choose Build Type</h4>
        <div class="build-options">
          ${plan.options.map(option => `
            <button class="build-option-btn ${option.type === 'full' ? 'primary' : ''}" 
                    onclick="confirmBuild('${option.type}')">
              <div class="option-label">${option.label}</div>
              <div class="option-description">${option.description}</div>
              <div class="option-time">${option.time}</div>
            </button>
          `).join('')}
        </div>
      </div>

      <div class="plan-actions">
        <button class="secondary-btn" onclick="revisePlan()">← Revise Plan</button>
      </div>
    </div>
  `;
  
  progressContent.innerHTML = html;
  document.getElementById('buildStatus').textContent = 'Plan Ready - Choose Build Type';
}

/**
 * Step 3: User confirms build type (design or full)
 */
async function confirmBuild(buildType) {
  if (!currentPlan) {
    alert('No plan available. Please try again.');
    return;
  }

  setState(AppState.BUILDING);
  
  // Update UI
  const buildBtn = document.getElementById('buildBtn');
  buildBtn.disabled = true;
  buildBtn.innerHTML = '<span class="spinner"></span> Building...';
  
  // Clear progress and show building state
  document.getElementById('progressContent').innerHTML = '';
  document.getElementById('buildStatus').innerHTML = '<span class="spinner"></span> Building...';

  // Get options
  const planMode = document.getElementById('planMode').checked;
  const enterpriseMode = document.getElementById('enterpriseMode').checked;
  const livePreview = document.getElementById('livePreview').checked;
  const autoDeploy = document.getElementById('autoDeploy').checked;

  // Show preview panel if enabled
  if (livePreview) {
    document.getElementById('previewPanel').classList.remove('hidden');
  }

  try {
    // Start the actual build
    const response = await fetch('/api/v1/build-realtime', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        instruction: currentPlan.title,
        plan_id: currentPlan.plan_id,
        build_type: buildType,
        plan_mode: planMode,
        enterprise_mode: enterpriseMode,
        live_preview: livePreview,
        auto_deploy: autoDeploy
      })
    });

    if (!response.ok) {
      throw new Error('Failed to start build');
    }

    const data = await response.json();
    currentBuildId = data.build_id;

    // Start polling for progress
    pollProgress();

  } catch (error) {
    console.error('Build error:', error);
    showError('Build Failed', error.message);
    buildBtn.disabled = false;
    buildBtn.innerHTML = '✨ Build My App';
    setState(AppState.ERROR);
  }
}

/**
 * Step 4: Poll for build progress
 */
function pollProgress() {
  if (!currentBuildId) return;

  progressInterval = setInterval(async () => {
    try {
      const response = await fetch(`/api/v1/build-progress/${currentBuildId}`);
      const data = await response.json();

      // Update progress steps
      if (data.steps && data.steps.length > 0) {
        updateProgressSteps(data.steps);
      }

      // Update preview if available
      if (data.preview_url) {
        document.getElementById('previewUrl').textContent = data.preview_url;
        document.getElementById('previewIframe').src = data.preview_url;
      }

      // Check if complete
      if (data.status === 'complete') {
        clearInterval(progressInterval);
        setState(AppState.COMPLETE);
        document.getElementById('buildStatus').innerHTML = '✅ Build Complete!';
        document.getElementById('buildBtn').disabled = false;
        document.getElementById('buildBtn').innerHTML = '✨ Build My App';

        // Show deployment URL
        if (data.deployment_url) {
          addProgressStep('complete', '🎉 Deployment Complete!', 
            `Your app is live at: ${data.deployment_url}`, data.total_time);
        }
      }

      // Check if error
      if (data.status === 'error') {
        clearInterval(progressInterval);
        setState(AppState.ERROR);
        document.getElementById('buildStatus').innerHTML = '❌ Build Failed';
        document.getElementById('buildBtn').disabled = false;
        document.getElementById('buildBtn').innerHTML = '✨ Build My App';
      }

    } catch (error) {
      console.error('Progress poll error:', error);
    }
  }, 1000); // Poll every second
}

/**
 * Update progress steps in UI
 */
function updateProgressSteps(steps) {
  const progressContent = document.getElementById('progressContent');
  
  const html = steps.map(step => {
    const statusIcon = {
      'pending': '⏳',
      'active': '⏳',
      'complete': '✅',
      'error': '❌'
    }[step.status] || '⏳';
    
    const statusClass = step.status;
    
    return `
      <div class="progress-step ${statusClass}">
        <div class="step-header">
          <span class="step-icon">${statusIcon}</span>
          <span class="step-title">${step.title}</span>
          ${step.time_elapsed ? `<span class="step-time">${step.time_elapsed}s</span>` : ''}
        </div>
        <div class="step-detail">${step.detail}</div>
      </div>
    `;
  }).join('');
  
  progressContent.innerHTML = html;
}

/**
 * Add a single progress step (legacy support)
 */
function addProgressStep(status, title, detail, time) {
  // This function is kept for compatibility
  // The new updateProgressSteps handles all steps at once
}

/**
 * Revise plan - go back to input
 */
function revisePlan() {
  currentPlan = null;
  setState(AppState.IDLE);
  
  // Clear progress
  const progressContent = document.getElementById('progressContent');
  progressContent.innerHTML = `
    <div style="text-align: center; padding: 3rem; color: #8b949e;">
      <div style="font-size: 3rem; margin-bottom: 1rem;">🚀</div>
      <div style="font-size: 1.125rem; margin-bottom: 0.5rem;">Ready to Build Amazing Apps</div>
      <div style="font-size: 0.875rem;">Enter your idea and click "Build My App" to get started!</div>
    </div>
  `;
  
  document.getElementById('buildStatus').textContent = 'Ready to build';
  document.getElementById('userInput').focus();
}

/**
 * Show error message
 */
function showError(title, message) {
  const progressContent = document.getElementById('progressContent');
  progressContent.innerHTML = `
    <div class="error-message">
      <div class="error-icon">❌</div>
      <div class="error-title">${title}</div>
      <div class="error-detail">${message}</div>
      <button class="retry-btn" onclick="revisePlan()">Try Again</button>
    </div>
  `;
}

/**
 * Set app state
 */
function setState(state) {
  currentState = state;
  console.log('State changed to:', state);
}

/**
 * Preview panel functions
 */
function refreshPreview() {
  const iframe = document.getElementById('previewIframe');
  iframe.src = iframe.src;
}

function openInNewTab() {
  const url = document.getElementById('previewUrl').textContent;
  if (url && url !== 'Building...') {
    window.open(url, '_blank');
  }
}
