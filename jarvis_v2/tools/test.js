#!/usr/bin/env node
/**
 * JARVIS Tool Server - Test Suite
 */

const BASE_URL = 'http://localhost:8002';

async function testAction(action, target, params = {}) {
  try {
    const response = await fetch(`${BASE_URL}/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, target, params })
    });

    const result = await response.json();
    console.log(`✓ ${action} (${target}):`, result.success ? 'SUCCESS' : 'FAILED');
    if (!result.success) {
      console.log(`  Error: ${result.error}`);
    }
    return result;
  } catch (error) {
    console.log(`✗ ${action} (${target}): ERROR - ${error.message}`);
    return { success: false, error: error.message };
  }
}

async function runTests() {
  console.log('🧪 JARVIS Tool Server - Test Suite');
  console.log('='.repeat(50));

  // Health check
  console.log('\n1. Health Check');
  try {
    const response = await fetch(`${BASE_URL}/health`);
    const health = await response.json();
    console.log('✓ Server is healthy:', health);
  } catch (error) {
    console.log('✗ Server is not responding');
    console.log('  Make sure to start the server first: npm start');
    process.exit(1);
  }

  // OS Control tests
  console.log('\n2. OS Control Tests');
  await testAction('get_volume', null);
  await testAction('get_system_info', null);

  // Browser tests
  console.log('\n3. Browser Tests');
  await testAction('open_url', 'https://www.google.com');
  await testAction('web_search', 'JARVIS AI assistant');

  // Security tests
  console.log('\n4. Security Tests (should fail)');
  await testAction('execute_command', 'rm -rf /');
  await testAction('execute_command', 'sudo reboot');

  // Safe command test
  console.log('\n5. Safe Command Test');
  await testAction('execute_command', 'echo "Hello JARVIS"');

  console.log('\n' + '='.repeat(50));
  console.log('✓ Test suite completed');
}

runTests().catch(console.error);
