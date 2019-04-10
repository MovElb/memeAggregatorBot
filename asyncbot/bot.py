import json
from .graph_api import FacebookGraphApi
from requests_toolbelt import MultipartEncoder


class Bot(FacebookGraphApi):

    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)

    async def send_text_message(self, recipient_id, message):
        '''Send text messages to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/text-message
        Input:
            recipient_id: recipient id to send to
            message: message to send
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': {
                'id': recipient_id
            },
            'message': {
                'text': message
            }
        }
        return await self.send_raw(payload)

    async def send_message(self, recipient_id, message):
        '''Send text messages to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/text-message
        Input:
            recipient_id: recipient id to send to
            message: raw message to send
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': {
                'id': recipient_id
            },
            'message': message
        }
        return await self.send_raw(payload)

    async def send_generic_message(self, recipient_id, elements):
        '''Send generic messages to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/generic-template
        Input:
            recipient_id: recipient id to send to
            elements: generic message elements to send
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': {
                'id': recipient_id
            },
            'message': {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": elements
                    }
                }
            }
        }
        return await self.send_raw(payload)

    async def send_button_message(self, recipient_id, text, buttons):
        '''Send text messages to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/button-template
        Input:
            recipient_id: recipient id to send to
            text: text of message to send
            buttons: buttons to send
        Output:
            Response from API as <dict>
        '''

        payload = {
            'recipient': {
                'id': recipient_id
            },
            'message': {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": text,
                        "buttons": buttons
                    }
                }
            }
        }
        return await self.send_raw(payload)

    async def send_image(self, recipient_id, image_path):
        '''Send an image to the specified recipient.
        Image must be PNG or JPEG or GIF (more might be supported).
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/image-attachment
        Input:
            recipient_id: recipient id to send to
            image_path: path to image to be sent
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': json.dumps(
                {
                    'id': recipient_id
                }
            ),
            'message': json.dumps(
                {
                    'attachment': {
                        'type': 'image',
                        'payload': {}
                    }
                }
            ),
            'filedata': (image_path, open(image_path, 'rb'))
        }
        multipart_data = MultipartEncoder(payload)
        multipart_header = {
            'Content-Type': multipart_data.content_type
        }
        async with self.session.post(self.base_url, data=multipart_data, headers=multipart_header) as resp:
            return await resp.json()

    async def send_image_url(self, recipient_id, image_url):
        '''Send an image to specified recipient using URL.
        Image must be PNG or JPEG or GIF (more might be supported).
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/image-attachment
        Input:
            recipient_id: recipient id to send to
            image_url: url of image to be sent
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': json.dumps(
                {
                    'id': recipient_id
                }
            ),
            'message': json.dumps(
                {
                    'attachment': {
                        'type': 'image',
                        'payload': {
                            'url': image_url
                        }
                    }
                }
            )
        }
        return await self.send_raw(payload)

    async def send_action(self, recipient_id, action):
        '''Send typing indicators or send read receipts to the specified recipient.
        Image must be PNG or JPEG.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/sender-actions

        Input:
            recipient_id: recipient id to send to
            action: action type (mark_seen, typing_on, typing_off)
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': {
                'id': recipient_id
            },
            'sender_action': action
        }
        return await self.send_raw(payload)

    async def send_raw(self, payload):
        request_endpoint = '{0}/me/messages'.format(self.graph_url)
        async with self.session.post(request_endpoint, params=self.auth_args, json=payload) as resp:
            return await resp.json()

    async def send_audio(self, recipient_id, audio_path):
        '''Send audio to the specified recipient.
        Audio must be MP3 or WAV
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/audio-attachment
        Input:
            recipient_id: recipient id to send to
            audio_path: path to audio to be sent
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': json.dumps(
                {
                    'id': recipient_id
                }
            ),
            'message': json.dumps(
                {
                    'attachment': {
                        'type': 'audio',
                        'payload': {}
                    }
                }
            ),
            'filedata': (audio_path, open(audio_path, 'rb'))
        }
        multipart_data = MultipartEncoder(payload)
        multipart_header = {
            'Content-Type': multipart_data.content_type
        }
        async with self.session.post(self.base_url, data=multipart_data, headers=multipart_header) as resp:
            return await resp.json()

    async def send_audio_url(self, recipient_id, audio_url):
        '''Send audio to specified recipient using URL.
        Audio must be MP3 or WAV
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/audio-attachment
        Input:
            recipient_id: recipient id to send to
            audio_url: url of audio to be sent
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': json.dumps(
                {
                    'id': recipient_id
                }
            ),
            'message': json.dumps(
                {
                    'attachment': {
                        'type': 'audio',
                        'payload': {
                            'url': audio_url
                        }
                    }
                }
            )
        }
        return await self.send_raw(payload)

    async def send_video(self, recipient_id, video_path):
        '''Send video to the specified recipient.
        Video should be MP4 or MOV, but supports more (https://www.facebook.com/help/218673814818907).
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/video-attachment
        Input:
            recipient_id: recipient id to send to
            video_path: path to video to be sent
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': json.dumps(
                {
                    'id': recipient_id
                }
            ),
            'message': json.dumps(
                {
                    'attachment': {
                        'type': 'audio',
                        'payload': {}
                    }
                }
            ),
            'filedata': (video_path, open(video_path, 'rb'))
        }
        multipart_data = MultipartEncoder(payload)
        multipart_header = {
            'Content-Type': multipart_data.content_type
        }
        async with self.session.post(self.base_url, data=multipart_data, headers=multipart_header) as resp:
            return await resp.json()

    async def send_video_url(self, recipient_id, video_url):
        '''Send video to specified recipient using URL.
        Video should be MP4 or MOV, but supports more (https://www.facebook.com/help/218673814818907).
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/video-attachment
        Input:
            recipient_id: recipient id to send to
            video_url: url of video to be sent
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': json.dumps(
                {
                    'id': recipient_id
                }
            ),
            'message': json.dumps(
                {
                    'attachment': {
                        'type': 'audio',
                        'payload': {
                            'url': video_url
                        }
                    }
                }
            )
        }
        return await self.send_raw(payload)

    async def send_file(self, recipient_id, file_path):
        '''Send file to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/file-attachment
        Input:
            recipient_id: recipient id to send to
            file_path: path to file to be sent
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': json.dumps(
                {
                    'id': recipient_id
                }
            ),
            'message': json.dumps(
                {
                    'attachment': {
                        'type': 'file',
                        'payload': {}
                    }
                }
            ),
            'filedata': (file_path, open(file_path, 'rb'))
        }
        multipart_data = MultipartEncoder(payload)
        multipart_header = {
            'Content-Type': multipart_data.content_type
        }
        async with self.session.post(self.base_url, data=multipart_data, headers=multipart_header) as resp:
            return await resp.json()

    async def send_file_url(self, recipient_id, file_url):
        '''Send file to the specified recipient.
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/file-attachment
        Input:
            recipient_id: recipient id to send to
            file_url: url of file to be sent
        Output:
            Response from API as <dict>
        '''
        payload = {
            'recipient': json.dumps(
                {
                    'id': recipient_id
                }
            ),
            'message': json.dumps(
                {
                    'attachment': {
                        'type': 'file',
                        'payload': {
                            'url': file_url
                        }
                    }
                }
            )
        }
        return await self.send_raw(payload)
