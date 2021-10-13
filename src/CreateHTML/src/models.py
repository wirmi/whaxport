import time


class Message:
    def __init__(self, received_timestamp, remote_resource, key_from_me, data, media_caption, media_wa_type, sender, media_path):
        self.received_timestamp = received_timestamp
        self.remote_resource = remote_resource
        self.key_from_me = key_from_me
        self.data = data
        self.media_caption = media_caption
        self.media_wa_type = media_wa_type
        self.received_timestamp_str = Message.__timestamp_to_str(received_timestamp)
        self.sender = sender
        self.media_path = media_path

    @staticmethod
    def __timestamp_to_str(timestamp: str) -> str:
        ts = int(timestamp) / 1000.0
        return time.strftime('%d.%m.%Y %H:%M', time.localtime(ts))

    def get_content(self) -> str:
        if self.media_wa_type == '0':
            return self.data
        media_caption = self.media_caption
        media_path = self.media_path
        if self.media_caption is None:
            media_caption = ""

        if(media_caption != ""):
            media_caption += "<br/><br/>"

        if self.media_wa_type == '1': # IMAGE
            return f'{media_caption}<a class="img" href="{media_path}" target="_blank"><img src="{media_path}"" style="max-width:600px;max-height:600px;"></a>'

        elif self.media_wa_type == '2': # AUDIO

            return f"{media_caption}<audio controls><source src='{media_path}'>Your browser does not support the audio element.</audio>"
        elif self.media_wa_type == '3': # VIDEO
            return f"{media_caption}<video width='100%' controls><source src='{media_path}'>Your browser does not support the video tag.</video>"
        elif self.media_wa_type == '4':
            return "<b>Contacto</b>"
        elif self.media_wa_type == '5' or self.media_wa_type == '16':
            return "<b>Ubicación</b>"
        elif self.media_wa_type == '8':
            return "<b>Llamada</b>"
        elif self.media_wa_type == '10':
            return "<b>Llamada perdida</b>"
        elif self.media_wa_type == '13':
            return "<b>Gif</b>"
        elif self.media_wa_type == '15':
            return "<i>Se eliminó este mensaje</i>"
        elif self.media_wa_type == '20':
            return "<b>Sticker</b>"
        else:
            return f"[MEDIA] ({media_path}) {media_caption}"

    def get_sender_name(self) -> str:
        if self.sender:
            return self.sender
        elif self.remote_resource:
            return self.remote_resource.split("@")[0]
        else:
            return self.remote_resource

    def __str__(self):
        if self.key_from_me:
            return f"> {self.received_timestamp_str} - {self.get_content()}"
        else:
            return f"< {self.received_timestamp_str} - {self.get_content()}"


class Chat:
    def __init__(self, key_remote_jid, subject: str, sort_timestamp, name: str, messages: list):
        self.key_remote_jid = key_remote_jid
        self.subject = subject
        self.sort_timestamp = sort_timestamp
        self.name = name
        self.phone_number = key_remote_jid.split("@")[0]
        self.title = self.__get_chat_title()
        self.messages = messages

    def __str__(self):
        return str(self.key_remote_jid) + " " + str(self.title)

    def __get_chat_title(self):
        if self.subject is not None:
            return self.subject
        elif self.name is not None:
            return self.name
        else:
            return self.phone_number
