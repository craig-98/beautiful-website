# Deployment Instructions for Render.com

This document outlines the steps to deploy your Flask app on Render.com, a modern cloud platform that simplifies deployment with managed services.

## 1. Create a Render Account

- Go to https://render.com and sign up for a free account.

## 2. Prepare Your Flask App for Deployment

- Ensure your app has a `requirements.txt` file listing all dependencies.
- Ensure your app listens on the port provided by the environment variable `PORT` (Render sets this automatically).
- Example in `app.py`:

```python
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
```

## 3. Push Your Code to a Git Repository

- Push your project to GitHub, GitLab, or Bitbucket.

## 4. Create a New Web Service on Render

- Click "New" > "Web Service".
- Connect your Git repository.
- Select the branch to deploy.
- Set the build command: `pip install -r requirements.txt`
- Set the start command: `gunicorn app:app`
- Choose the instance type (free tier available).

## 5. Environment Variables

- Add any required environment variables in the Render dashboard.

## 6. Deploy

- Click "Create Web Service".
- Render will build and deploy your app.
- Your app will be available at the provided Render URL.

## 7. Additional Configuration

- Set up custom domains and HTTPS in Render dashboard if needed.
- Configure automatic deploys on git push.

---

If you want, I can help you create the `requirements.txt` file or modify your app to be compatible with Render deployment.
