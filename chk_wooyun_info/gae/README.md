

## How to deploy?
prerequisites:
- sign-up for an account on google application engine (GAE): http://appengine.google.com/
- download and install the Google App Engine SDK
- internet connection from your PC

## how to install cron-tab application:
- unpack all files included in cron-tab.zip into a specific local directory, e.g 'myapp'
- change the file app.yaml: set the application to your app_id
- upload all files from 'myapp' to google application engine server: appcfg.py update myapp

