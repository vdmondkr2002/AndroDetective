import traceback

from scripts.artifacts.accounts_ce import get_accounts_ce
from scripts.artifacts.accounts_ce_authtokens import get_accounts_ce_authtokens
from scripts.artifacts.appicons import get_appicons
from scripts.artifacts.bluetoothConnections import get_bluetoothConnections
from scripts.artifacts.build import get_build
from scripts.artifacts.calllog import get_calllog
from scripts.artifacts.chrome import get_chrome
from scripts.artifacts.chromeBookmarks import get_chromeBookmarks
from scripts.artifacts.chromeCookies import get_chromeCookies
from scripts.artifacts.chromeOfflinePages import get_chromeOfflinePages
from scripts.artifacts.chromeTopSites import get_chromeTopSites
from scripts.artifacts.contacts import get_contacts
from scripts.artifacts.googleKeepNotes import get_googleKeepNotes
from scripts.artifacts.messages import get_messages
from scripts.artifacts.last_boot_time import get_last_boot_time
from scripts.artifacts.packageGplinks import get_packageGplinks
from scripts.artifacts.permissions import get_permissions
from scripts.artifacts.recentactivity import get_recentactivity
from scripts.artifacts.siminfo import get_siminfo
from scripts.artifacts.teams import get_teams
from scripts.artifacts.usagestatsVersion import get_usagestatsVersion
from scripts.artifacts.Whatsapp import get_Whatsapp
from scripts.artifacts.wifiHotspot import get_wifiHotspot

from scripts.funcs import *

tosearch = {
    'build':('Device Info', '*/system/build.prop'),
    'accounts_ce': ('Accounts_ce', '*/data/system_ce/*/accounts_ce.db'),
    'accounts_ce_authtokens':('Accounts_ce', '*/data/system_ce/*/accounts_ce.db'),
    'appicons':('Installed Apps', '*/data/com.google.android.apps.nexuslauncher/databases/app_icons.db*'),
    'bluetoothConnections':('Bluetooth Connections', '*/data/misc/bluedroid/bt_config.conf'),
    'calllog': ('Call Logs', '*/data/com.android.providers.contacts/databases/calllog.db'),
    'chrome':('Chromium', '*/data/data/*/app_chrome/Default/History*'),
    'chromeBookmarks':('Chromium', '*/data/data/*/app_chrome/Default/Bookmarks*'),
    'chromeCookies':('Chromium', '*/data/data/*/app_chrome/Default/Cookies*'),
    'chromeOfflinePages':('Chromium', '*/data/data/*/app_chrome/Default/Offline Pages/metadata/OfflinePages.db*'),
    'chromeTopSites':('Chromium', '*/data/data/*/app_chrome/Default/Top Sites*'),
    'contacts':('Contacts', '**/com.android.providers.contacts/databases/contact*'),
    'googleKeepNotes':('Google Keep', "**/data/com.google.android.keep/databases/keep.db"),
    'messages': ('Messages', ('**/com.google.android.apps.messaging/databases/bugle_db*')),
    'last_boot_time': ('Power Events', '**/data/misc/bootstat/last_boot_time_utc'),
    'packageGplinks': ('Installed Apps', '*/system/packages.list'),
    'recentactivity':('Recent Activity', '*/data/system_ce/*'),
    'permissions':('Permissions', '*/system/packages.xml'),
    'siminfo':('Device Info', '*/user_de/*/com.android.providers.telephony/databases/telephony.db'),
    'teams':('Teams', '*/com.microsoft.teams/databases/SkypeTeams.db*'),
    'usagestatsVersion':('Usage Stats', '*/system/usagestats/*/version'),
    'Whatsapp':('Whatsapp', ('*/com.whatsapp/databases/*.db*','**/com.whatsapp/shared_prefs/com.whatsapp_preferences_light.xml')),
    'wifiHotspot':('WiFi Profiles', '**/misc/wifi/softap.conf'),
    }

slash = '\\' if is_platform_windows() else '/'

def process_artifact(files_found, artifact_func, artifact_name, seeker, report_folder_base, wrap_text):
    logfunc('{} [{}] artifact executing'.format(artifact_name, artifact_func))
    report_folder = os.path.join(report_folder_base, artifact_name) + slash
    try:
        if os.path.isdir(report_folder):
            pass
        else:
            os.makedirs(report_folder)
    except Exception as ex:
        logfunc('Error creating {} report directory at path {}'.format(artifact_name, report_folder))
        logfunc('Reading {} artifact failed!'.format(artifact_name))
        logfunc('Error was {}'.format(str(ex)))
        return
    try:
        method = globals()['get_' + artifact_func]
        method(files_found, report_folder, seeker, wrap_text)
    except Exception as ex:
        logfunc('Reading {} artifact had errors!'.format(artifact_name))
        logfunc('Error was {}'.format(str(ex)))
        logfunc('Exception Traceback: {}'.format(traceback.format_exc()))
        return

    logfunc('{} [{}] artifact completed'.format(artifact_name, artifact_func))
