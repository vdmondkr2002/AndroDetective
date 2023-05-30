import sqlite3
import datetime
import xmltodict
import urllib.parse
import requests
import json
import re

from scripts.artifacts.api_key import key
from scripts.artifact_report import ArtifactHtmlReport
from scripts.funcs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly,does_column_exist_in_db,media_to_html

def get_Whatsapp(files_found, report_folder, seeker, wrap_text):

    source_file_msg = ''
    source_file_wa = ''
    whatsapp_msgstore_db = ''
    whatsapp_wa_db = ''
    
    for file_found in files_found:
        
        file_name = str(file_found)
        if file_name.endswith('msgstore.db'):
           whatsapp_msgstore_db = str(file_found)
           source_file_msg = file_found.replace(seeker.directory, '')

        if file_name.endswith('wa.db'):
           whatsapp_wa_db = str(file_found)
           source_file_wa = file_found.replace(seeker.directory, '')

    db = open_sqlite_db_readonly(whatsapp_msgstore_db)
    cursor = db.cursor()
    try:
        cursor.execute('''
        SELECT case CL.video_call when 1 then "Video Call" else "Audio Call" end as call_type, 
               CL.timestamp/1000 as start_time, 
               ((cl.timestamp/1000) + CL.duration) as end_time, 
               case CL.from_me when 0 then "Incoming" else "Outgoing" end as call_direction,
		       J1.raw_string AS from_id,
                            group_concat(J.raw_string) AS group_members
                     FROM   call_log_participant_v2 AS CLP
                            JOIN call_log AS CL
                              ON CL._id = CLP.call_log_row_id
                            JOIN jid AS J
                              ON J._id = CLP.jid_row_id
                            JOIN jid as J1
                              ON J1._id = CL.jid_row_id
                            GROUP  BY CL._id
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('Whatsapp - Group Call Logs')
        # logfunc(str(all_rows))
        report.start_artifact_report(report_folder, 'Whatsapp - Group Call Logs')
        report.add_script()
        data_headers = ('Start Time', 'End Time','Call Type', 'Call Direction', 'From ID', 'Group Members') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            starttime = datetime.datetime.fromtimestamp(int(row[1])).strftime('%Y-%m-%d %H:%M:%S')
            endtime = datetime.datetime.fromtimestamp(int(row[2])).strftime('%Y-%m-%d %H:%M:%S')
            data_list.append(( starttime, endtime, row[0], row[3], row[4], row[5]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Whatsapp - Group Call Logs'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_msg)

        tlactivity = f'Whatsapp - Group Call Logs'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Whatsapp Group Call Logs found')
        
    try:        
        cursor.execute('''
                     SELECT CL.timestamp/1000 as start_time, 
                            case CL.video_call when 1 then "Video Call" else "Audio Call" end as call_type, 
                            ((CL.timestamp/1000) + CL.duration) as end_time, 
                            J.raw_string AS num, 
                            case CL.from_me when 0 then "Incoming" else "Outgoing" end as call_direction
                     FROM   call_log AS CL 
                            JOIN jid AS J 
                              ON J._id = CL.jid_row_id 
                     WHERE  CL._id NOT IN (SELECT DISTINCT call_log_row_id 
                                           FROM   call_log_participant_v2) 
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('Whatsapp - Single Call Logs')
        report.start_artifact_report(report_folder, 'Whatsapp - Single Call Logs')
        report.add_script()
        data_headers = ('Start Time','Call Type','End Time','Number','Call Direction') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        # logfunc(str(all_rows))
        for row in all_rows:
            starttime = datetime.datetime.fromtimestamp(int(row[0])).strftime('%Y-%m-%d %H:%M:%S')
            endtime = datetime.datetime.fromtimestamp(int(row[2])).strftime('%Y-%m-%d %H:%M:%S')
            data_list.append((starttime, row[1], endtime, row[3], row[4]))
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Whatsapp - Single Call Logs'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_msg)
        
        tlactivity = f'Whatsapp - Single Call Logs'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Whatsapp Single Call Log available')
            
    cursor.execute('''attach database "''' + whatsapp_wa_db + '''" as wadb ''')
    
        
    if does_column_exist_in_db(db, 'messages', 'data'):
        
        try:
            cursor.execute('''
            SELECT 
            datetime(messages.timestamp/1000,'unixepoch') AS message_timestamp, 
            case messages.received_timestamp
                WHEN 0 THEN ''
                ELSE datetime(messages.received_timestamp/1000,'unixepoch')
            end as received_timestamp,
            messages.key_remote_jid AS id, 
            case 
            when contact_book_w_groups.recipients is null then messages.key_remote_jid
            else contact_book_w_groups.recipients
            end as recipients, 
            case key_from_me
                WHEN 0 THEN "Incoming"
                WHEN 1 THEN "Outgoing"
            end AS direction, 
            messages.data            AS content, 
            case 
                when messages.remote_resource is null then messages.key_remote_jid 
                else messages.remote_resource
            end AS group_sender,
            messages.media_url       AS attachment
            FROM   (SELECT jid, 
            recipients 
            FROM   wadb.wa_contacts AS contacts 
            left join (SELECT gjid, 
            Group_concat(CASE 
            WHEN jid == "" THEN NULL 
            ELSE jid 
            END) AS recipients 
            FROM   group_participants 
            GROUP  BY gjid) AS groups 
            ON contacts.jid = groups.gjid 
            GROUP  BY jid) AS contact_book_w_groups 
            join messages 
            ON messages.key_remote_jid = contact_book_w_groups.jid
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        except:
            usageentries = 0
            
        if usageentries > 0:
            report = ArtifactHtmlReport('WhatsApp - Messages')
            report.start_artifact_report(report_folder, 'WhatsApp - Messages')
            report.add_script()
            data_headers = ('Message Timestamp', 'Received Timestamp','Message ID','Recipients', 'Direction', 'Message', 'Group Sender', 'Attachment') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
                
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'WhatsApp - Messages'
            tsv(report_folder, data_headers, data_list, tsvname, source_file_msg)
            
            tlactivity = f'WhatsApp - Messages'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No WhatsApp - Messages data available')
            
        db.close()
    
    #Looks for newly changed column names
    else:
        logfunc("In message part")
        logfunc(whatsapp_wa_db)
        try:
            cursor.execute('''
            SELECT
            CASE
			WHEN message.timestamp = 0 then ''
			ELSE
			datetime(message.timestamp/1000,'unixepoch')
			END AS "Message Time",
            CASE
            WHEN message.received_timestamp = 0 then ''
            ELSE
            datetime(message.received_timestamp/1000,'unixepoch')
            END AS "Time Message Received",
            wadb.wa_contacts.wa_name AS "Other Participant WA User Name",
            CASE
            WHEN message.from_me=0 THEN wadb.wa_contacts.jid
            ELSE "" 
            END AS "Sending Party JID",
            CASE
            WHEN message.from_me=0 THEN "Incoming"
            WHEN message.from_me=1 THEN "Outgoing"
            END AS "Message Direction",
            CASE
            WHEN message.message_type=0 THEN "Text"
            WHEN message.message_type=1 THEN "Picture"
            WHEN message.message_type=2 THEN "Audio"
            WHEN message.message_type=3 THEN "Video"
            WHEN message.message_type=5 THEN "Static Location"
            WHEN message.message_type=7 THEN "System Message"
            WHEN message.message_type=9 THEN "Document"
            WHEN message.message_type=16 THEN "Live Location"
            ELSE message.message_type
            END AS "Message Type",
            message.text_data AS "Message",
            message_media.file_path AS "Local Path to Media",
            message_media.file_size AS "Media File Size",
            message_location.latitude AS "Shared Latitude/Starting Latitude (Live Location)",
            message_location.longitude AS "Shared Longitude/Starting Longitude (Live Location)",
            message_location.live_location_share_duration AS "Duration Live Location Shared (Seconds)",
            message_location.live_location_final_latitude AS "Final Live Latitude",
            message_location.live_location_final_longitude AS "Final Live Longitude",
            datetime(message_location.live_location_final_timestamp/1000,'unixepoch') AS "Final Location Timestamp"
            FROM
            message
            JOIN chat ON chat._id=message.chat_row_id
            JOIN jid ON jid._id=chat.jid_row_id
            LEFT JOIN message_media ON message_media.message_row_id=message._id
            LEFT JOIN message_location ON message_location.message_row_id=message._id
            JOIN wadb.wa_contacts ON wadb.wa_contacts.jid=jid.raw_string
            WHERE message.recipient_count=0
            ORDER BY "Message Time" ASC
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        except:
            usageentries = 0
            
        if usageentries > 0:
            report = ArtifactHtmlReport('WhatsApp - One To One Messages')
            report.start_artifact_report(report_folder, 'WhatsApp - One To One Messages')
            report.add_script()
            data_headers = ('Message Timestamp','Received Timestamp','Other Participant WA User Name','Sending Party JID','Message Direction','Message Type','Message','Suspicious','Malware', 'Phishing', 'Risk Score','Media','Local Path To Media','Media File Size','Shared Latitude/Starting Latitude (Live Location)','Shared Longitude/Starting Longitude (Live Location)','Duration Live Location Shared (Seconds)','Final Live Latitude','Final Live Longitude','Final Location Timestamp') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
              
                if row[7] is not None:
                  mediaident = row[7].split(separator)[-1]
                  print(mediaident)
                  media = media_to_html(mediaident, files_found, report_folder)
                else:
                  media = row[7]
                text_data = row[6]
                url=""
                try:
                    url = re.search("(?P<url>https?://[^\s]+)", text_data).group("url")
                except:
                    url=""
                suspicious = False
                malware = False
                phishing = False
                risk_score = 0
                logfunc(url)
                if url!="":
                    parsed_link = urllib.parse.quote(url, safe='')
                    api = "https://ipqualityscore.com/api/json/url/" + key + "/" + parsed_link
                    response = requests.get(api)
                    response_json = json.loads(response.content)
                    suspicious = response_json.get('suspicious', "")
                    malware = response_json.get('malware', "")
                    phishing = response_json.get('phishing', "")
                    risk_score = response_json.get('risk_score', "")
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6],suspicious, malware, phishing, risk_score, media, row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14]))

            report.write_artifact_data_table(data_headers, data_list, whatsapp_msgstore_db, html_no_escape=['Media'])
            report.end_artifact_report()
            
            tsvname = f'WhatsApp - One To One Messages'
            tsv(report_folder, data_headers, data_list, tsvname, whatsapp_msgstore_db)

            tlactivity = f'WhatsApp - One To One Messages'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No WhatsApp - One To One Messages found')

    db.close()

    db = open_sqlite_db_readonly(whatsapp_wa_db)
    cursor = db.cursor()
    try:
        cursor.execute('''
                     SELECT jid, 
                            CASE 
                              WHEN WC.number IS NULL THEN WC.jid 
                              WHEN WC.number == "" THEN WC.jid 
                              ELSE WC.number 
                            END number, 
                            CASE 
                              WHEN WC.given_name IS NULL 
                                   AND WC.family_name IS NULL 
                                   AND WC.display_name IS NULL THEN WC.jid 
                              WHEN WC.given_name IS NULL 
                                   AND WC.family_name IS NULL THEN WC.display_name 
                              WHEN WC.given_name IS NULL THEN WC.family_name 
                              WHEN WC.family_name IS NULL THEN WC.given_name 
                              ELSE WC.given_name 
                                   || " " 
                                   || WC.family_name 
                            END name 
                     FROM   wa_contacts AS WC
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('Whatsapp - Contacts')
        report.start_artifact_report(report_folder, 'Whatsapp - Contacts')
        report.add_script()
        data_headers = ('Number','Name') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        # logfunc(str(all_rows))
        for row in all_rows:
            data_list.append((row[1], row[2]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Whatsapp - Contacts'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_wa)

    else:
        logfunc('No Whatsapp Contacts found')

    db.close

    for file_found in files_found:
        if('com.whatsapp_preferences_light.xml' in file_found):
            with open(file_found, encoding='utf-8') as fd:
                xml_dict = xmltodict.parse(fd.read())
                string_dict = xml_dict.get('map','').get('string','')
                data = []
                # for i in range(len(string_dict)):
                #     logfunc(str(string_dict[i]))
                for i in range(len(string_dict)):
                    # if(string_dict[i]['@name'] == 'push_name'):                 # User Profile Name
                    #     data.append(string_dict[i]['#text'])
                    if(string_dict[i]['@name'] == 'my_current_status'):         # User Current Status
                        data.append(string_dict[i]['#text'])
                    # if(string_dict[i]['@name'] == 'version'):                   # User current whatsapp version
                    #     data.append(string_dict[i]['#text'])
                    if(string_dict[i]['@name'] == 'ph'):                        # User Mobile Number
                        data.append(string_dict[i]['#text'])
                    if(string_dict[i]['@name'] == 'cc'):                        # User country code
                        data.append(string_dict[i]['#text'])
                # logfunc(str(data))
                if(len(data)>0):
                    report = ArtifactHtmlReport('Whatsapp - User Profile')
                    report.start_artifact_report(report_folder,'Whatsapp - User Profile')
                    report.add_script()
                    # data_headers = ('Version', 'Name', 'User Status', 'Country Code', 'Mobile Number')
                    data_headers = {'User Status','Country Code','Mobile Number'}
                    data_list = []
                    # data_list.append((data[1], data[4], data[2], data[3], data[0]))
                    data_list.append((data[1],data[2],data[0]))
                    report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                    report.end_artifact_report()

                    tsvname = "Whatsapp - User Profile"
                    tsv(report_folder, data_headers, data_list,tsvname)

                    tlactivity = "Whatsapp - User Profile"
                    timeline(report_folder, tlactivity, data_list, data_headers)
                else:
                    logfunc("No Whatsapp - Profile data found")
    return
