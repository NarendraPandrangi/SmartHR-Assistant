const fs = require('fs');
const path = require('path');

const backendUrl = process.env.BACKEND_URL;

if (!backendUrl) {
    console.log("No BACKEND_URL provided, skipping injection.");
    process.exit(0);
}

// Since Vercel is running this inside the frontend/ directory, app.js is right next to it.
const file = path.join(__dirname, 'app.js');
let content = fs.readFileSync(file, 'utf8');

content = content.replace('{BACKEND_URL_INJECT}', backendUrl);

fs.writeFileSync(file, content);
console.log(`Successfully injected BACKEND_URL: ${backendUrl} into app.js`);
