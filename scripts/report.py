import html
import os
import pathlib
import shutil

from collections import OrderedDict
from scripts.html_parts import *
from scripts.funcs import *
from scripts.version_info import version

def get_icon_name(category, artifact):
    ''' Returns the icon name from the feathericons collection. To add an icon type for 
        an artifact, select one of the types from ones listed @ feathericons.com
        If no icon is available, the alert triangle is returned as default icon.
    '''
    category = category.upper()
    artifact = artifact.upper()
    icon = 'alert-triangle' # default (if not defined!)

    if category.find('ACCOUNT') >= 0:
        if artifact.find('AUTH') >= 0:  icon = 'key'
        else:                           icon = 'user'
    elif category == 'ADB HOSTS':       icon = 'terminal'
    elif category == 'AIRTAGS':       icon = 'map-pin'
    elif category == 'BURNER':
        if artifact.find('NUMBER INFORMATION') >= 0:         icon = 'user'
        elif artifact.find('COMMUNICATION INFORMATION') >= 0:           icon = 'message-circle'
    elif category == 'CALCULATOR LOCKER':       icon = 'lock'
    elif category == 'PLAYGROUND VAULT':       icon = 'lock'
    elif category == 'ENCRYPTING MEDIA APPS':       icon = 'lock'
    elif category == 'GOOGLE MAPS VOICE GUIDANCE': icon = 'map'
    elif category == 'GMAIL': icon = 'at-sign'
    elif category == 'APP INTERACTION': icon = 'bar-chart-2'
    elif category == 'PRIVACY DASHBOARD': icon = 'eye'
    elif category == 'BASH HISTORY':    icon = 'terminal'
    elif category == 'SETTINGS SERVICES':    
        if artifact.find('BATTERY') >=0:    icon = 'battery-charging'
    elif category == 'DEVICE HEALTH SERVICES':         
        if artifact.find('BLUETOOTH') >=0:  icon = 'bluetooth'
        elif artifact.find('BATTERY') >=0:  icon = 'battery-charging'
        else:                           icon = 'bar-chart-2'
    elif category == 'BLUETOOTH CONNECTIONS':       icon = 'bluetooth'
    elif category == 'CAST':            icon = 'cast'
    elif category == 'FITBIT':            icon = 'watch'
    elif category == 'CALL LOGS':       icon = 'phone'
    elif category == 'IMAGE MANAGER CACHE':       icon = 'image'
    elif category == 'CLIPBOARD':        icon = 'clipboard'
    elif category == 'CASH APP':        icon = 'credit-card'
    elif category == 'CHATS':           icon = 'message-circle'
    elif category == 'CHROMIUM':          
        if artifact.find('AUTOFILL') >= 0:        icon = 'edit-3'
        elif artifact.find('BOOKMARKS') >= 0:       icon = 'bookmark'
        elif artifact.find('DOWNLOADS') >= 0:       icon = 'download'
        elif artifact.find('LOGIN') >= 0:           icon = 'log-in'
        elif artifact.find('MEDIA HISTORY') >= 0:   icon = 'video'
        elif artifact.find('NETWORK ACTION PREDICTOR') >=0:    icon = 'type'
        elif artifact.find('OFFLINE PAGES') >= 0:   icon = 'cloud-off'
        elif artifact.find('SEARCH TERMS') >= 0:      icon = 'search'
        elif artifact.find('TOP SITES') >= 0:       icon = 'list'
        elif artifact.find('WEB VISITS') >= 0:      icon = 'globe'
        else:                                       icon = 'chrome'
    elif category == 'DEVICE INFO':     
        if artifact == 'BUILD INFO':                icon = 'terminal'
        elif artifact == 'PARTNER SETTINGS':        icon = 'settings'
        elif artifact.find('SETTINGS_SECURE_') >= 0: icon = 'settings'
        else:                                       icon = 'info'
    elif category == 'ETC HOSTS':       icon = 'globe'
    elif category == 'WIPE & SETUP':
        if artifact == 'FACTORY RESET':                  icon = 'loader'
        elif artifact == 'SUGGESTIONS.XML':                icon = 'loader'
        elif artifact == 'SETUP_WIZARD_INFO.XML':          icon = 'loader'
        elif artifact == 'APPOPS.XML':                     icon = 'loader'
        elif artifact == 'SAMSUNG WIPE HISTORY':           icon = 'trash-2'
        else:                                            icon = 'loader'
    elif category == 'EMULATED STORAGE METADATA':     icon = 'database'
    elif category == 'FACEBOOK MESSENGER':      icon = 'facebook'
    elif category == 'FIREFOX':
        if artifact.find('BOOKMARKS') >= 0:                 icon = 'bookmark'
        elif artifact.find('COOKIES') >= 0:                 icon = 'info'
        elif artifact.find('DOWNLOADS') >= 0:               icon = 'download'
        elif artifact.find('FORM HISTORY') >= 0:            icon = 'edit-3'
        elif artifact.find('PERMISSIONS') >= 0:             icon = 'sliders'
        elif artifact.find('RECENTLY CLOSED TABS') >= 0:    icon = 'x-square'
        elif artifact.find('SEARCH TERMS') >= 0:            icon = 'search'
        elif artifact.find('TOP SITES') >= 0:               icon = 'list'
        elif artifact.find('VISITS') >= 0:                  icon = 'globe'
        elif artifact.find('WEB HISTORY') >= 0:             icon = 'globe'
    elif category == 'GOOGLE CHAT':
        if artifact.find('GROUP INFORMATION') >= 0:         icon = 'users'
        elif artifact.find('CHAT MESSAGES') >= 0:           icon = 'message-circle'
    elif category == 'GOOGLE DRIVE':     icon = 'file'
    elif category == 'GOOGLE DUO':
        if artifact.find('CALL HISTORY') >= 0:      icon = 'phone-call'
        elif artifact.find('CONTACTS') >= 0:      icon = 'users'
        elif artifact.find('NOTES') >= 0:      icon = 'edit-3'
    elif category == 'GOOGLE FIT (GMS)':     icon = 'activity'           
    elif category == 'GOOGLE KEEP':     icon = 'list'
    elif category == 'TOR':     icon = 'globe'
    elif category == 'GBOARD KEYBOARD': icon = 'edit-3'
    elif category == 'GOOGLE NOW & QUICKSEARCH': icon = 'search'
    elif category == 'GOOGLE PHOTOS':
        if artifact.find('LOCAL TRASH') >=0:            icon = 'trash-2'
        elif artifact.find('BACKED UP FOLDER') >= 0:    icon = 'refresh-cw'
        else:                                           icon = 'image'
    elif category == 'MESSAGES':     icon = 'message-square'
    elif category == 'GOOGLE PLAY':     
        if artifact == 'GOOGLE PLAY SEARCHES':      icon = 'search'
        else:                                       icon = 'play'
    elif category == 'GOOGLE TASKS':     icon = 'list'
    elif category == 'GROUPME':
        if artifact.find('GROUP INFORMATION') >= 0:         icon = 'users'
        elif artifact.find('CHAT INFORMATION') >= 0:           icon = 'message-circle'
    elif category == 'HIDEX': icon = 'eye-off'
    elif category == 'INSTALLED APPS':  icon = 'package'
    elif category == 'MEDIA METADATA':  icon = 'file-plus'
    elif category == 'MEGA': icon = 'message-circle'
    elif category == 'MEWE':  icon = 'message-circle'
    elif category == 'NOW PLAYING':           icon = 'music'
    elif category == 'POWER EVENTS':
        if artifact.find('POWER OFF RESET'):    icon = 'power'
        elif artifact.find('LAST BOOT TIME'):          icon = 'power'
        elif artifact.find('SHUTDOWN CHECKPOINTS'):    icon = 'power'
    elif category == 'PROTONMAIL':
        if artifact.find('CONTACTS') >=0: icon = 'users'
        elif artifact.find('MESSAGES') >=0: icon = 'inbox'
        else:                           icon = 'mail'
    elif category == 'RCS CHATS':       icon = 'message-circle'
    elif category == 'RECENT ACTIVITY': icon = 'activity'
    elif category == 'SAMSUNG WEATHER CLOCK':
        if artifact.find('DAILY') >=0:            icon = 'sunrise'
        elif artifact.find('HOURLY') >=0:            icon = 'thermometer'
        else:                                          icon = 'sun'
    elif category == 'SAMSUNG_CMH':     icon = 'disc'
    elif category == 'SCRIPT LOGS':     icon = 'archive'
    elif category == 'SKOUT':
        if artifact == 'SKOUT MESSAGES':  icon = 'message-circle'
        if artifact == 'SKOUT USERS':  icon = 'users'
    elif category == 'TEAMS':
        if artifact == 'TEAMS MESSAGES':  icon = 'message-circle'
        elif artifact == 'TEAMS USERS':  icon = 'users'
        elif artifact == 'TEAMS CALL LOG':  icon = 'phone'
        elif artifact == 'TEAMS ACTIVITY FEED':  icon = 'at-sign'
        elif artifact == 'TEAMS FILE INFO':  icon = 'file'
        else:                           icon = 'file-text'
    elif category == 'VIBER':
        if artifact == 'VIBER - CONTACTS':  icon = 'user'
        if artifact == 'VIBER - MESSAGES':  icon = 'message-square'
        if artifact == 'VIBER - CALL LOGS':  icon = 'phone'
    elif category == 'SMS & MMS':       icon = 'message-square'
    elif category == 'SQLITE JOURNALING': icon = 'book-open'
    elif category == 'USAGE STATS':     icon = 'bar-chart-2'
    elif category == 'USER DICTIONARY': icon = 'book'
    elif category == 'WAZE': icon = 'navigation-2'
    elif category == 'WELLBEING' or category == 'WELLBEING ACCOUNT': 
        if artifact == 'ACCOUNT DATA':  icon = 'user'
        else:                           icon = 'layers'
    elif category == 'WIFI PROFILES':  icon = 'wifi'
    elif category == 'PERMISSIONS':  icon = 'check'
    elif category == 'APP ROLES':  icon = 'tool'
    elif category == 'LINE':
        if artifact == 'LINE - CONTACTS':  icon = 'user'
        if artifact == 'LINE - MESSAGES':  icon = 'message-square'
        if artifact == 'LINE - CALL LOGS':  icon = 'phone'
    elif category == 'IMO':
        if artifact == 'IMO - ACCOUNT ID':  icon = 'user'
        if artifact == 'IMO - MESSAGES':  icon = 'message-square'
    elif category == 'TANGO':
        if artifact == 'TANGO - MESSAGES':  icon = 'message-square'
    elif category == 'VLC':
        if artifact == 'VLC MEDIA LIST':  icon = 'film'
        if artifact == 'VLC THUMBNAILS':  icon = 'image'
    elif category == 'SNAPCHAT': icon = 'bell'
    elif category == 'SKYPE':
        if artifact == 'SKYPE - CALL LOGS':  icon = 'phone'
        if artifact == 'SKYPE - MESSAGES':  icon = 'message-square'
        if artifact == 'SKYPE - CONTACTS':  icon = 'user'
    elif category == 'TEXT NOW':
        if artifact == 'TEXT NOW - CALL LOGS':  icon = 'phone'
        if artifact == 'TEXT NOW - MESSAGES':  icon = 'message-square'
        if artifact == 'TEXT NOW - CONTACTS':  icon = 'user'
    elif category == 'TIKTOK':
        if artifact == 'TIKTOK - MESSAGES':  icon = 'message-square'
        if artifact == 'TIKTOK - CONTACTS':  icon = 'user'
    elif category == 'WHATSAPP':
        if artifact == 'WHATSAPP - MESSAGES':  icon = 'messages-square'
        if artifact == 'WHATSAPP - CONTACTS':  icon = 'user'
        else:                           icon = 'phone'
    elif category == 'CONTACTS':  icon = 'user'
    return icon

def generate_report(reportfolderbase, time_in_secs, time_HMS, extraction_type, image_input_path):
    control = None
    side_heading = \
    """<h6 class="sidebar-heading justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
        {0}
    </h6>
    """
    list_item = \
    """
    <li class="nav-item">
        <a class="nav-link {0}" href="{1}">
            <span data-feather="{2}"></span> {3}
        </a>
    </li>
    """
    # Populate the sidebar dynamic data (depends on data/files generated by parsers)
    # Start with the 'saved reports' (home) page link and then append elements
    nav_list_data = side_heading.format('Saved Reports') + list_item.format('', 'index.html', 'home', 'Report Home')
    # Get all files
    side_list = OrderedDict() # { Category1 : [path1, path2, ..], Cat2:[..] } Dictionary containing paths as values, key=category

    for root, _, files in sorted(os.walk(reportfolderbase)):
        files = sorted(files)
        for file in files:
            if file.endswith(".temphtml"):    
                fullpath = (os.path.join(root, file))
                _, tail = os.path.split(fullpath)
                p = pathlib.Path(fullpath)
                SectionHeader = (p.parts[-2])
                if SectionHeader == '_elements':
                    pass
                else:
                    if control == SectionHeader:
                        side_list[SectionHeader].append(fullpath)
                        icon = get_icon_name(SectionHeader, tail.replace(".temphtml", ""))
                        nav_list_data += list_item.format('', tail.replace(".temphtml", ".html"), icon, tail.replace(".temphtml", ""))
                    else:
                        control = SectionHeader
                        side_list[SectionHeader] = []
                        side_list[SectionHeader].append(fullpath)
                        nav_list_data += side_heading.format(SectionHeader)
                        icon = get_icon_name(SectionHeader, tail.replace(".temphtml", ""))
                        nav_list_data += list_item.format('', tail.replace(".temphtml", ".html"), icon, tail.replace(".temphtml", ""))

    # Now that we have all the file paths, start writing the files

    for path_list in side_list.values():
        for path in path_list:
            old_filename = os.path.basename(path)
            filename = old_filename.replace(".temphtml", ".html")
            # search for it in nav_list_data, then mark that one as 'active' tab
            active_nav_list_data = mark_item_active(nav_list_data, filename) + nav_bar_script
            artifact_data = get_file_content(path)

            # Now write out entire html page for artifact
            f = open(os.path.join(reportfolderbase, filename), 'w', encoding='utf8')
            artifact_data = insert_sidebar_code(artifact_data, active_nav_list_data, path)
            f.write(artifact_data)
            f.close()
            
            # Now delete .temphtml
            os.remove(path)
            # If dir is empty, delete it
            try:
                os.rmdir(os.path.dirname(path))
            except OSError:
                pass # Perhaps it was not empty!

    # Create index.html's page content
    create_index_html(reportfolderbase, time_in_secs, time_HMS, extraction_type, image_input_path, nav_list_data)
    elements_folder = os.path.join(reportfolderbase, '_elements')
    os.mkdir(elements_folder)
    __location__ = os.path.dirname(os.path.abspath(__file__))
    
    shutil.copy2(os.path.join(__location__,"dashboard.css"), elements_folder)
    shutil.copy2(os.path.join(__location__,"feather.min.js"), elements_folder)
    shutil.copytree(os.path.join(__location__,"MDB-Free_4.13.0"), os.path.join(elements_folder, 'MDB-Free_4.13.0'))
    
    #Copies custom.css & sidebard.js files to local directory
    shutil.copyfile(os.path.join(__location__, "custom.css"), os.path.join(elements_folder, "custom.css"))
    shutil.copyfile(os.path.join(__location__, "sidebar.js"), os.path.join(elements_folder, "sidebar.js"))

def get_file_content(path):
    f = open(path, 'r', encoding='utf8')
    data = f.read()
    f.close()
    return data

def create_index_html(reportfolderbase, time_in_secs, time_HMS, extraction_type, image_input_path, nav_list_data):
    '''Write out the index.html page to the report folder'''
    content = '<br />'
    content += """
    <div class="card bg-white" style="padding: 20px;">
        <h2 class="card-title">Case Information</h2>
    """ # CARD start
    
    case_list = [   ['Extraction location', image_input_path],
                    ['Extraction type', extraction_type],
                    ['Report directory', reportfolderbase],
                    ['Processing time', f'{time_HMS} (Total {time_in_secs} seconds)']  ]

    tab1_content = generate_key_val_table_without_headings('', case_list) + \
    """         <p class="note note-primary mb-4">
                    All dates and times are in UTC unless noted otherwise!
                </p>
    """

    # Get script run log (this will be tab2)
    devinfo_files_path = os.path.join(reportfolderbase, 'Script Logs', 'DeviceInfo.html')
    tab2_content = get_file_content(devinfo_files_path)
    
    # Get script run log (this will be tab3)
    script_log_path = os.path.join(reportfolderbase, 'Script Logs', 'Screen Output.html')
    tab3_content = get_file_content(script_log_path)
    
    # Get processed files list (this will be tab3)
    processed_files_path = os.path.join(reportfolderbase, 'Script Logs', 'ProcessedFilesLog.html')
    tab4_content = get_file_content(processed_files_path)
    
    content += tabs_code.format(tab1_content, tab2_content, tab3_content, tab4_content)
    
    content += '</div>' # CARD end

    # WRITE INDEX.HTML LAST
    filename = 'index.html'
    page_title = 'Forensics Report'
    body_heading = 'Android Forensics Tool'
    body_description = 'This is a tool for the purpose of forensic analysis of android device.'
    active_nav_list_data = mark_item_active(nav_list_data, filename) + nav_bar_script

    f = open(os.path.join(reportfolderbase, filename), 'w', encoding='utf8')
    f.write(page_header.format(page_title))
    f.write(body_start.format(f"Forensics Tool {version}"))
    f.write(body_sidebar_setup + active_nav_list_data + body_sidebar_trailer)
    f.write(body_main_header + body_main_data_title.format(body_heading, body_description))
    f.write(content)
    f.write(body_main_trailer + body_end + nav_bar_script_footer + page_footer)
    f.close()

def generate_key_val_table_without_headings(title, data_list, html_escape=True, width="70%"):
    '''Returns the html code for a key-value table (2 cols) without col names'''
    code = ''
    if title:
        code += f'<h2>{title}</h2>'
    table_header_code = \
    """
        <div class="table-responsive">
            <table class="table table-bordered table-hover table-sm" width={}>
                <tbody>
    """
    table_footer_code = \
    """
                </tbody>
            </table>
        </div>
    """
    code += table_header_code.format(width)

    # Add the rows
    if html_escape:
        for row in data_list:
            code += '<tr>' + ''.join( ('<td>{}</td>'.format(html.escape(str(x))) for x in row) ) + '</tr>'
    else:
        for row in data_list:
            code += '<tr>' + ''.join( ('<td>{}</td>'.format(str(x)) for x in row) ) + '</tr>'

    # Add footer
    code += table_footer_code

    return code

def insert_sidebar_code(data, sidebar_code, filename):
    pos = data.find(body_sidebar_dynamic_data_placeholder)
    if pos < 0:
        logfunc(f'Error, could not find {body_sidebar_dynamic_data_placeholder} in file {filename}')
        return data
    else:
        ret = data[0 : pos] + sidebar_code + data[pos + len(body_sidebar_dynamic_data_placeholder):]
        return ret

def mark_item_active(data, itemname):
    '''Finds itemname in data, then marks that node as active. Return value is changed data'''
    pos = data.find(f'" href="{itemname}"')
    if pos < 0:
        logfunc(f'Error, could not find {itemname} in {data}')
        return data
    else:
        ret = data[0 : pos] + " active" + data[pos:]
        return ret
    