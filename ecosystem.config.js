module.exports = {
    apps: [
      {
        name: 'prodatinha', 
        script: 'app.js',
        args: 'run dev', 
        instances: 1,
        interpreter: 'python3', 
        cwd: '/opt/docker/repo/disponibilizar_arquivos',
        watch: true, 
        autorestart: false,
        max_restarts: 10, 
        max_memory_restart: '1G',,
    ],
  };