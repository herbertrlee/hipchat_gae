import datetime as dt
import json
import logging

import requests
from requests.auth import HTTPBasicAuth

from google.appengine.ext import ndb


class AccessToken(ndb.Model):
    token = ndb.StringProperty()
    expiration = ndb.DateTimeProperty()

    @property
    def is_expired(self):
        return self.expiration < dt.datetime.utcnow()


class Installation(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    room_id = ndb.IntegerProperty(required=True)
    group_id = ndb.IntegerProperty(required=True)
    oauth_secret = ndb.StringProperty(required=True)
    token_url = ndb.StringProperty(required=True)
    api_url = ndb.StringProperty(required=True)
    access_token_obj = ndb.StructuredProperty(AccessToken)

    @property
    def access_token(self):
        if not self.access_token_obj or self.access_token_obj.is_expired:
            self.refresh_access_token()
        return self.access_token_obj.token

    @property
    def oauth_id(self):
        return self.key.id()

    @property
    def headers(self):
        return {
            "Authorization": "Bearer %s" % self.access_token,
            "Content-Type": "application/json"
        }

    @property
    def notification_url(self):
        return "{api_url}room/{room_id}/notification".format(api_url=self.api_url, room_id=self.room_id)

    def refresh_access_token(self):
        access_token_dict = requests.post(
            self.token_url,
            data={"grant_type": "client_credentials"},
            auth=HTTPBasicAuth(username=self.oauth_id, password=self.oauth_secret)
        ).json()

        self.access_token_obj = AccessToken(
            token=access_token_dict['access_token'],
            expiration=dt.datetime.utcnow() + dt.timedelta(seconds=access_token_dict['expires_in'] - 60)
        )

        self.put()

    def send_notification(self, payload):
        logging.info("Making notification call to %s", self.notification_url)
        response = requests.post(self.notification_url, data=json.dumps(payload), headers=self.headers)
        logging.info("API call returned with status code %d", response.status_code)
        logging.debug(response.content)
