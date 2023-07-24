module.exports = {
    apps: [
      {
        name: 'prodatinha', 
        script: 'prodatinha.py', 
        interpreter: 'python3', 
        cwd: '/repo/prodatinha',
        watch: true, 
        autorestart: false,
        max_restarts: 10, 
        ignore_watch: ['node_modules', 'logs', '.git', '.vscode'],
        env: {
        },
      },
    ],
  };