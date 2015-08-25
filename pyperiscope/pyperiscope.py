# -*- coding: utf-8 -*-
import requests
import re
import json
import os
import subprocess as sp
from PIL import Image
import datetime


class PeriscopeAPI(object):
    """
    Wrapper Class for the Periscope API
    """
    ###############################################
    ############## HELPER FUNCTIONS ###############
    ###############################################

    def __http_response(self, url, method, request={}, print_flag=True):
        """
        Helper to do something with http response

        Input:
        url - url for the http request
        method - 'GET' or 'POST' for type of HTTP request
        request - json request object with input parameters - required for POST
        (optional) print_flag - print json result to stdout (default=True)

        Output:
        Response result as a tuple of (response status code, response url, JSON object).
        """

        try:
            if method == 'POST':
                res = requests.post(url, json=request)
            elif method == 'GET':
                res = requests.get(url)
            elif method == 'POST form':
                res = requests.post(url, files=request)
            else:
                print 'Please use either GET or POST for the method'
            if res:
                print 'Response was a success with code: %d and url: %s' % (res.status_code, res.url)
            if print_flag and res.status_code != 401:
                print json.dumps(res.json()['result'], indent=4, separators=(', ', ': '))
            return (res.status_code, res.url, res.json()['result'])
        except requests.exceptions.RequestException as e:
            print(e)
            return (res.status_code, res.url, {})


    ###############################################
    ########## INITIALIZATION FUNCTION ############
    ###############################################

    def __init__(self,
                twitter_un, twitter_user_id,
                twitter_consumer_key, twitter_consumer_secret,
                periscope_user_id,
                periscope_consumer_key, periscope_consumer_secret):
        """
        Initialize the API using the Twitter and Periscope credentials of the user

        Inputs:
        twitter_un - Twitter username
        twitter_user_id - Twitter user id
        twitter_consumer_key - Twitter consumer key from API
        twitter_consumer_secret - Twitter consumer secret from API
        periscope_user_id - Periscope user id
        periscope_consumer_key - Periscope consumer key from API
        periscope_consumer_secret - Periscope consumer secret from API
        """
        self.build = 'v1.0.2'

        self.twitter_un = twitter_un
        self.twitter_user_id = twitter_user_id

        self.twitter_consumer_key = twitter_consumer_key
        self.twitter_consumer_secret = twitter_consumer_secret

        self.periscope_user_id = periscope_user_id
        self.periscope_key = periscope_consumer_key
        self.periscope_secret = periscope_consumer_secret


    ###############################################
    ########### IMPLEMENTED ENDPOINTS #############
    ###############################################

    def login_twitter(self, print_flag=True):
        """
        POST https://api.periscope.tv/api/v2/loginTwitter?build=v1.0.2

        Output:
        (response status code, response url, JSON object)

        JSON object format:
        {
            "cookie": "<a_value_used_for_authenticating_further_requests>",
            "settings": {
                "auto_save_to_camera": false,
                "push_new_follower": false
            },
            "suggested_username": "",
            "user": {
                "class_name": "User",
                "created_at": "2015-04-14T12:35:43.249931849-07:00",
                "description": "",
                "display_name": "Testing",
                "id": "<integer_user_id>",
                "initials": "",
                "is_beta_user": false,
                "is_employee": false,
                "is_twitter_verified": false,
                "n_broadcasts": 0,
                "n_followers": 0,
                "n_following": 1,
                "profile_image_urls": [
                    {
                        "height": 128,
                        "ssl_url": "https://abs.twimg.com/sticky/default_profile_images/default_profile_1_reasonably_small.png",
                        "url": "http://abs.twimg.com/sticky/default_profile_images/default_profile_1_reasonably_small.png",
                        "width": 128
                    },
                    {
                        "height": 200,
                        "ssl_url": "https://abs.twimg.com/sticky/default_profile_images/default_profile_1_200x200.png",
                        "url": "http://abs.twimg.com/sticky/default_profile_images/default_profile_1_200x200.png",
                        "width": 200
                    },
                    {
                        "height": 400,
                        "ssl_url": "https://abs.twimg.com/sticky/default_profile_images/default_profile_1_400x400.png",
                        "url": "http://abs.twimg.com/sticky/default_profile_images/default_profile_1_400x400.png",
                        "width": 400
                    }
                ],
                "twitter_screen_name": "<twitter_screen_name>",
                "updated_at": "2015-04-14T12:35:57.046371902-07:00",
                "username": "<periscope_user_name>"
            }
        }
        """
        url = 'https://api.periscope.tv/api/v2/loginTwitter?build=%s' % self.build
        method = 'POST'
        request = {
            'bundle_id': "com.bountylabs.periscope",
            'phone_number': '',
            'session_key': self.twitter_consumer_key,
            'session_secret': self.twitter_consumer_secret,
            'user_id': self.twitter_user_id,
            'user_name': self.twitter_un,
            'vendor_id': "81EA8A9B-2950-40CD-9365-40535404DDE4"
        }
        return self.__http_response(url, method, request=request, print_flag=print_flag)

    def create_broadcast(self, twitter_cookie, print_flag=True):
        """
        POST https://api.periscope.tv/api/v2/createBroadcast?build=v1.0.2

        Input:
        twitter_cookie - cookie returned from login_twitter JSON obj (see above)
        (optional) location - {lat:lat, long:long} default = {}

        Output:
        (response status code, response url, JSON object)

        JSON object format:
        {
            "application": "liveorigin",
            "auth_token": "<pubnub_auth_token>",
            "broadcast": {
                "Application": "liveorigin",
                "Host": "ec2-52-4-220-111.compute-1.amazonaws.com",
                "OriginId": "i90be606d",
                "Region": "us-east-1",
                "available_for_replay": false,
                "city": "Kings",
                "class_name": "Broadcast",
                "country": "",
                "country_state": "New York",
                "created_at": "2015-04-14T17:24:41.265499812-07:00",
                "featured": false,
                "friend_chat": false,
                "has_location": false,
                "height": 568,
                "hidden": false,
                "id": "<integer_broadcast_id>",
                "image_url": "<s3_url_to_put_thumbnail_to>",
                "image_url_small": "<s3_url_to_put_downsized_thumbnail_to>",,
                "ip_lat": 0.0,    // location latitude
                "ip_lng": -20.0,  // location longitude
                "is_locked": false,
                "iso_code": "",
                "lock": null,
                "profile_image_url": "http://abs.twimg.com/sticky/default_profile_images/default_profile_1_reasonably_small.png",
                "state": "NOT_STARTED",
                "status": "",
                "stream_name": "<string_representing_RTMP_stream_name>",
                "updated_at": "2015-04-14T17:24:41.265499812-07:00",
                "user_display_name": "Testing",
                "user_id": "<periscope_user_id>",
                "width": 320
            },
            "can_share_twitter": true,
            "channel": "<pubnub_channel_name>",
            "credential": "<string_used_as_RTMP_streaming_credential>",
            "host": "ec2-52-4-220-111.compute-1.amazonaws.com", // host to stream RTMP to
            "participant_index": 0,
            "port": 80,
            "private_port": 443,
            "private_protocol": "RTMPS",
            "protocol": "RTMP",
            "publisher": "<pubnub_publisher_key>",
            "read_only": false,
            "signer_token": "<string_including_credential_value>",
            "stream_name": "<same_as_channel_name>",
            "subscriber": "<pubnub_subscriber_key>",
            "thumbnail_upload_url": "<s3_thumbnail_upload_url>",
            "upload_url": "<s3_video_replay_url>"
        }
        """
        url = 'https://api.periscope.tv/api/v2/createBroadcast?build=%s' % self.build
        method = 'POST'
        request = {
            'cookie': twitter_cookie,
            'height': 568,  # video height
            'lat': 0.0,     # current location latitude
            'lng': -20.0,   # current location longitude
            'width': 320    # video width
        }
        if location != {}:
            request['lat'] = location['lat']
            request['lng'] = location['lng']
        return self.__http_response(url, method, request=request, print_flag=print_flag)

    def get_broadcast_share_url(self, broadcast_id, twitter_cookie, print_flag=True):
        """
        POST https://api.periscope.tv/api/v2/getBroadcastShareURL?build=v1.0.

        Input:
        broadcast_id - from create_broadcast result (see above)
        twitter_cookie - cookie returned from login_twitter JSON obj (see above)

        Output:
        (response status code, response url, JSON object)

        JSON object format:
        {
            "url": "https://www.periscope.tv/w/<long_string>" // Public video URL that can be visited in a browser
        }
        """
        url = 'https://api.periscope.tv/api/v2/getBroadcastShareURL?build=%s' % self.build
        method = 'POST'
        request = {
            'broadcast_id': broadcast_id,
            'cookie': twitter_cookie
        }
        return self.__http_response(url, method, request=request, print_flag=print_flag)

    def publish_broadcast(self, broadcast_id, twitter_cookie, print_flag=True):
        """
        POST https://api.periscope.tv/api/v2/publishBroadcast?build=v1.0.2

        Input:
        broadcast_id - from create_broadcast result (see above)
        twitter_cookie - cookie returned from login_twitter JSON obj (see above)
        (optional) location - {lat=lat, long=long} default = {}
        (optional) friend_chat - default = False
        (optional) status - default = ""

        Output:
        (response status code, response url, JSON object)

        JSON object format:
        {
            "success": true
        }
        """
        url = 'https://api.periscope.tv/api/v2/publishBroadcast?build=%s' % self.build
        method = 'POST'
        request = {
            'broadcast_id': broadcast_id,
            'cookie': twitter_cookie,
            'friend_chat': friend_chat,
            'status': status
        }
        if location == {}:
            request['has_location'] = False
        else:
            request['has_location'] = True
            request['lat'] = location['lat']
            request['long'] = location['long']
        return self.__http_response(url, method, request=request, print_flag=print_flag)

    def broadcast_meta(self, broadcast_id, twitter_cookie, print_flag=True):
        """
        POST https://api.periscope.tv/api/v2/broadcastMeta?build=v1.0.2

        Input:
        broadcast_id - from create_broadcast result (see above)
        twitter_cookie - cookie returned from login_twitter JSON obj (see above)

        Output:
        (response status code, response url, JSON object)

        JSON object format:
        {
            "success": true
        }
        """
        url = 'https://api.periscope.tv/api/v2/broadcastMeta?build=%s' % self.build
        method = 'POST'
        request = {
            'broadcast_id': broadcast_id,
            'cookie': twitter_cookie,
            'stats': {
                'BatteryDrainPerMinute': 0,
                'TransmitOK': True,
                'UploadRate_max': 458,
                'UploadRate_mean': 432,
                'UploadRate_min': 406,
                'UploadRate_stddev': 36.76955262170047,
                'VideoIndexRatio_max': 133.7396760459014,
                'VideoIndexRatio_mean': 104.5064813303835,
                'VideoIndexRatio_min': 86.44113275958026,
                'VideoIndexRatio_stddev': 11.66700863607694,
                'VideoOK': True,
                'VideoOutputRate_max': 534.9587041836056,
                'VideoOutputRate_mean': 418.0259253215341,
                'VideoOutputRate_min': 345.764531038321,
                'VideoOutputRate_stddev': 46.66803454430801,
                'pn_connect_t': 0.2213719,
                'pn_msg_fail': 0,
                'pn_msg_received': 5,
                'pn_msg_sent': 0,
                'pn_prs_received': 1,
                'pn_subscribe_t': 0.839077
            }
        }
        return self.__http_response(url, method, request=request, print_flag=print_flag)

    def end_broadcast(self, broadcast_id, twitter_cookie, print_flag=True):
        """
        POST https://api.periscope.tv/api/v2/endBroadcast?build=v1.0.2

        Input:
        broadcast_id - from create_broadcast result (see above)
        twitter_cookie - cookie returned from login_twitter JSON obj (see above)

        Output:
        (response status code, response url, JSON object)

        JSON object format:
        {
            "broadcast": {
                "AbuseDate": null,
                "AbuseReporter": "",
                "AbuseStatus": "",
                "Application": "liveorigin",
                "Host": "ec2-52-4-220-111.compute-1.amazonaws.com",
                "NAbuseReports": 0,
                "OriginId": "i90be606d",
                "Region": "us-east-1",
                "available_for_replay": false,
                "city": "Kings",
                "class_name": "Broadcast",
                "country": "",
                "country_state": "New York",
                "created_at": "2015-04-14T17:24:41.265499812-07:00",
                "end": "2015-04-14T17:25:01.674845856-07:00",
                "featured": false,
                "friend_chat": false,
                "has_location": true,
                "height": 568,
                "hidden": false,
                "id": "4656494",
                "image_url": "<thumbnail_url>",
                "image_url_small": "<small_thumbnail_url>",
                "ip_lat": 0.0,
                "ip_lng": -20.0,
                "is_locked": false,
                "iso_code": "",
                "join_time_average": 0,
                "join_time_count": 0,
                "lock": null,
                "lost_before_end": 0,
                "n_comments": 0,
                "n_hearts": 0,
                "n_replay_hearts": 0,
                "n_replay_watched": 0,
                "n_watched": 0,
                "n_watching": 0,
                "n_watching_web": 0,
                "n_web_watched": 0,
                "profile_image_url": "http://abs.twimg.com/sticky/default_profile_images/default_profile_1_reasonably_small.png",
                "start": "2015-04-14T17:24:46.518208519-07:00",
                "state": "ENDED",
                "status": "",
                "stream_name": "<stream_name_from_createBroadcast>",
                "updated_at": "2015-04-14T17:25:01.674845856-07:00",
                "user_display_name": "Testing",
                "user_id": "<periscope_user_id>",
                "watched_time": 0,
                "watched_time_calculated": 0,
                "watched_time_implied": 0,
                "width": 320
            }
        }
        """
        url = 'https://api.periscope.tv/api/v2/endBroadcast?build=%s' % self.build
        method = 'POST form'
        files = {
            'broadcast_id': broadcast_id,
            'coookie': twitter_cookie
        }
        return self.__http_response(url, method, request=files, print_flag=print_flag)


    ###############################################
    ###### UNIMPLEMENTED/UNSURE ENDPOINTS #########
    ###############################################

    ### GET https://api.periscope.tv/api/v2/getAccessPublic

    ### GET token=aKvpYTg4NjM4NzB8NjkzNjc5NjnflJhV3spm07GjDsJsS7knEkD8WbccqdNowhn6cfvRhQ%3D%3D

    ### POST https://api.periscope.tv/api/v2/application/<broadcast_id>

    ### GET https://api.periscope.tv/api/v2/getBroadcasts

    def follow_broadcast_feed(self):
        """
        POST https://api.periscope.tv/api/v2/followingBroadcastFeed?build=v1.0.2
        """
        raise NotImplementedError('To be implemented')

    def suggested_people(self):
        """
        POST https://api.periscope.tv/api/v2/suggestedPeople?build=v1.0.2
        """
        raise NotImplementedError('To be implemented')

    def featured_broadcasts(self):
        """
        POST https://api.periscope.tv/api/v2/featuredBroadcastFeed?build=v1.0.2
        """
        raise NotImplementedError('To be implemented')

    def upload_padding(self):
        """
        POST https://api.periscope.tv/api/v2/uploadPadding?build=v1.0.2
        """
        raise NotImplementedError('To be implemented')

    def get_broadcast_viewers(self, broadcast_id):
        """
        POST https://api.periscope.tv/api/v2/getBroadcastViewers?build=v1.0.2
        """
        raise NotImplementedError('To be implemented')

    def replay_upload(self, broadcast_id):
        """
        POST https://api.periscope.tv/api/v2/replayUploaded?build=v1.0.2
        """
        raise NotImplementedError('To be implemented')