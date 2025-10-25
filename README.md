# Humanitarian AI Crisis Management System

## 🎯 Project Overview

An advanced **Multi-Agent AI System** for optimizing aid distribution in refugee settlements during humanitarian crises. This system uses multiple specialized AI agents powered by **local LLMs (Ollama)** to make intelligent decisions about resource allocation, logistics planning, and delivery optimization.

### 🌟 Key Features

- **Multi-Agent Architecture**: Four specialized AI agents working collaboratively
- **Local AI Processing**: Uses free, open-source Ollama (no API costs!)
- **Real-time Decision Making**: Intelligent prioritization and resource optimization
- **Route Optimization**: Efficient delivery planning with real-world constraints
- **Adaptive Learning**: Continuous monitoring and improvement recommendations
- **Interactive Visualizations**: Beautiful dashboards and analytics
- **Privacy-First**: All data processing happens locally on your machine

### 🎬 Demo Results

Typical single-cycle results:
- ✅ **85-95% Success Rate** in aid delivery
- 📊 **60-70% Population Coverage** per cycle
- 🚚 **Optimized Routes** reducing delivery time by 30%
- 🎯 **Critical Zone Prioritization** ensuring urgent needs met first

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Guide](#installation-guide)
3. [Quick Start](#quick-start)
4. [Detailed Usage](#detailed-usage)
5. [Viewing Results](#viewing-results)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)
8. [Project Structure](#project-structure)

---

## 🔧 Prerequisites

### System Requirements

- **Operating System**: macOS, Linux, or Windows
- **Python**: Version 3.9 - 3.13 (Python 3.14 has some warnings but works)
- **RAM**: Minimum 8GB (16GB recommended for larger models)
- **Disk Space**: At least 5GB free (for Ollama and models)
- **Internet**: Required only for initial setup

### Software Dependencies

- Python 3.9+
- pip (Python package manager)
- Ollama (for local AI inference)
- Web browser (Chrome, Firefox, or Safari)

---

## 🚀 Installation Guide

### Step 1: Install Ollama

Ollama provides free, local AI models. Choose your platform:

#### **macOS**
```bash
# Using Homebrew (recommended)
brew install ollama

# OR download from https://ollama.ai
```

#### **Linux**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### **Windows**

Download the installer from: https://ollama.ai/download/windows

### Step 2: Start Ollama and Download Model

Open a terminal and run:
```bash
# Start Ollama service (keep this running)
ollama serve
```

**Open a NEW terminal tab/window** and download the AI model:
```bash
# Download small, fast model (recommended - ~2GB)
ollama pull llama3.2:3b

# OR download more powerful model (~4.7GB) - better results
ollama pull llama3.2:8b

# Verify installation
ollama list
```

You should see the model listed. **Keep the `ollama serve` terminal running!**

### Step 3: Clone/Download Project
```bash
# Create project directory
mkdir humanitarian-ai-project
cd humanitarian-ai-project

# Download all project files to this directory
# (Copy all provided Python files, or clone from repository)
```

### Step 4: Set Up Python Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

### Step 5: Install Python Dependencies
```bash
# Upgrade pip first
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

**If you get any errors**, try installing packages individually:
```bash
pip install langchain==0.3.7
pip install langchain-community==0.3.7
pip install numpy==1.26.4
pip install pandas==2.2.0
pip install plotly==5.18.0
pip install python-dotenv==1.0.0
pip install requests==2.31.0
```

### Step 6: Configure Environment

Create a `.env` file in the project root:
```bash
# Create .env file
touch .env

# Add configuration (use any text editor)
echo "OLLAMA_MODEL=llama3.2:3b" >> .env
echo "OLLAMA_BASE_URL=http://localhost:11434" >> .env
```

Or manually create `.env` with this content:
```
OLLAMA_MODEL=llama3.2:3b
OLLAMA_BASE_URL=http://localhost:11434
```

### Step 7: Verify Installation
```bash
# Test that everything works
python -c "from utils.llm_wrapper import LocalLLM; print('✓ System Ready!')"

# Should output: ✓ System Ready!
```

---

## ⚡ Quick Start

### Running Your First Cycle
```bash
# Make sure Ollama is running in another terminal
# Terminal 1:
ollama serve

# Terminal 2 (in project directory with venv activated):
python main.py
```

**Expected output:**
```
╔══════════════════════════════════════════════════════════════════╗
║       HUMANITARIAN AI CRISIS MANAGEMENT SYSTEM                   ║
╚══════════════════════════════════════════════════════════════════╝

INITIALIZING HUMANITARIAN AI SYSTEM
🤖 Initializing AI Agents...
  ✓ Needs Assessment Agent ready
  ✓ Resource Allocation Agent ready
  ✓ Logistics Coordinator Agent ready
  ✓ Monitor & Adaptation Agent ready

...

CYCLE #1 COMPLETE
Success Rate: 85.5%
Population Served: 10,726
```

### Viewing Results
```bash
# Open dashboard in browser
open outputs/dashboard.html          # macOS
xdg-open outputs/dashboard.html      # Linux
start outputs/dashboard.html         # Windows

# Or from VS Code terminal
open outputs/dashboard.html
```

---

## 📚 Detailed Usage

### Running Different Scenarios

Edit `main.py` before running to customize:
```python
# In main.py, modify these settings:

NUM_ZONES = 10              # Number of settlement zones (5-20)
RESOURCE_SCENARIO = 'normal'  # 'abundant', 'normal', or 'scarce'
MAX_ZONES_PER_CYCLE = 7     # Max zones to serve per cycle
NUM_CYCLES = 1              # Number of cycles to run
```

#### Resource Scenarios

- **`abundant`**: 150% resources - Tests optimal conditions
- **`normal`**: 100% resources - Realistic scenario  
- **`scarce`**: 60% resources - Crisis scenario with limited resources

### Running Multiple Cycles

To see how the system learns and adapts:
```python
# In main.py, change:
NUM_CYCLES = 3  # Run 3 consecutive cycles
```

Then run:
```bash
python main.py
```

This will:
- Run 3 distribution cycles
- Show performance trends
- Generate timeline visualization
- Provide multi-cycle summary report

### Testing Individual Components

Test each component separately:
```bash
# Test settlement simulator
python data/settlement_data.py

# Test needs assessment
python agents/needs_assessment.py

# Test resource allocation
python agents/resource_allocation.py

# Test logistics coordinator
python agents/logistics_coordinator.py

# Test monitoring agent
python agents/monitor_adaptation.py

# Test full orchestrator
python core/orchestrator.py
```

---

## 📊 Viewing Results

### Interactive Dashboards

After running, open these HTML files in your browser:

**1. Main Dashboard** (`outputs/dashboard.html`)
- Zone priority scores
- Resource distribution
- Delivery success rates
- Challenges encountered
- Overall performance gauge

**2. Route Map** (`outputs/route_map.html`)
- Geographic visualization of zones
- Delivery routes
- Distribution center location

**3. Performance Timeline** (`outputs/timeline.html`) 
- Only available for multiple cycles
- Shows trends over time
- Success rate progression

### Opening HTML Files

**From Terminal:**
```bash
# macOS
open outputs/dashboard.html

# Linux
xdg-open outputs/dashboard.html

# Windows
start outputs/dashboard.html
```

**From VS Code:**
1. Right-click on HTML file → "Reveal in Finder/Explorer"
2. Double-click to open in browser

**OR install Live Server extension:**
1. Extensions → Search "Live Server"
2. Install by Ritwick Dey
3. Right-click HTML file → "Open with Live Server"

### JSON Results

Detailed data in `outputs/cycle_*.json` includes:

- Complete settlement data
- Priority assessments for all zones
- Resource allocation details
- Delivery routes and schedules
- Actual outcomes vs. planned
- Performance metrics
- Recommendations

View with any text editor or JSON viewer.

---

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Ollama Configuration
OLLAMA_MODEL=llama3.2:3b           # Model to use
OLLAMA_BASE_URL=http://localhost:11434  # Ollama server URL
```

### Main Configuration (main.py)
```python
NUM_ZONES = 10                    # Settlement zones (5-20 recommended)
RESOURCE_SCENARIO = 'normal'      # Resource availability
MAX_ZONES_PER_CYCLE = 7          # Zones to serve per cycle
NUM_CYCLES = 1                    # Number of cycles to run
```

### Model Selection

Different models offer trade-offs between speed and quality:
```bash
# Fast, efficient (recommended for testing)
ollama pull llama3.2:3b          # ~2GB, fast responses

# Better quality (recommended for final results)
ollama pull llama3.2:8b          # ~4.7GB, better reasoning

# High quality (requires 16GB+ RAM)
ollama pull llama3.1:70b         # ~40GB, best results
```

Update `.env` to use different model:
```
OLLAMA_MODEL=llama3.2:8b
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. "Ollama request failed" or Connection Refused

**Problem**: Ollama service not running

**Solution**:
```bash
# Start Ollama in a separate terminal
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags
```

#### 2. "Model not found" Error

**Problem**: AI model not downloaded

**Solution**:
```bash
# Download the model
ollama pull llama3.2:3b

# Verify installation
ollama list
```

#### 3. "ModuleNotFoundError" or Import Errors

**Problem**: Dependencies not installed or wrong Python version

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Check Python version (should be 3.9-3.13)
python --version
```

#### 4. "Object of type int64 is not JSON serializable"

**Problem**: Numpy type conversion issue (already fixed in updated orchestrator.py)

**Solution**: Make sure you have the latest `core/orchestrator.py` with the `convert_numpy()` function in `save_results()` method.

#### 5. Slow Performance or Timeouts

**Problem**: Model too large for your system or Ollama overloaded

**Solution**:
```bash
# Use smaller model
ollama pull llama3.2:3b

# Update .env
OLLAMA_MODEL=llama3.2:3b

# Restart Ollama
pkill ollama
ollama serve
```

#### 6. "UserWarning: Core Pydantic V1 functionality"

**Problem**: Python 3.14 compatibility warning

**Solution**: This is just a warning and doesn't affect functionality. You can:
- Ignore it (system works fine)
- Use Python 3.11-3.13 for cleaner output

#### 7. Empty or Incorrect Visualizations

**Problem**: Invalid data in results

**Solution**:
```bash
# Check if JSON was created
ls -la outputs/*.json

# Verify JSON is valid
python -c "import json; print(json.load(open('outputs/cycle_1_*.json')))"

# Re-run the system
python main.py
```

#### 8. Can't Open HTML Files

**Problem**: Browser not found or file permissions

**Solution**:
```bash
# Make files readable
chmod +r outputs/*.html

# Try different methods
open outputs/dashboard.html                    # macOS
python -m http.server 8000                     # Then go to http://localhost:8000/outputs/
double-click the file in file explorer         # Windows
```

### Getting Help

If you still have issues:

1. Check Ollama is running: `ollama list`
2. Verify Python environment: `which python` (should show venv path)
3. Check dependencies: `pip list | grep -E "langchain|ollama|pandas|plotly"`
4. Review error messages carefully
5. Check outputs folder exists: `ls -la outputs/`

---

## 📁 Project Structure
```
humanitarian-ai-project/
│
├── .env                          # Configuration (create this)
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── main.py                       # Main entry point ⭐ RUN THIS
│
├── data/
│   ├── __init__.py
│   └── settlement_data.py        # Simulates refugee settlements
│
├── agents/                       # AI Agent modules
│   ├── __init__.py
│   ├── needs_assessment.py       # Prioritizes zones by need
│   ├── resource_allocation.py    # Optimizes resource distribution
│   ├── logistics_coordinator.py  # Plans delivery routes
│   └── monitor_adaptation.py     # Tracks outcomes & learns
│
├── core/
│   ├── __init__.py
│   └── orchestrator.py           # Coordinates all agents
│
├── utils/
│   ├── __init__.py
│   ├── llm_wrapper.py           # Ollama LLM interface ⭐ IMPORTANT
│   └── visualization.py          # Creates dashboards
│
└── outputs/                      # Generated results
    ├── cycle_*.json              # Detailed cycle data
    ├── dashboard.html            # Main dashboard
    ├── route_map.html            # Route visualization
    └── timeline.html             # Performance over time
```

---



### Quick Reference Commands
```bash
# Start Ollama
ollama serve

# Activate environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Run system
python main.py

# View results
open outputs/dashboard.html

# Test components
python agents/needs_assessment.py
```

### System Requirements Check
```bash
# Check Python version
python --version  # Should be 3.9-3.13
