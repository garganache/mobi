// Test script to verify frontend routing and upload fixes

// Test 1: Verify backend API routes are correct
console.log('Testing backend API routes...');

const routes = [
    { method: 'GET', path: '/health', expected: 200 },
    { method: 'POST', path: '/api/analyze-step', expected: 422 }, // Validation error without proper data
    { method: 'POST', path: '/api/description', expected: 400 }, // Bad request without proper data
    { method: 'GET', path: '/api/description/latest', expected: 404 }, // Not found initially
    { method: 'GET', path: '/api/image-analyses', expected: 200 },
];

async function testRoute(method, path, expectedStatus) {
    try {
        const response = await fetch(`http://localhost:8000${path}`, {
            method,
            headers: method === 'POST' ? { 'Content-Type': 'application/json' } : {},
            body: method === 'POST' ? JSON.stringify({}) : undefined
        });
        
        if (response.status === expectedStatus) {
            console.log(`✅ ${method} ${path} -> ${response.status} (expected ${expectedStatus})`);
            return true;
        } else {
            console.log(`❌ ${method} ${path} -> ${response.status} (expected ${expectedStatus})`);
            return false;
        }
    } catch (error) {
        console.log(`❌ ${method} ${path} -> ERROR: ${error.message}`);
        return false;
    }
}

async function runTests() {
    let passed = 0;
    let total = routes.length;
    
    for (const route of routes) {
        if (await testRoute(route.method, route.path, route.expected)) {
            passed++;
        }
    }
    
    console.log(`\nBackend API Tests: ${passed}/${total} passed`);
    
    if (passed === total) {
        console.log('✅ All backend routing fixes are working correctly!');
    } else {
        console.log('❌ Some backend routing tests failed.');
    }
}

// Run tests if this script is executed directly
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { runTests };
} else {
    runTests().catch(console.error);
}