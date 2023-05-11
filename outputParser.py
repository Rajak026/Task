import os
import json
import xlsxwriter
from datetime import datetime

from utils import *

def parseOutputJson(models_inf_per_sec_info):
    models_used = list(models_inf_per_sec_info["avg_inferences"].keys())
    perf_profiles_used = list(models_inf_per_sec_info["avg_inferences"][models_used[0]].keys())

    optimal_values = {}
    for model in models_used:
        optimal_values[model] = {}
        for perf_profile in perf_profiles_used:
            optimal_values[model][perf_profile] = {}
            max_perf_thread = max(models_inf_per_sec_info["avg_inferences"][model][perf_profile], key=models_inf_per_sec_info["avg_inferences"][model][perf_profile].get)
            optimal_values[model][perf_profile][max_perf_thread] = models_inf_per_sec_info["avg_inferences"][model][perf_profile][max_perf_thread]

    return optimal_values

def createAnalysisSheet(models_inf_per_sec_info, args):
    
    list_of_models = list(models_inf_per_sec_info["all_inferences"].keys())
    optimal_values = parseOutputJson(models_inf_per_sec_info)
    now = datetime.now()
    curr_datetime = now.strftime("%Y%m%d%H%M%S")
    os.makedirs("optimal_thread_analysis_{}".format(str(curr_datetime)))
    workbook = xlsxwriter.Workbook("optimal_thread_analysis_{}/output.xlsx".format(str(curr_datetime)))
    worksheet = workbook.add_worksheet("Analysis")
    border_format = workbook.add_format({'border': 1})
    
    def merge_cells(row1,col1, row2,col2, text):
        merge_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
        worksheet.merge_range(row1,col1, row2,col2, text, merge_format)

    merge_cells(2,1,3,1, 'Models')
    start_r=2; start_c=2; end_r=2; end_c=2
    for perf_profile in DEFAULT_PERF_PROFILES:
        merge_cells(start_r,start_c,end_r,end_c+1, perf_profile)
        worksheet.write(start_r+1,start_c, "Optimum Threads",border_format)
        worksheet.write(start_r+1,start_c+1, "Inf/sec",border_format)
        start_c+=2; end_c+=2
    
    row = 4; column = 1
    for model in list_of_models:
        column=1
        worksheet.write(row,column, model,border_format)
        for perf_profile in DEFAULT_PERF_PROFILES:
            optimal_thread = list(optimal_values[model][perf_profile].keys())[0]
            worksheet.write(row,column+1, int(optimal_thread.split('_threads')[0]),border_format)
            worksheet.write(row,column+2, optimal_values[model][perf_profile][optimal_thread],border_format)
            column+=2
        row+=1

    worksheet = workbook.add_worksheet("Runs info")
    start_r=1; start_c=1; end_r=1; end_c=1

    for model in list_of_models:
        merge_cells(start_r,start_c,start_r,start_c+2, "{}".format(model))
        # worksheet.write(start_r,start_c+2, "{}".format(model),border_format)
        start_r+=1; end_r+=1
        merge_cells(start_r,start_c,start_r+1,start_c, 'Models')
        for t_id in range(1, int(args.max_threads)+1):
            merge_cells(start_r,start_c+1,end_r,end_c+int(args.avg_run_each_model)+1, "{}_thread".format(t_id))
            for perf_idx, perf_profile in enumerate(DEFAULT_PERF_PROFILES,start=1):
                thread_keys = list(models_inf_per_sec_info['all_inferences'][model][perf_profile].keys())
                if '{}_threads'.format(t_id) in thread_keys:
                    for run_id in range(1,int(args.avg_run_each_model)+1):
                        worksheet.write(start_r+1,start_c+run_id, "R{}".format(run_id),border_format)
                        worksheet.write(start_r+1+perf_idx,start_c+run_id, models_inf_per_sec_info['all_inferences'][model][perf_profile]['{}_threads'.format(t_id)][run_id-1],border_format)

                    worksheet.write(start_r+1,start_c+int(args.avg_run_each_model)+1, "Average",border_format)
                    worksheet.write(start_r+1+perf_idx,start_c+int(args.avg_run_each_model)+1, models_inf_per_sec_info['avg_inferences'][model][perf_profile]['{}_threads'.format(t_id)],border_format)
                    # worksheet.write(start_r+1+perf_idx,1, model,border_format)
                    worksheet.write(start_r+1+perf_idx,1, perf_profile,border_format)

            start_c+=int(args.avg_run_each_model)+1; end_c+=int(args.avg_run_each_model)+1
        start_r+=3+len(DEFAULT_PERF_PROFILES); end_r+=3+len(DEFAULT_PERF_PROFILES); start_c=1; end_c=1
        
    workbook.close()

    with open("optimal_thread_analysis_{}/runsInfo.json".format(str(curr_datetime)), "w") as outfile:
        json.dump(models_inf_per_sec_info, outfile, indent = 4)

# if __name__=='__main__':
#     import argparse
#     parser = argparse.ArgumentParser(description="Running Optimum thread analysis")
#     parser.add_argument('-max_threads', dest='max_threads', required=False, default=10, type=int, action="store", help="Number of threads to use while execution. Goes from 1 to n")
#     parser.add_argument('-avg_run', dest='avg_run_each_model', required=False, default=3, type=int, action="store", help="Number of runs to perform for each model, final inf/sec will be avg of these runs")

#     args = parser.parse_args()

#     with open('runsInfo.json','r') as file:
#         models_inf_per_sec_info = json.load(file)

#     # import pdb; pdb.set_trace()
#     print(models_inf_per_sec_info)
#     createAnalysisSheet(models_inf_per_sec_info, args)
