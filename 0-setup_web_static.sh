#!/usr/bin/env bash
# Sets up a web server for the deployment of web_static

# Install Nginx if it is not already installed
if ! command -v nginx > /dev/null 2>&1; then
    apt-get -y update
    apt-get -y install nginx
fi

# Create the folder structure
mkdir -p /data/web_static/releases/test/ /data/web_static/shared/

# Create a fake HTML file to test the Nginx configuration
cat > /data/web_static/releases/test/index.html << 'HTML'
<html>
  <head>
  </head>
  <body>
    School
  </body>
</html>
HTML

# Recreate the symbolic link every time the script runs
rm -f /data/web_static/current
ln -s /data/web_static/releases/test /data/web_static/current

# Give ownership of /data/ to the ubuntu user and group
chown -R ubuntu:ubuntu /data/

# Serve /data/web_static/current/ at /hbnb_static (added only once)
config="/etc/nginx/sites-available/default"
if ! grep -q "location /hbnb_static" "$config"; then
    sed -i '0,/listen 80 default_server;/s//listen 80 default_server;\n\n\tlocation \/hbnb_static {\n\t\talias \/data\/web_static\/current\/;\n\t}/' "$config"
fi

service nginx restart

exit 0
