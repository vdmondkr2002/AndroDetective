import os
import scripts.report as report

from scripts.search_files import *
from scripts.tool_artifacts import *
from scripts.version_info import version
from time import process_time, gmtime, strftime

def crunch_artifacts(search_list, extracttype, input_path, out_params, ratio, wrap_text):
    start = process_time()

    logfunc('Procesing started. Please wait. This may take a few minutes...')

    logfunc('\n--------------------------------------------------------------------------------------')
    logfunc(f'AndroDetective')
    logdevinfo()

    seeker = FileSeekerDir(input_path)

    # Now ready to run
    logfunc(f'Artifact categories to parse: {str(len(search_list))}')
    logfunc(f'File/Directory selected: {input_path}')
    logfunc('\n--------------------------------------------------------------------------------------')

    log = open(os.path.join(out_params.report_folder_base, 'Script Logs', 'ProcessedFilesLog.html'), 'w+', encoding='utf8')
    nl = '\n' #literal in order to have new lines in fstrings that create text files
    log.write(f'Extraction/Path selected: {input_path}<br><br>')
    
    categories_searched = 0
    # Search for the files per the arguments
    for key, val in search_list.items():
        search_regexes = []
        artifact_pretty_name = val[0]
        if isinstance(val[1], list) or isinstance(val[1], tuple):
            search_regexes = val[1]
        else:
            search_regexes.append(val[1])
        files_found = []
        for artifact_search_regex in search_regexes:
            found = seeker.search(artifact_search_regex)
            if not found:
                logfunc()
                logfunc(f'No files found for {key} -> {artifact_search_regex}')
                log.write(f'No files found for {key} -> {artifact_search_regex}<br><br>')
            else:
                files_found.extend(found)
        if files_found:
            logfunc()
            process_artifact(files_found, key, artifact_pretty_name, seeker, out_params.report_folder_base, wrap_text)
            for pathh in files_found:
                if pathh.startswith('\\\\?\\'):
                    pathh = pathh[4:]
                log.write(f'Files for {artifact_search_regex} located at {pathh}<br><br>')
        categories_searched += 1
        GuiWindow.SetProgressBar(categories_searched * ratio)
    log.close()

    logfunc('')
    logfunc('Processes completed.')
    end = process_time()
    run_time_secs =  end - start
    run_time_HMS = strftime('%H:%M:%S', gmtime(run_time_secs))
    logfunc("Processing time = {}".format(run_time_HMS))

    logfunc('')
    logfunc('Report generation started.')
    # remove the \\?\ prefix we added to input and output paths, so it does not reflect in report
    if is_platform_windows(): 
        if out_params.report_folder_base.startswith('\\\\?\\'):
            out_params.report_folder_base = out_params.report_folder_base[4:]
        if input_path.startswith('\\\\?\\'):
            input_path = input_path[4:]
    report.generate_report(out_params.report_folder_base, run_time_secs, run_time_HMS, extracttype, input_path)
    logfunc('Report generation Completed.')
    logfunc('')
    logfunc(f'Report location: {out_params.report_folder_base}')
    return True
