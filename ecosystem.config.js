module.exports = {
    apps: [
      {
        name: 'prodatinha', 
        script: 'prodatinha.py', 
        interpreter: 'python3', 
        cwd: '/repo/prodatinha',
        watch: false, 
        autorestart: false,
        max_memory_restart: '200M',
        env: {
          PYTHONPATH: '/repo/prodatinha',
        },
        ignore_watch: ['logs', '.git', '.vscode'],
      },
    ],
  };