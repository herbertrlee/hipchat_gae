## hipchat_gae
A very basic [Hipchat](https://www.hipchat.com/) integration that can be launched quickly on Google App Engine.  This repository is intended as a starting point for people who want to do Hipchat integration development, but find the official Hipchat documentation for doing so to be lacking.

## Before You Begin
You should be somewhat familiar with [Google App Engine](https://cloud.google.com/appengine/) and [Flask](http://flask.pocoo.org/), and have glanced over the [HipChat Integration documentation](https://developer.atlassian.com/hipchat/guide)

## Prerequisites
There are a few things you'll need to have ready.

### Set up a HipChat room
If you don't already have one, create a HipChat room that you have administrative rights on.

### Set up a Google Cloud Project
Go to the [Google Cloud Console](https://console.cloud.google.com) and create a Google Cloud Project.

### Install the Google Cloud SDK
You'll need the [Google Cloud SDK](https://cloud.google.com/sdk/) and the gcloud command-line utility in order develop for GAE and to deploy the integration.

## Deploying to GAE
Deploying the integration to GAE works just like any other GAE deployment.  Once you've cloned the repository, go to the repository folder and enter the following:

`gcloud app deploy app.yaml`

You may need to auth and set your project ID with gcloud before it will let you do this.  The deployment will take a minute or so.  Once the deployment has completed, go to:

`https://<YOUR_PROJECT_ID>.appspot.com/capabilities`

You should see something that looks like this:

````
{
  "name": "Hipchat GAE Sample Integration",
  "description": "A basic Hipchat integration built on Google App Engine using Flask.",
  "key": "{{ project_id }}",
  "links": {
      "homepage": "https://<YOUR_PROJECT_ID>.appspot.com",
      "self": "https://<YOUR_PROJECT_ID>.appspot.com/capabilities"
  },
  "capabilities": {
    "installable": {
        "allowGlobal": false,
        "allowRoom": true,
        "callbackUrl": "https://<YOUR_PROJECT_ID>.appspot.com/installed",
        "uninstalledUrl": "https://<YOUR_PROJECT_ID>.appspot.com/uninstalled"
      },
      "hipchatApiConsumer": {
          "fromName": "Hipchat GAE Sample Integration",
          "scopes": [
              "send_notification",
              "view_messages"
          ]
      },
      "webhook": [
        {
          "url": "https://<YOUR_PROJECT_ID>.appspot.com/echo",
          "pattern": "^/[eE][cC][hH][oO]",
          "event": "room_message",
          "name": "echo"
        }
      ]
  }
}
````

This is the capabilities document.  HipChat will access it every time your integration is installed.

## Connecting your integration to HipChat
Now that your integration is up and serving, it's time to connect it to your room.  Go to your room addons page.  It should look something like this:

`https://<YOUR_SERVER>.hipchat.com/addons/?room=<YOUR_ROOM_ID>`

Scroll all the way down to the bottom of the page.  You should see a link that says, "Install an integration from a descriptor URL".  Click it, and it should open a modal that tells you to enter your capabilities URL.  Paste the URL from the previous step into this box.  Click 'Agree' a few more times, and you should end up on the add-on page for the Hipchat GAE Sample Integration.

### Testing the HipChat integration
The sample integration is very simple.  It only has one feature - it listens to your HipChat room for messages of the following format:

`/echo message`

When a message that starts with `/echo` is heard, HipChat will send a POST to `https://<YOUR_PROJECT_ID>.appspot.com/echo`.  The integration will then strip the `/echo` from the message and send a notification back to the room with the rest of the message.

To test this integration, then, type `/echo hello world` into your room.  You should see `hello world` come back from the Hipchat GAE Sample Integration user.

That's it!  You've successfully deployed and connected your HipChat integration.

## Uninstalling
To uninstall your integration, go to the room addons page, click into the Hipchat GAE Sample Integration page, and hit the Remove button. 

## API Endpoints
At this point, if you haven't yet, it would be a good idea to read through the HipChat integration docs, especially the [server-side installation flow section](https://developer.atlassian.com/hipchat/guide/installation-flow/server-side-installation#Server-sideinstallation-Installationflow).

### /capabilities
The capabilities endpoint is fairly simple.  It returns a capabilities JSON document that describes the integration and what it can do.  During the installation process, HipChat will make a GET to this endpoint, which will serve the capabilities.json file from the templates folder, with your Google project ID injected into the file.

### /installed
The `/installed` endpoint is a callback.  If you look at the capabilities JSON, you'll notice that this endpoint is registered in the `installable` object as the `callbackUrl`.  After retrieving the capabilities document, HipChat will make a POST to this endpoint with the oauth credentials for this installation.  The endpoint saves these credentials to the Google Cloud Datastore.

### /uninstalled
Similarly to the `/installed` endpoint, the `/uninstalled` endpoint is also a callback, and is also registered in the capabilities JSON.  When the end user removes their installation of your integration, HipChat will post to this endpoint.  This endpoint then removes the oauth credentials for this installation and performs any other necessary cleanup.

### /echo
The `/echo` endpoint is registered in the capabilities document as a [webhook](https://developer.atlassian.com/hipchat/guide/webhooks).  Whenever a message is sent to the room that matches the pattern specified in the capabilities doc, HipChat will make a post to this endpoint.  In this case, the endpoint is relatively simple - it strips the leading `/echo` from the message and sends a notification back to the room containing the message.

## Adding your own features
Now that you've got an idea of how this all works, you can start adding in your own features.  This is a pretty simple process - any webhooks you want to add should be registered in the capabilities document, and the endpoints should be added to the Flask app.

One caveat to be aware of is that you will need to uninstall and reinstall your integration on HipChat in order for new webhooks to show up.  You can modify existing endpoints without doing this, but HipChat won't refresh the capabilities doc (and won't know about new webhooks) without an uninstall/reinstall.

I hope this has helped you!  Please contact me if you have questions with the setup.
