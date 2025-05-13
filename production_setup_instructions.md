# Production Deployment Setup for Flask App

This document outlines the steps to deploy your Flask app in a production-ready environment using Gunicorn and Nginx.

## 1. Install Gunicorn

Gunicorn is a production WSGI server for Python.

```bash
pip install gunicorn
```

## 2. Run Flask App with Gunicorn

From your project directory, run:

```bash
gunicorn -w 4 -b 127.0.0.1:8000 app:app
```

- `-w 4` runs 4 worker processes.
- `-b` binds to localhost on port 8000.
- `app:app` assumes your Flask app instance is named `app` in `app.py`.

## 3. Install and Configure Nginx

- Install Nginx on your server.
- Create a server block configuration to proxy requests to Gunicorn.

Example Nginx config (`/etc/nginx/sites-available/yourapp`):

```
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/your/project/static/;
    }
}
```

- Enable the site and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/yourapp /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

## 4. Environment Variables and Debug Mode

- Set `FLASK_ENV=production` or unset it.
- Ensure `app.run(debug=True)` is disabled or removed in `app.py`.

## 5. Security and Optimization

- Use HTTPS with SSL certificates (e.g., via Let's Encrypt).
- Configure firewall rules.
- Optimize static assets.
- Set up logging and monitoring.

---

If you want, I can help you create scripts or configuration files for this setup.
