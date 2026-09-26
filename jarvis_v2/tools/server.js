#!/usr/bin/env node
/**
 * JARVIS Tool Server - System Control & Automation
 * Node.js 18+ with async/await
 * 
 * Features:
 * - OS control (app management, desktop switching)
 * - Browser automation (Playwright)
 * - System commands (terminal execution)
 * - File operations (CRUD, search, organize)
 * - Metrics monitoring (CPU, RAM, Disk, GPU, Fan)
 */

import express from 'express';
import cors from 'cors';
import { exec, spawn } from 'child_process';
import { promisify } from 'util';
import fs from 'fs/promises';
import path from 'path';
import os from 'os';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const execAsync = promisify(exec);

const app = express();
const PORT = process.env.TOOL_SERVER_PORT || 8002;

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));

// Platform detection
const IS_MAC = process.platform === 'darwin';
const IS_WINDOWS = process.platform === 'win32';
const IS_LINUX = process.platform === 'linux';

// ============================================================================
// SAFE EXEC WRAPPER — Sunucu asla çökmez, hata JSON olarak döner
// ============================================================================

/**
 * execAsync'i try-catch ile saran güvenli wrapper.
 * Başarısız olursa { success: false, error: "Başarısız: <neden>" } döner.
 */
async function safeExec(command, options = {}) {
  try {
    const { stdout, stderr } = await execAsync(command, {
      timeout: options.timeout || 15000,
      ...options,
    });
    return { success: true, stdout: stdout.trim(), stderr: stderr.trim() };
  } catch (err) {
    const reason = err.stderr?.trim() || err.message || 'Bilinmeyen hata';
    console.error(`[EXEC FAIL] ${command} → ${reason}`);
    return { success: false, error: `Başarısız: ${reason}`, command };
  }
}

/**
 * osascript çağrısı için özel wrapper.
 */
async function safeOsascript(script, description = 'osascript') {
  const result = await safeExec(`osascript -e '${script}'`);
  if (!result.success) {
    console.error(`[OSASCRIPT FAIL] ${description}: ${result.error}`);
  }
  return result;
}

// ============================================================================
// HEALTH & STATUS
// ============================================================================

app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'jarvis-tool-server',
    version: '2.0.0',
    platform: process.platform,
    uptime: process.uptime(),
    memory: process.memoryUsage()
  });
});

// ============================================================================
// ACTION EXECUTOR
// ============================================================================

app.post('/action', async (req, res) => {
  const { action, target, params } = req.body;
  
  console.log(`[ACTION] ${action} ${target || ''}`);
  
  try {
    let result;
    
    switch (action) {
      // App Management
      case 'open_app':
        result = await openApp(params?.app_name || target);
        break;
      case 'close_app':
        result = await closeApp(target);
        break;
      case 'focus_app':
        result = await focusApp(target);
        break;
      case 'list_apps':
        result = await listApps();
        break;
      case 'minimize_window':
        result = await minimizeWindow(target);
        break;
      case 'maximize_window':
        result = await maximizeWindow(target);
        break;
      
      // Desktop Management
      case 'list_desktops':
        result = await listDesktops();
        break;
      case 'switch_desktop':
        result = await switchDesktop(target);
        break;
      case 'create_desktop':
        result = await createDesktop();
        break;
      case 'move_app_to_desktop':
        result = await moveAppToDesktop(target, params?.desktop);
        break;
      
      // System Settings
      case 'set_volume':
        result = await setVolume(target);
        break;
      case 'get_volume':
        result = await getVolume();
        break;
      case 'set_brightness':
        result = await setBrightness(target);
        break;
      case 'toggle_wifi':
        result = await toggleWifi();
        break;
      case 'toggle_bluetooth':
        result = await toggleBluetooth();
        break;
      case 'get_battery':
        result = await getBattery();
        break;
      case 'get_system_metrics':
        result = await getSystemMetrics();
        break;
      case 'get_fan_speed':
        result = await getFanSpeed();
        break;
      case 'get_gpu_info':
        result = await getGPUInfo();
        break;
      
      // Terminal
      case 'execute_command':
        result = await executeCommand(target, params);
        break;
      case 'create_script':
        result = await createScript(target, params?.content);
        break;
      case 'run_script':
        result = await runScript(target);
        break;
      
      // File System
      case 'create_file':
        result = await createFile(target, params?.content);
        break;
      case 'delete_file':
        result = await deleteFile(target);
        break;
      case 'list_files':
        result = await listFiles(target);
        break;
      case 'search_files':
        result = await searchFiles(target, params?.pattern);
        break;
      case 'get_file_info':
        result = await getFileInfo(target);
        break;
      case 'find_large_files':
        result = await findLargeFiles(target, params?.minSize);
        break;
      case 'create_folder':
        result = await createFolder(target);
        break;
      
      // Dynamic Code Writing
      case 'write_code_and_open':
        result = await writeCodeAndOpen(
          params?.filename || target,
          params?.content || '',
          params?.open_in_vscode !== false
        );
        break;
      
      // Terminal execution with CWD support
      case 'run_terminal':
        result = await runTerminalCommand(
          params?.command || target,
          params?.cwd || ''
        );
        break;
      
      // Read existing file content
      case 'read_file_content':
        result = await readFileContent(params?.filepath || target);
        break;
      
      // Overwrite file with new content and open in VS Code
      case 'update_file_content':
        result = await updateFileContent(
          params?.filepath || target,
          params?.new_content || '',
          params?.open_in_vscode !== false
        );
        break;
      
      // Browser
      case 'open_url':
        result = await openURL(target);
        break;
      case 'web_search':
        result = await webSearch(target);
        break;
      case 'take_screenshot':
        result = await takeScreenshot(params?.path);
        break;
      case 'navigate_to':
        result = await navigateTo(target);
        break;
      case 'fill_form':
        result = await fillForm(params?.formData || {});
        break;
      case 'click_element':
        result = await clickElement(target);
        break;
      case 'get_text':
        result = await getText(target);
        break;
      case 'get_page_content':
        result = await getPageContent();
        break;
      case 'wait_for_element':
        result = await waitForElement(target, params?.timeout);
        break;
      case 'execute_script':
        result = await executeScript(target);
        break;
      case 'close_browser':
        await closeBrowser();
        result = { closed: true };
        break;
      
      default:
        result = { success: false, error: `Unknown action: ${action}` };
    }
    
    res.json({
      success: true,
      action,
      target,
      result,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error(`[ERROR] ${action}:`, error.message);
    res.status(500).json({
      success: false,
      action,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// ============================================================================
// BATCH ACTIONS
// ============================================================================

app.post('/batch', async (req, res) => {
  const { actions } = req.body;
  
  if (!Array.isArray(actions)) {
    return res.status(400).json({ error: 'actions must be an array' });
  }
  
  console.log(`[BATCH] Processing ${actions.length} actions`);
  
  const results = [];
  
  for (const actionReq of actions) {
    try {
      const response = await fetch(`http://localhost:${PORT}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(actionReq)
      });
      
      const result = await response.json();
      results.push(result);
    } catch (error) {
      results.push({
        success: false,
        action: actionReq.action,
        error: error.message
      });
    }
  }
  
  res.json({
    success: true,
    total: actions.length,
    results,
    timestamp: new Date().toISOString()
  });
});

// ============================================================================
// APP MANAGEMENT FUNCTIONS
// ============================================================================

async function openApp(appName) {
  if (!IS_MAC) throw new Error('Platform not supported');

  const appMap = {
    'instagram': 'Instagram', 'spotify': 'Spotify',
    'chrome': 'Google Chrome', 'safari': 'Safari',
    'mail': 'Mail', 'notes': 'Notes',
    'vscode': 'Visual Studio Code', 'visual studio code': 'Visual Studio Code',
    'terminal': 'Terminal', 'browser': 'Safari',
    'finder': 'Finder', 'xcode': 'Xcode',
    'stm32cubeide': 'STM32CubeIDE', 'capcut': 'CapCut',
  };

  const actualName = appMap[appName?.toLowerCase()] || appName;
  const result = await safeExec(`open -a "${actualName}"`);

  if (!result.success) {
    // Fallback: open without -a flag
    const fallback = await safeExec(`open "${actualName}"`);
    if (!fallback.success) {
      return { success: false, error: `Başarısız: "${actualName}" uygulaması bulunamadı.` };
    }
    return { success: true, opened: actualName, method: 'fallback' };
  }
  return { success: true, opened: actualName };
}

async function closeApp(appName) {
  if (!IS_MAC) throw new Error('Platform not supported');
  const result = await safeOsascript(`quit app "${appName}"`, `closeApp(${appName})`);
  return result.success ? { closed: appName } : result;
}

async function focusApp(appName) {
  if (!IS_MAC) throw new Error('Platform not supported');
  const result = await safeOsascript(`tell application "${appName}" to activate`, `focusApp(${appName})`);
  return result.success ? { focused: appName } : result;
}

async function listApps() {
  if (!IS_MAC) throw new Error('Platform not supported');
  const result = await safeOsascript(
    `tell application "System Events" to get name of every process whose background only is false`,
    'listApps'
  );
  if (!result.success) return result;
  const apps = result.stdout.split(', ').filter(Boolean);
  return { apps, count: apps.length };
}

async function minimizeWindow(appName) {
  if (!IS_MAC) throw new Error('Platform not supported');
  const result = await safeOsascript(
    `tell application "System Events" to tell process "${appName}" to set miniaturized of window 1 to true`,
    `minimizeWindow(${appName})`
  );
  return result.success ? { minimized: appName } : result;
}

async function maximizeWindow(appName) {
  if (!IS_MAC) throw new Error('Platform not supported');
  const result = await safeOsascript(
    `tell application "System Events" to tell process "${appName}" to set miniaturized of window 1 to false`,
    `maximizeWindow(${appName})`
  );
  return result.success ? { maximized: appName } : result;
}

// ============================================================================
// DESKTOP MANAGEMENT
// ============================================================================

async function listDesktops() {
  if (IS_MAC) {
    // macOS Mission Control spaces
    const { stdout } = await execAsync(`osascript -e 'tell application "System Events" to get properties of desktops'`);
    return { desktops: stdout.trim() };
  }
  
  throw new Error('Platform not supported');
}

async function switchDesktop(desktopNumber) {
  if (IS_MAC) {
    await execAsync(`osascript -e 'tell application "System Events" to key code ${18 + parseInt(desktopNumber)} using control down'`);
    return { switched_to: desktopNumber };
  }
  
  throw new Error('Platform not supported');
}

async function createDesktop() {
  if (IS_MAC) {
    await execAsync(`osascript -e 'tell application "System Events" to keystroke "n" using {control down}'`);
    return { created: true };
  }
  
  throw new Error('Platform not supported');
}

async function moveAppToDesktop(appName, desktopNumber) {
  if (IS_MAC) {
    // This requires accessibility permissions
    await execAsync(`osascript -e 'tell application "System Events" to tell process "${appName}" to set value of attribute "AXWindow" to desktop ${desktopNumber}'`);
    return { moved: appName, to_desktop: desktopNumber };
  }
  
  throw new Error('Platform not supported');
}

// ============================================================================
// SYSTEM SETTINGS
// ============================================================================

async function setVolume(level) {
  if (!IS_MAC) throw new Error('Platform not supported');
  const result = await safeExec(`osascript -e "set volume output volume ${parseInt(level) || 50}"`);
  return result.success ? { volume: level } : result;
}

async function getVolume() {
  if (!IS_MAC) throw new Error('Platform not supported');
  const result = await safeExec(`osascript -e "output volume of (get volume settings)"`);
  return result.success ? { volume: parseInt(result.stdout) || 0 } : result;
}

async function setBrightness(level) {
  if (!IS_MAC) throw new Error('Platform not supported');
  const result = await safeExec(`brightness ${parseFloat(level) / 100}`);
  return result.success ? { brightness: level } : { ...result, note: 'Install: brew install brightness' };
}

async function toggleWifi() {
  if (!IS_MAC) throw new Error('Platform not supported');
  const result = await safeExec(`networksetup -setairportpower en0 toggle`);
  return result.success ? { toggled: true } : result;
}

async function toggleBluetooth() {
  if (!IS_MAC) throw new Error('Platform not supported');
  const result = await safeExec(`blueutil -p toggle`);
  return result.success ? { toggled: true } : { ...result, note: 'Install: brew install blueutil' };
}

async function getBattery() {
  if (!IS_MAC) throw new Error('Platform not supported');
  const result = await safeExec(`pmset -g batt | grep -Eo "\\d+%"`);
  return result.success ? { battery: result.stdout } : result;
}

async function getSystemMetrics() {
  const [cpuUsage, memUsage, diskUsage] = await Promise.all([
    getCPUUsage(), getMemoryUsage(), getDiskUsage()
  ]);
  return { cpu: cpuUsage, memory: memUsage, disk: diskUsage, platform: process.platform, uptime: os.uptime() };
}

async function getCPUUsage() {
  if (!IS_MAC) return 0;
  const result = await safeExec(`top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//'`);
  return result.success ? (parseFloat(result.stdout) || 0) : 0;
}

async function getMemoryUsage() {
  const totalMem = os.totalmem();
  const freeMem  = os.freemem();
  return Math.round(((totalMem - freeMem) / totalMem) * 100);
}

async function getDiskUsage() {
  if (!IS_MAC) return 0;
  const result = await safeExec(`df -h / | tail -1 | awk '{print $5}' | sed 's/%//'`);
  return result.success ? (parseInt(result.stdout) || 0) : 0;
}

async function getFanSpeed() {
  if (!IS_MAC) throw new Error('Platform not supported');
  const result = await safeExec(`istats fan speed`);
  return result.success
    ? { fan_speed: result.stdout }
    : { fan_speed: 'N/A', note: 'Install: gem install iStats' };
}

async function getGPUInfo() {
  if (!IS_MAC) throw new Error('Platform not supported');
  const result = await safeExec(`system_profiler SPDisplaysDataType | grep "Chipset Model"`);
  return result.success ? { gpu: result.stdout } : { gpu: 'N/A' };
}

// ============================================================================
// TERMINAL FUNCTIONS
// ============================================================================

async function executeCommand(command, params = {}) {
  const { cwd, timeout = 30000 } = params;
  
  // Security: Parse command and use spawn without shell to prevent injection
  const commandParts = command.trim().split(/\s+/);
  const cmd = commandParts[0];
  const args = commandParts.slice(1);
  
  return new Promise((resolve, reject) => {
    const child = spawn(cmd, args, {
      cwd: cwd || process.cwd(),
      timeout,
      shell: false  // CRITICAL: Disable shell to prevent command injection
    });
    
    let stdout = '';
    let stderr = '';
    
    child.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    child.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    child.on('close', (code) => {
      resolve({
        stdout: stdout.trim(),
        stderr: stderr.trim(),
        command,
        exitCode: code
      });
    });
    
    child.on('error', (error) => {
      reject(new Error(`Command execution failed: ${error.message}`));
    });
    
    // Timeout handling
    setTimeout(() => {
      child.kill();
      reject(new Error(`Command timeout after ${timeout}ms`));
    }, timeout);
  });
}

// ============================================================================
// DYNAMIC CODE WRITING & TERMINAL
// ============================================================================

/**
 * Read existing file content — returns string or "FILE_NOT_FOUND"
 * Supports absolute paths and paths relative to jarvis_temp_workspace
 */
async function readFileContent(filepath) {
  if (!filepath) throw new Error('filepath is required');

  // Resolve: absolute path → use as-is; relative → workspace-relative
  let resolvedPath = filepath;
  if (!path.isAbsolute(filepath)) {
    const workspaceDir = path.join(process.cwd(), 'jarvis_temp_workspace');
    resolvedPath = path.join(workspaceDir, path.basename(filepath));
  }

  console.log(`📖 Reading file: ${resolvedPath}`);

  try {
    const content = await fs.readFile(resolvedPath, 'utf8');
    const stats = await fs.stat(resolvedPath);
    console.log(`✅ Read ${content.length} chars from ${resolvedPath}`);
    return {
      success: true,
      filepath: resolvedPath,
      filename: path.basename(resolvedPath),
      content,
      size: stats.size,
      modified: stats.mtime
    };
  } catch (err) {
    if (err.code === 'ENOENT') {
      console.warn(`⚠️  File not found: ${resolvedPath}`);
      return {
        success: false,
        filepath: resolvedPath,
        content: null,
        error: 'FILE_NOT_FOUND'
      };
    }
    throw err;
  }
}

/**
 * Overwrite file with new content (from LLM) and bring it up in VS Code
 * Creates the file if it doesn't exist yet
 */
async function updateFileContent(filepath, newContent, openInVscode = true) {
  if (!filepath) throw new Error('filepath is required');
  if (newContent === undefined || newContent === null) throw new Error('new_content is required');

  // Resolve path same as readFileContent
  let resolvedPath = filepath;
  if (!path.isAbsolute(filepath)) {
    const workspaceDir = path.join(process.cwd(), 'jarvis_temp_workspace');
    await fs.mkdir(workspaceDir, { recursive: true });
    resolvedPath = path.join(workspaceDir, path.basename(filepath));
  }

  console.log(`✏️  Updating file: ${resolvedPath} (${newContent.length} chars)`);

  // Write atomically: temp → rename
  const tempPath = resolvedPath + '.jarvis_tmp';
  await fs.writeFile(tempPath, newContent, 'utf8');
  await fs.rename(tempPath, resolvedPath);

  console.log(`✅ Updated: ${resolvedPath}`);

  // Bring file to front in VS Code
  if (openInVscode) {
    try {
      await execAsync(`code "${resolvedPath}"`);
    } catch {
      try { await execAsync(`open -a "Visual Studio Code" "${resolvedPath}"`); } catch {}
    }
  }

  return {
    success: true,
    filepath: resolvedPath,
    filename: path.basename(resolvedPath),
    size: newContent.length,
    opened_in_vscode: openInVscode
  };
}

/**
 * Write any code/text to a dynamic filename and open in VS Code
 * LLM decides the filename + extension based on content type
 * 
 * Examples:
 *   simulation.cpp  → C++ flight simulation
 *   App.tsx         → React component
 *   scraper.py      → Python web scraper
 *   notlar.txt      → Plain text notes
 *   main.go         → Go server
 */
async function writeCodeAndOpen(filename, content, openInVscode = true) {
  if (!filename || !content) {
    throw new Error('filename and content are required');
  }
  
  // Security: prevent directory traversal
  const safeName = path.basename(filename);
  
  // Workspace directory
  const workspaceDir = path.join(process.cwd(), 'jarvis_temp_workspace');
  const filePath = path.join(workspaceDir, safeName);
  
  // Create workspace if not exists
  await fs.mkdir(workspaceDir, { recursive: true });
  
  // Write file
  await fs.writeFile(filePath, content, 'utf8');
  console.log(`✅ Written: ${filePath}`);
  
  // Open in VS Code
  if (openInVscode && IS_MAC) {
    try {
      await execAsync(`code "${filePath}"`);
      console.log(`📂 Opened in VS Code: ${safeName}`);
    } catch (e) {
      // VS Code CLI not in PATH, try open
      await execAsync(`open -a "Visual Studio Code" "${filePath}"`);
    }
  }
  
  return {
    success: true,
    filename: safeName,
    path: filePath,
    size: content.length,
    opened_in_vscode: openInVscode,
    workspace: workspaceDir
  };
}

/**
 * Run terminal command with proper CWD management
 * Supports: npm, pip, git, mkdir, cd chains, etc.
 * 
 * Examples:
 *   npm create vite@latest my-app -- --template react-ts
 *   pip install requests pandas
 *   git clone https://github.com/user/repo
 */
async function runTerminalCommand(command, cwd = '') {
  if (!command) {
    throw new Error('command is required');
  }
  
  // Resolve working directory
  let workDir = cwd;
  if (!workDir) {
    workDir = path.join(process.cwd(), 'jarvis_temp_workspace');
    await fs.mkdir(workDir, { recursive: true });
  }
  
  console.log(`🖥️  Terminal: ${command} (cwd: ${workDir})`);
  
  // Use execAsync for commands that need shell features (npm, pip, git, etc.)
  // These are trusted commands from LLM, not user raw input
  const { stdout, stderr } = await execAsync(command, {
    cwd: workDir,
    timeout: 120000,  // 2 minutes for installs
    env: {
      ...process.env,
      PATH: `/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin:${process.env.PATH || ''}`
    }
  });
  
  return {
    success: true,
    command,
    cwd: workDir,
    stdout: stdout.trim(),
    stderr: stderr.trim()
  };
}

async function createScript(filename, content) {
  await fs.writeFile(filename, content, { mode: 0o755 });
  return { created: filename, executable: true };
}

async function runScript(scriptPath) {
  const { stdout, stderr } = await execAsync(`bash ${scriptPath}`);
  return {
    stdout: stdout.trim(),
    stderr: stderr.trim(),
    script: scriptPath
  };
}

// ============================================================================
// FILE SYSTEM FUNCTIONS
// ============================================================================

async function createFile(filePath, content = '') {
  try {
    await fs.writeFile(filePath, content, 'utf8');
    return { success: true, created: filePath };
  } catch (err) {
    return { success: false, error: `Başarısız: ${err.message}` };
  }
}

async function deleteFile(filePath) {
  try {
    await fs.unlink(filePath);
    return { success: true, deleted: filePath };
  } catch (err) {
    return { success: false, error: `Başarısız: ${err.message}` };
  }
}

async function listFiles(dirPath) {
  try {
    const files = await fs.readdir(dirPath);
    return { success: true, files, count: files.length, path: dirPath };
  } catch (err) {
    return { success: false, error: `Başarısız: ${err.message}` };
  }
}

async function searchFiles(dirPath, pattern) {
  const result = await safeExec(`find "${dirPath}" -name "${pattern}" 2>/dev/null`);
  if (!result.success) return result;
  const files = result.stdout.split('\n').filter(Boolean);
  return { success: true, files, count: files.length, pattern };
}

async function getFileInfo(filePath) {
  try {
    const stats = await fs.stat(filePath);
    return {
      success: true, path: filePath, size: stats.size,
      created: stats.birthtime, modified: stats.mtime,
      isDirectory: stats.isDirectory(), isFile: stats.isFile()
    };
  } catch (err) {
    return { success: false, error: `Başarısız: ${err.message}` };
  }
}

async function findLargeFiles(dirPath, minSize = 100 * 1024 * 1024) {
  const result = await safeExec(`find "${dirPath}" -type f -size +${minSize}c 2>/dev/null`);
  if (!result.success) return result;
  const files = result.stdout.split('\n').filter(Boolean);
  return { success: true, files, count: files.length, minSize };
}

async function createFolder(dirPath) {
  try {
    await fs.mkdir(dirPath, { recursive: true });
    return { success: true, created: dirPath };
  } catch (err) {
    return { success: false, error: `Başarısız: ${err.message}` };
  }
}

// ============================================================================
// BROWSER FUNCTIONS (Enhanced with Playwright)
// ============================================================================

let browser = null;
let browserContext = null;

async function initBrowser() {
  if (!browser) {
    try {
      const { chromium } = require('playwright');
      browser = await chromium.launch({ headless: false });
      browserContext = await browser.newContext();
      console.log('✓ Browser initialized');
    } catch (error) {
      console.error('Browser initialization failed:', error.message);
      throw error;
    }
  }
  return browserContext;
}

async function closeBrowser() {
  if (browser) {
    await browser.close();
    browser = null;
    browserContext = null;
    console.log('✓ Browser closed');
  }
}

async function openURL(url) {
  try {
    const context = await initBrowser();
    const page = await context.newPage();
    await page.goto(url, { waitUntil: 'networkidle' });
    return { opened: url, success: true };
  } catch (error) {
    // Fallback to system browser
    if (IS_MAC) {
      await execAsync(`open "${url}"`);
    } else if (IS_WINDOWS) {
      await execAsync(`start "${url}"`);
    } else {
      await execAsync(`xdg-open "${url}"`);
    }
    return { opened: url, success: true, method: 'system' };
  }
}

async function webSearch(query) {
  const searchURL = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
  return await openURL(searchURL);
}

async function takeScreenshot(savePath = 'screenshot.png') {
  try {
    const context = await initBrowser();
    const pages = context.pages();
    
    if (pages.length > 0) {
      await pages[0].screenshot({ path: savePath, fullPage: true });
      return { screenshot: savePath, success: true };
    }
  } catch (error) {
    // Fallback to system screenshot
    if (IS_MAC) {
      await execAsync(`screencapture ${savePath}`);
      return { screenshot: savePath, success: true, method: 'system' };
    }
  }
  
  throw new Error('Screenshot failed');
}

// NEW: Browser automation actions
async function navigateTo(url) {
  const context = await initBrowser();
  const page = await context.newPage();
  await page.goto(url, { waitUntil: 'networkidle' });
  return { navigated: url, title: await page.title() };
}

async function fillForm(formData) {
  const context = await initBrowser();
  const pages = context.pages();
  
  if (pages.length === 0) {
    throw new Error('No active page');
  }
  
  const page = pages[0];
  
  for (const [selector, value] of Object.entries(formData)) {
    await page.fill(selector, value);
  }
  
  return { filled: Object.keys(formData).length };
}

async function clickElement(selector) {
  const context = await initBrowser();
  const pages = context.pages();
  
  if (pages.length === 0) {
    throw new Error('No active page');
  }
  
  const page = pages[0];
  await page.click(selector);
  
  return { clicked: selector };
}

async function getText(selector) {
  const context = await initBrowser();
  const pages = context.pages();
  
  if (pages.length === 0) {
    throw new Error('No active page');
  }
  
  const page = pages[0];
  const text = await page.textContent(selector);
  
  return { selector, text };
}

async function getPageContent() {
  const context = await initBrowser();
  const pages = context.pages();
  
  if (pages.length === 0) {
    throw new Error('No active page');
  }
  
  const page = pages[0];
  const content = await page.content();
  const title = await page.title();
  const url = page.url();
  
  return { url, title, content: content.substring(0, 5000) }; // Limit content
}

async function waitForElement(selector, timeout = 5000) {
  const context = await initBrowser();
  const pages = context.pages();
  
  if (pages.length === 0) {
    throw new Error('No active page');
  }
  
  const page = pages[0];
  await page.waitForSelector(selector, { timeout });
  
  return { found: selector };
}

async function executeScript(script) {
  const context = await initBrowser();
  const pages = context.pages();
  
  if (pages.length === 0) {
    throw new Error('No active page');
  }
  
  const page = pages[0];
  const result = await page.evaluate(script);
  
  return { result };
}

// ============================================================================
// START SERVER
// ============================================================================

app.listen(PORT, () => {
  console.log(`🛠️  JARVIS Tool Server v2.0.0`);
  console.log(`📡 Listening on http://localhost:${PORT}`);
  console.log(`🖥️  Platform: ${process.platform}`);
  console.log(`✅ Ready for actions!`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('🛑 SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('🛑 SIGINT received, shutting down gracefully');
  process.exit(0);
});
