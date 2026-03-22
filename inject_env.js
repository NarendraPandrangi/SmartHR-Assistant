const fs = require('fs');

const backendUrl = process.env.BACKEND_URL;

if (!backendUrl) {
    console.log("No BACKEND_URL provided, skipping injection.");
    process.exit(0);
}

const file = 'frontend/app.js';
let content = fs.readFileSync(file, 'utf8');

content = content.replace('{BACKEND_URL_INJECT}', backendUrl);

fs.writeFileSync(file, content);
console.log(`Successfully injected BACKEND_URL: ${backendUrl} into app.js`);
