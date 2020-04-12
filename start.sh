export FLASK_SECRET=219237111451840798711512131094837773769
export REPOSI_GITHUB_CLIENT_ID=41262c068df26f834ee4
export REPOSI_GITHUB_SECRET=687fd01f94cdcb392fdf81273860b08f8ba8caf8
export FLASK_HOST=https://reposi.0cdn.me
export GITHUB_TOKEN=da4b012350401dcae21eb58b7b3f8d824feb7abb
/usr/local/bin/gunicorn --certfile=reposi.crt --keyfile=reposi.key --bind 0.0.0.0:443 app:app
