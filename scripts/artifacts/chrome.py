import os
import textwrap
import urllib.parse
import requests
import json

from scripts.artifacts.api_key import key
from scripts.artifact_report import ArtifactHtmlReport
from scripts.funcs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly, does_column_exist_in_db

def get_browser_name(file_name):

    if 'brave' in file_name.lower():
        return 'Brave'
    elif 'microsoft' in file_name.lower():
        return 'Edge'
    elif 'opera' in file_name.lower():
        return 'Opera'
    elif 'android.chrome' in file_name.lower():
        return 'Chrome'
    else:
        return 'Unknown'

def get_chrome(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'History': # skip -journal and other files
            continue
        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'
        elif file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data??

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        
        #Web History
        cursor.execute('''
        SELECT
        datetime(last_visit_time/1000000 + (strftime('%s','1601-01-01')),'unixepoch') AS LastVisitDate,
        url AS URL,
        title AS Title,
        visit_count AS VisitCount,
        typed_count AS TypedCount,
        id AS ID,
        CASE hidden
            WHEN 0 THEN ''
            WHEN 1 THEN 'Yes'
        END as Hidden
        FROM urls  
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'{browser_name} - Web History')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{browser_name} - Web History.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('Last Visit Time','URL','Title','Visit Count', 'IP Address', 'Suspicious','Malware', 'Phishing', 'Risk Score')
            data_list = []
            for row in all_rows:
                parsed_link = urllib.parse.quote(row[1], safe='')
                api = "https://ipqualityscore.com/api/json/url/" + key + "/" + parsed_link
                response = requests.get(api)
                response_json = json.loads(response.content)
                ip_address = response_json.get('ip_address', "")
                suspicious = response_json.get('suspicious', "")
                malware = response_json.get('malware', "")
                phishing = response_json.get('phishing', "")
                risk_score = response_json.get('risk_score', "")
                if wrap_text:
                    data_list.append((row[0],textwrap.fill(row[1], width=30),row[2],row[3], ip_address, suspicious, malware, phishing, risk_score))
                else:
                    data_list.append((row[0],row[1],row[2],row[3], ip_address, suspicious, malware, phishing, risk_score))
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'{browser_name} - Web History'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'{browser_name} - Web History'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc(f'No {browser_name} - Web History data available')
       
     
        #Web Search    
        cursor.execute('''
        SELECT
            url,
            title,
            visit_count,
            datetime(last_visit_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
        FROM urls
        WHERE url like '%search?q=%'
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'{browser_name} - Search Terms')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{browser_name} - Search Terms.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('Last Visit Time','Search Term','URL', 'Title', 'Visit Count')
            data_list = []
            for row in all_rows:
                search = row[0].split('search?q=')[1].split('&')[0]
                search = urllib.parse.unquote(search).replace('+', ' ')
                if wrap_text:
                    data_list.append((row[3], search, (textwrap.fill(row[0], width=100)),row[1],row[2]))
                else:
                    data_list.append((row[3], search, row[0], row[1], row[2]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'{browser_name} - Search Terms'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'{browser_name} - Search Terms'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc(f'No {browser_name} - Search Terms data available')
            
        #Downloads
        # check for last_access_time column, an older version of chrome db (32) does not have it
        if does_column_exist_in_db(db, 'downloads', 'last_access_time') == True:
            last_access_time_query = '''
            CASE last_access_time 
                WHEN "0" 
                THEN "" 
                ELSE datetime(last_access_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
            END AS "Last Access Time"'''
        else:
            last_access_time_query = "'' as last_access_query"

        cursor.execute(f'''
        SELECT 
        CASE start_time  
            WHEN "0" 
            THEN "" 
            ELSE datetime(start_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
        END AS "Start Time", 
        CASE end_time 
            WHEN "0" 
            THEN "" 
            ELSE datetime(end_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
        END AS "End Time", 
        {last_access_time_query},
        tab_url, 
        target_path, 
        CASE state
            WHEN "0" THEN "In Progress"
            WHEN "1" THEN "Complete"
            WHEN "2" THEN "Canceled"
            WHEN "3" THEN "Interrupted"
            WHEN "4" THEN "Interrupted"
        END,
        CASE danger_type
            WHEN "0" THEN ""
            WHEN "1" THEN "Dangerous"
            WHEN "2" THEN "Dangerous URL"
            WHEN "3" THEN "Dangerous Content"
            WHEN "4" THEN "Content May Be Malicious"
            WHEN "5" THEN "Uncommon Content"
            WHEN "6" THEN "Dangerous But User Validated"
            WHEN "7" THEN "Dangerous Host"
            WHEN "8" THEN "Potentially Unwanted"
            WHEN "9" THEN "Allowlisted by Policy"
            WHEN "10" THEN "Pending Scan"
            WHEN "11" THEN "Blocked - Password Protected"
            WHEN "12" THEN "Blocked - Too Large"
            WHEN "13" THEN "Warning - Sensitive Content"
            WHEN "14" THEN "Blocked - Sensitive Content"
            WHEN "15" THEN "Safe - Deep Scanned"
            WHEN "16" THEN "Dangerous, But User Opened"
            WHEN "17" THEN "Prompt For Scanning"
            WHEN "18" THEN "Blocked - Unsupported Type"
        END,
        CASE interrupt_reason
            WHEN "0" THEN ""
            WHEN "1" THEN "File Error"
            WHEN "2" THEN "Access Denied"
            WHEN "3" THEN "Disk Full"
            WHEN "5" THEN "Path Too Long"
            WHEN "6" THEN "File Too Large"
            WHEN "7" THEN "Virus"
            WHEN "10" THEN "Temporary Problem"
            WHEN "11" THEN "Blocked"
            WHEN "12" THEN "Security Check Failed"
            WHEN "13" THEN "Resume Error"
            WHEN "20" THEN "Network Error"
            WHEN "21" THEN "Operation Timed Out"
            WHEN "22" THEN "Connection Lost"
            WHEN "23" THEN "Server Down"
            WHEN "30" THEN "Server Error"
            WHEN "31" THEN "Range Request Error"
            WHEN "32" THEN "Server Precondition Error"
            WHEN "33" THEN "Unable To Get File"
            WHEN "34" THEN "Server Unauthorized"
            WHEN "35" THEN "Server Certificate Problem"
            WHEN "36" THEN "Server Access Forbidden"
            WHEN "37" THEN "Server Unreachable"
            WHEN "38" THEN "Content Lenght Mismatch"
            WHEN "39" THEN "Cross Origin Redirect"
            WHEN "40" THEN "Canceled"
            WHEN "41" THEN "Browser Shutdown"
            WHEN "50" THEN "Browser Crashed"
        END,
        opened, 
        received_bytes, 
        total_bytes
        FROM downloads
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport(f'{browser_name} - Downloads')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{browser_name} - Downloads.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('Start Time','End Time','Last Access Time','URL','Target Path','State','Danger Type','Interrupt Reason','Opened?','Received Bytes','Total Bytes')
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'{browser_name} - Downloads'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'{browser_name} - Downloads'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc(f'No {browser_name} - Downloads data available')
        
        
        db.close()