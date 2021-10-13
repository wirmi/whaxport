import configparser
import sqlite3
from sqlite3 import Connection
from typing import List, Optional, Dict

import exporter
from models import Message, Chat

from sys import argv


def query_messages(con: Connection, key_remote_jid: str, contacts: Dict[str, Optional[str]]) -> List[Message]:
    cur = con.cursor()
    query = """
            SELECT _id, received_timestamp, remote_resource, key_from_me, data, media_caption, media_wa_type, media_hash 
            FROM messages 
            WHERE key_remote_jid =:key_remote_jid
            ORDER BY max(receipt_server_timestamp, received_timestamp)"""

    messages = []

    execute = cur.execute(query, {"key_remote_jid": key_remote_jid}).fetchall()

    for _id, received_timestamp, remote_resource, key_from_me, data, media_caption, media_wa_type, media_hash in execute:
        if(media_wa_type != '0' and media_hash != None):
            cur.execute(f'select file_path from message_media where file_hash = "{media_hash}"')
            media_path = cur.fetchall()[0][0]
        else:
            media_path = None

        messages.append(
            Message(received_timestamp, remote_resource, key_from_me, data, media_caption, media_wa_type, contacts.get(remote_resource, None), media_path)
        )
    return messages


def query_all_chats(db_path: str, contact: Dict[str, Optional[str]]) -> List[Chat]:
    chats = []
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    query = f"SELECT raw_string_jid as key_remote_jid, subject, sort_timestamp FROM chat_view WHERE sort_timestamp IS NOT NULL AND key_remote_jid = '{list(contact.keys())[0]}' ORDER BY sort_timestamp DESC"
    for key_remote_jid, subject, sort_timestamp in cur.execute(query):
        chats.append(
            Chat(key_remote_jid, subject, sort_timestamp, contact.get(key_remote_jid, None), query_messages(con, key_remote_jid, contact))
        )
    con.close()
    return chats


def main():
    print("### WhatsApp Database Exporter ###")

    config = configparser.ConfigParser()
    config.read("config.cfg")

    contact = {}
    contact[argv[1]] = argv[2]

    database = argv[3]

    export_path = argv[4] + "index.html"


    chats = query_all_chats(database, contact)

    print("[+] Exporting to HTML")
    exporter.chats_to_html(chats, export_path)

    print("[+] Finished")


if __name__ == "__main__":
    main()
