module.exports = {
    apps: [
      {
        name: 'prodatinha', 
        script: 'prodatinha.py', 
        interpreter: 'python3', 
        cwd: '/repo/prodatinha',
        watch: false, 
        autorestart: false,
        ignore_watch: ['node_modules', 'logs', '.git', '.vscode'],
      },
    ],
  };