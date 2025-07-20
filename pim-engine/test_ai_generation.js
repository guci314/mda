const puppeteer = require('puppeteer');

async function testAIGeneration() {
    console.log('Starting AI code generation test with Puppeteer...');
    
    const browser = await puppeteer.launch({
        headless: false,  // Set to true for CI/CD
        slowMo: 100,      // Slow down actions for visibility
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    try {
        const page = await browser.newPage();
        
        // Set viewport
        await page.setViewport({ width: 1280, height: 800 });
        
        // 1. Navigate to models page
        console.log('1. Navigating to models page...');
        await page.goto('http://localhost:8001/models', { waitUntil: 'networkidle2' });
        
        // 2. Wait for page to load and refresh models
        console.log('2. Refreshing model list...');
        await page.waitForSelector('#refreshModels', { timeout: 5000 });
        await page.click('#refreshModels');
        await page.waitForTimeout(2000);
        
        // 3. Check if todo_management model is loaded
        console.log('3. Looking for todo_management model...');
        const modelExists = await page.evaluate(() => {
            const models = document.querySelectorAll('.model-item');
            for (const model of models) {
                if (model.textContent.includes('todo_management')) {
                    return true;
                }
            }
            return false;
        });
        
        if (!modelExists) {
            console.log('Model not found in list. Loading it...');
            // Click on load model if not present
            // This would require additional UI elements
        }
        
        // 4. Navigate to code generation section
        console.log('4. Selecting model for code generation...');
        await page.evaluate(() => {
            // Select the model in dropdown
            const select = document.querySelector('select[name="model"]');
            if (select) {
                for (let option of select.options) {
                    if (option.value === 'todo_management') {
                        select.value = 'todo_management';
                        select.dispatchEvent(new Event('change'));
                        break;
                    }
                }
            }
        });
        
        // 5. Select FastAPI as target platform
        console.log('5. Selecting FastAPI platform...');
        await page.evaluate(() => {
            const platformSelect = document.querySelector('select[name="platform"]');
            if (platformSelect) {
                platformSelect.value = 'fastapi';
                platformSelect.dispatchEvent(new Event('change'));
            }
        });
        
        // 6. Enable AI generation
        console.log('6. Enabling AI generation...');
        const aiCheckbox = await page.$('#llm-todo_management');
        if (aiCheckbox) {
            const isChecked = await page.evaluate(el => el.checked, aiCheckbox);
            if (!isChecked) {
                await aiCheckbox.click();
            }
        }
        
        // 7. Click generate code button
        console.log('7. Generating code with AI...');
        await page.click('#generateCode');
        
        // 8. Wait for generation to complete (AI takes longer)
        console.log('8. Waiting for AI generation (this may take 30-60 seconds)...');
        await page.waitForFunction(
            () => {
                const status = document.querySelector('.generation-status');
                return status && !status.textContent.includes('Generating');
            },
            { timeout: 120000 }  // 2 minutes timeout for AI
        );
        
        // 9. Check generation results
        console.log('9. Checking generation results...');
        const results = await page.evaluate(() => {
            const codeBlocks = document.querySelectorAll('pre code');
            const files = [];
            
            for (const block of codeBlocks) {
                const filename = block.getAttribute('data-filename') || 'unknown';
                const content = block.textContent;
                files.push({ filename, content });
            }
            
            return files;
        });
        
        // 10. Analyze the generated code
        console.log('10. Analyzing generated code...');
        console.log(`Generated ${results.length} files`);
        
        for (const file of results) {
            console.log(`\n--- File: ${file.filename} ---`);
            
            // Check for TODO placeholders (template generation)
            const hasTodos = file.content.includes('TODO');
            const hasNotImplemented = file.content.includes('NotImplementedError');
            
            // Check for AI-generated features
            const hasValidation = file.content.includes('validate') || file.content.includes('Validate');
            const hasErrorHandling = file.content.includes('try') || file.content.includes('except');
            const hasLogging = file.content.includes('logger') || file.content.includes('log');
            const hasDatabase = file.content.includes('db.') || file.content.includes('session.');
            
            console.log('Code quality indicators:');
            console.log(`  - Has TODOs: ${hasTodos ? '❌ (Template)' : '✅ (No TODOs)'}`);
            console.log(`  - Has NotImplementedError: ${hasNotImplemented ? '❌ (Template)' : '✅ (Implemented)'}`);
            console.log(`  - Has validation: ${hasValidation ? '✅' : '❌'}`);
            console.log(`  - Has error handling: ${hasErrorHandling ? '✅' : '❌'}`);
            console.log(`  - Has logging: ${hasLogging ? '✅' : '❌'}`);
            console.log(`  - Has database operations: ${hasDatabase ? '✅' : '❌'}`);
            
            // Show a snippet of the code
            const lines = file.content.split('\n').slice(0, 20);
            console.log('\nFirst 20 lines:');
            console.log(lines.join('\n'));
        }
        
        // 11. Take a screenshot of the results
        console.log('\n11. Taking screenshot...');
        await page.screenshot({ 
            path: 'ai_generation_result.png',
            fullPage: true 
        });
        
        console.log('\n✅ Test completed successfully!');
        console.log('Screenshot saved as: ai_generation_result.png');
        
    } catch (error) {
        console.error('❌ Test failed:', error);
        await page.screenshot({ path: 'error_screenshot.png' });
        throw error;
    } finally {
        await browser.close();
    }
}

// Run the test
testAIGeneration().catch(console.error);