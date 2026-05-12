import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const UI_DIR = path.resolve(__dirname, '../src/components/ui');
const REGISTRY_DIR = path.resolve(__dirname, '../registry');
const REGISTRY_UI_DIR = path.resolve(REGISTRY_DIR, 'ui');

// Ensure registry directories exist
if (!fs.existsSync(REGISTRY_DIR)) fs.mkdirSync(REGISTRY_DIR, { recursive: true });
if (!fs.existsSync(REGISTRY_UI_DIR)) fs.mkdirSync(REGISTRY_UI_DIR, { recursive: true });

// Build the components
const components = fs.readdirSync(UI_DIR).filter(file => file.endsWith('.tsx'));
const index = [];

for (const file of components) {
  const name = file.replace('.tsx', '');
  const content = fs.readFileSync(path.join(UI_DIR, file), 'utf-8');
  
  // Basic dependency detection (can be expanded)
  const dependencies = [];
  if (content.includes('@radix-ui/react-slot')) dependencies.push('@radix-ui/react-slot');
  if (content.includes('lucide-react')) dependencies.push('lucide-react');
  
  const registryItem = {
    name,
    type: 'registry:ui',
    dependencies,
    registryDependencies: [],
    files: [
      {
        path: `ui/${file}`,
        content,
        type: 'registry:ui',
        target: `components/ui/${file}`
      }
    ]
  };

  // Write individual component JSON
  fs.writeFileSync(
    path.join(REGISTRY_UI_DIR, `${name}.json`),
    JSON.stringify(registryItem, null, 2)
  );

  index.push({
    name,
    type: 'registry:ui',
    files: [`ui/${file}`],
    dependencies,
    registryDependencies: []
  });
}

// Write the main registry index.json
fs.writeFileSync(
  path.join(REGISTRY_DIR, 'index.json'),
  JSON.stringify(index, null, 2)
);

// Also package utils.ts and theme.css
const utilsContent = fs.readFileSync(path.resolve(__dirname, '../src/lib/utils.ts'), 'utf-8');
fs.writeFileSync(
  path.join(REGISTRY_DIR, 'utils.json'),
  JSON.stringify({
    name: 'utils',
    type: 'registry:lib',
    dependencies: ['clsx', 'tailwind-merge'],
    files: [{ path: 'lib/utils.ts', content: utilsContent, type: 'registry:lib' }]
  }, null, 2)
);

const themeContent = fs.readFileSync(path.resolve(__dirname, '../src/styles/theme.css'), 'utf-8');
fs.writeFileSync(
  path.join(REGISTRY_DIR, 'theme.json'),
  JSON.stringify({
    name: 'theme',
    type: 'registry:style',
    files: [{ path: 'styles/theme.css', content: themeContent, type: 'registry:style' }]
  }, null, 2)
);


console.log(`✅ Registry built successfully: ${components.length} UI components compiled.`);