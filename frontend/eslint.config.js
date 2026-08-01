import js from '@eslint/js';

export default [
  {
    ignores: ['node_modules/', 'dist/', 'build/', '.vscode/', '.saydeploy/'],
  },
  js.configs.recommended,
];
