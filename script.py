import json
from time import sleep
from datetime import datetime
import os

import sys
import xlsxwriter

DEFAULT_SYSMON_PROFILES = ["timestamp","0x0", "0x1000", "0x2", "0x3", "Total Ion Memory"]

#inpu = [{'|0x0': 8192, '|0x1000': 511647744, '|0x2': 8192, '|0x3': 286720}, {'|0x0': 8192, '|0x1000': 511647744, '|0x2': 8192, '|0x3': 286720}, {'|0x0': 8192, '|0x1000': 511647744, '|0x2': 8192, '|0x3': 286720}, {'|0x0': 4096, '|0x1000': 511647744, '|0x2': 8192, '|0x3': 4096}, {'|0x1000': 503316480}]

def createAnalysisSheet(inputt):

#  list_of_models = list(models_inf_per_sec_info["all_inferences"].keys())
#  optimal_values = parseOutputJson(models_inf_per_sec_info)
  now = datetime.now()
  curr_datetime = now.strftime("%Y%m%d%H%M%S")
  os.makedirs("debugfs_{}".format(str(curr_datetime)))
  workbook = xlsxwriter.Workbook("debugfs_{}/output.xlsx".format(str(curr_datetime)))
  worksheet = workbook.add_worksheet("Analysis")
  border_format = workbook.add_format({'border': 1})

  def merge_cells(row1,col1, row2,col2, text):
    merge_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
    worksheet.merge_range(row1,col1, row2,col2, text, merge_format)

  print("printing")
  start_r=0; start_c=0; end_r=0; end_c=0
  for perf_profile in DEFAULT_SYSMON_PROFILES:
    worksheet.write(start_r, end_c, perf_profile,border_format)
    start_c+=1; end_c+=1

#  print(time_dict)

  row = 1; column = 0
  for element in inputt:
    column=0
    count =0
    for dict_ele in element:
        if 'timestamp' in dict_ele:
          print(dict_ele)
          column=0
          print(element[dict_ele])
          worksheet.write(row,column, element['timestamp'],border_format)
          print("write timestamp",column,element['timestamp'],row)
        elif '|0x0' in dict_ele:
          print(dict_ele)
          column=1
          print(element[dict_ele])
          worksheet.write(row,column, element['|0x0'],border_format)
          print("write 0",column,element['|0x0'],row)
        elif '|0x1000' in dict_ele:
          print(dict_ele)
          column=2
          print(element[dict_ele])
          worksheet.write(row,column, element['|0x1000'],border_format)
          print("write 1",column,element['|0x1000'],row)
        elif '|0x2' in dict_ele:
          print(dict_ele)
          column=3
          print(element[dict_ele])
          worksheet.write(row,column, element['|0x2'],border_format)
          print("write 2",column,element['|0x2'],row)
        elif '|0x3' in dict_ele:
          print(dict_ele)
          column=4
          print(element[dict_ele])
          worksheet.write(row,column, element['|0x3'],border_format)
          print("write 3",column,element['|0x3'],row)
        elif '|Total Ion Memory' in dict_ele:
          print(dict_ele)
          column=5
          print(element[dict_ele])
          worksheet.write(row,column, element['|Total Ion Memory'],border_format)
          print("write combine",column,element['|Total Ion Memory'],row)
#        else:
#          worksheet.write(row,column, 0 ,border_format)
#        column += 1
    row+=1

  workbook.close()

'''
  row = 4; column = 1
  for element in data:
    column = 1
  name = ""
  timesta = 0
  val = 0
  worksheet.write(row,column, model,border_format)
  for ele in element.keys():
    if 'Name' in ele:
      name = element[ele]
    if 'timestamp' in ele:
      for ele1 in element[ele].keys():
        if 'Value' in ele1:
          print("\ntimestamp",element[ele][ele1])
    if 'Description' in ele:
      print("\nDescription",element[ele])
    if 'Params' in ele:
      print("\n {} in % is {}".format(name, element[ele][1]['Value'])
'''      
#  workbook.close()

#  with open("optimal_thread_analysis_{}/runsInfo.json".format(str(curr_datetime)), "w") as outfile:
#    json.dump(models_inf_per_sec_info, outfile, indent = 4)





my_json = open("vgg19_qnncpp_T.txt", "r")
lis_ele = []
lis_ele = my_json.readlines()
#print(lis_ele)
length = len(lis_ele)
print(len(lis_ele))
count = 0
lis_maps = []
for i in range(0,length):
    if 'LIST OF MAPS' in lis_ele[i]:
        list_size = {}
        list_size['|0x0'] = 0
        list_size['|0x2'] = 0
        list_size['|0x3'] = 0
        list_size['|Total Ion Memory'] = 0
        list_size['timestamp'] = 0
        list_size['|0x1000'] = 0
        print(lis_ele[i])
        count += 1
        print(lis_ele[i+3])
        print(len(lis_ele[i+3]))
        print(lis_ele[i+3].split()[-1])
        list_size['timestamp'] = lis_ele[i-16].split('-')[-1].split()[-1]
        print("here")
        print(lis_ele[i-16].split('-')[-1].split()[-1])
        print("timestamp")
        for j in range(i,length):
            if 'len' in lis_ele[j]:
                break
            if len(lis_ele[j]) >=88  and '|0x0' in lis_ele[j].split()[-1]:
                print(lis_ele[j].split())
                val = int(lis_ele[j].split()[-2].split('|0x')[-1])
                print("printing  0")
                if '|0x0' in list_size:
                    updated_hex = list_size['|0x0']               
                    updated_dec = int(updated_hex)
                    new_dec = val
                    new_dec = new_dec + updated_dec
                    val = new_dec
#                    print("printing values 0")
 #                   print(updated_hex)
  #                  print(updated_dec)
   #                 print(new_dec)
    #                print(val)
                list_size['|0x0'] = val
            elif len(lis_ele[j]) >= 88 and '|0x1000' in lis_ele[j].split()[-1]:
                print(lis_ele[j].split())
                val = int(lis_ele[j].split()[-2].split('|0x')[-1])
                print("printing  0")
                if '|0x1000' in list_size:
                    updated_hex = list_size['|0x1000']                   
                    updated_dec = int(updated_hex)
                    new_dec = val
                    new_dec = new_dec + updated_dec
                    val = new_dec
#                    print("printing values 0")
 #                   print(updated_hex)
  #                  print(updated_dec)
   #                 print(new_dec)
    #                print(val)
                list_size['|0x1000'] = val
            elif len(lis_ele[j]) >= 88 and '|0x2' in lis_ele[j].split()[-1]:
                print(lis_ele[j].split())
                val = int(lis_ele[j].split()[-2].split('|0x')[-1])
                print("printing  0")
                if '|0x2' in list_size:
                    updated_hex = list_size['|0x2']                   
                    updated_dec = int(updated_hex)
                    new_dec = val
                    new_dec = new_dec + updated_dec
                    val = new_dec
#                    print("printing values 0")
 #                   print(updated_hex)
  #                  print(updated_dec)
   #                 print(new_dec)
    #                print(val)
                list_size['|0x2'] = val
            elif len(lis_ele[j]) >= 88 and '|0x3' in lis_ele[j].split()[-1]:
                print(lis_ele[j].split())
                val = int(lis_ele[j].split()[-2].split('|0x')[-1])
                print("printing  0")
                if '|0x3' in list_size:
                    updated_hex = list_size['|0x3']                    
                    updated_dec = int(updated_hex)
                    new_dec = val
                    new_dec = new_dec + updated_dec
                    val = new_dec
#                    print("printing values 0")
 #                   print(updated_hex)
  #                  print(updated_dec)
   #                 print(new_dec)
    #                print(val)
                list_size['|0x3'] = val
        list_size['|Total Ion Memory'] = list_size['|0x0'] + list_size['|0x2'] + list_size['|0x3']
        lis_maps.append(list_size)
        print(list_size)


final_list = []
for ele in lis_maps:
    myKeys = list(ele.keys())
    myKeys.sort()
    sorted_dict = {i: ele[i] for i in myKeys}
    final_list.append(sorted_dict)

print(final_list)





#print(count)
createAnalysisSheet(final_list)

