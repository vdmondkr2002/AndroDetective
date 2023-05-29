import urllib.parse
import flask_restful
import validators
import requests
import json
import re

from scripts.artifacts.api_key import key
from scripts.artifact_report import ArtifactHtmlReport
from scripts.funcs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_messages(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('bugle_db'):
            continue # Skip all other files
        logfunc(file_found)
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(parts.timestamp/1000,'unixepoch') AS "Timestamp (UTC)",
        parts.content_type AS "Message Type",
        conversations.name AS "Other Participant/Conversation Name",
        participants.display_destination AS "Message Sender",
        parts.text AS "Message"
        FROM
        parts
        JOIN messages ON messages._id=parts.message_id
        JOIN participants ON participants._id=messages.sender_id
        JOIN conversations ON conversations._id=parts.conversation_id
        ORDER BY "Timestamp (UTC)" ASC
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Messages')
            report.start_artifact_report(report_folder, 'Messages')
            report.add_script()
            data_headers = ('Message Timestamp (UTC)','Message Type','Other Participant/Conversation Name','Message Sender','Message', 'Suspicious','Malware', 'Phishing', 'Risk Score') 
            data_list = []
            for row in all_rows:
                message_data = row[4]
                url=""
                try:
                    url = re.search("(?P<url>https?://[^\s]+)", message_data).group("url")
                except:
                    url=""
                suspicious = False
                malware = False
                phishing = False
                risk_score = 0
                if url!="":
                    parsed_link = urllib.parse.quote(url, safe='')
                    api = "https://ipqualityscore.com/api/json/url/" + key + "/" + parsed_link
                    response = requests.get(api)
                    response_json = json.loads(response.content)
                    suspicious = response_json.get('suspicious', "")
                    malware = response_json.get('malware', "")
                    phishing = response_json.get('phishing', "")
                    risk_score = response_json.get('risk_score', "")
                data_list.append((row[0],row[1],row[2],row[3],row[4], suspicious, malware, phishing, risk_score))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Messages'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Messages'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Messages data available')
        
        db.close()