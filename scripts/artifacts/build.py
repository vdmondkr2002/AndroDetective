import os
import scripts.artifacts.artGlobals 

from scripts.artifact_report import ArtifactHtmlReport
from scripts.funcs import logfunc, logdevinfo, tsv, is_platform_windows

def get_build(files_found, report_folder, seeker, wrap_text):
    data_list = []
    Androidversion = scripts.artifacts.artGlobals.versionf
    
    file_found = str(files_found[0])
    with open(file_found, "r") as f:
        for line in f: 
            splits = line.split('=')
            if splits[0] == 'ro.product.manufacturer':
                key = 'Manufacturer'
                value = splits[1]
                logdevinfo(f"Manufacturer: {value}")
            elif splits[0] == 'ro.product.brand':
                key = 'Brand'
                value = splits[1]
                logdevinfo(f"Brand: {value}")
                data_list.append((key, value))
            elif splits[0] == 'ro.product.model':
                key = 'Model'
                value = splits[1]
                logdevinfo(f"Model: {value}")
                data_list.append((key, value))
            elif splits[0] == 'ro.product.device':
                key = 'Device'
                value = splits[1]
                logdevinfo(f"Device: {value}")
                data_list.append((key, value))
            elif splits[0] == 'ro.build.version.release':
                key = 'Android Version'
                value = splits[1]
                if Androidversion == 0:
                    scripts.artifacts.artGlobals.versionf = value
                logfunc(f"Android version per build.props: {value}")
                logdevinfo(f"Android version per build.props: {value}")
                data_list.append((key, value))
            elif splits[0] == 'ro.build.version.sdk':
                key = 'SDK'
                value = splits[1]
                logdevinfo(f"SDK: {value}")
                data_list.append((key, value))
    
    itemqty = len(data_list)
    if itemqty > 0:
        report = ArtifactHtmlReport('Build Info')
        report.start_artifact_report(report_folder, f'Build Info')
        report.add_script()
        data_headers = ('Key', 'Value')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Build Info'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc(f'No Build Info data available')    
   