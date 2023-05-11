import os
import json
from copy import deepcopy
from utils import *

def makeConfig(host_path, on_device_path, duration, max_threads, vtcm_mem, dsp_arch, qnn_v1=False, qnn_v2=False):
  list_of_models = []
  for file in os.listdir(host_path):
    if file.endswith('.serialized.bin'):
      list_of_models.append(file)

  if qnn_v1:
    customParam = deepcopy(custom_param_config_v1)
    customParam["vtcm_mb"] = vtcm_mem
    customParam["dsp_arch"] = dsp_arch

    with open(os.path.join(host_path,"customParamV1.json"), "w") as outfile:
      json.dump(customParam, outfile, indent = 4)

  if qnn_v2:
    for perf_profile in DEFAULT_PERF_PROFILES:
      customParam = {}
      customParam[perf_profile] = deepcopy(custom_param_config_v2)
      customParam[perf_profile]["graphs"]["vtcm_mb"] = vtcm_mem
      customParam[perf_profile]["devices"][0]["dsp_arch"] = dsp_arch
      customParam[perf_profile]["devices"][0]["cores"][0]["perf_profile"] = perf_profile

      with open(os.path.join(host_path,"customParamV2_{}.json".format(perf_profile)), "w") as outfile:
        json.dump(customParam[perf_profile], outfile, indent = 4)

  for n_thread in range(1, max_threads+1):
    tpnr_config = {}
    tpnr_config = deepcopy(config_skel)

    tpnr_config['backends'][0]['backendPath'] = os.path.join(on_device_path,'libQnnHtp.so')
    tpnr_config['backends'][0]['backendExtensions'] = os.path.join(on_device_path,'libQnnHtpNetRunExtensions.so')
    tpnr_config['testCase']['threads'][0]['loop'] = duration
    
    for t_idx in range(1, n_thread):
      tpnr_config['models'].append(deepcopy(tpnr_config['models'][0]))
      tpnr_config['models'][t_idx]['modelName'] = 'model_{}'.format(str(t_idx+1))
      tpnr_config['models'][t_idx]['outputPath'] = 'model_{}-output'.format(str(t_idx+1))

      tpnr_config['contexts'].append(deepcopy(tpnr_config['contexts'][0]))
      tpnr_config['contexts'][t_idx]['contextName'] = 'htp_context_{}'.format(str(t_idx+1))

      tpnr_config['testCase']['threads'].append(deepcopy(tpnr_config['testCase']['threads'][0]))
      tpnr_config['testCase']['threads'][t_idx]['threadName'] = 'htp_thread_{}'.format(str(t_idx+1))
      tpnr_config['testCase']['threads'][t_idx]['context'] = 'htp_context_{}'.format(str(t_idx+1))
      tpnr_config['testCase']['threads'][t_idx]['model'] = 'model_{}'.format(str(t_idx+1))

    for model in list_of_models:
      for perf_profile in DEFAULT_PERF_PROFILES:
        tpnr_config['backends'][0]['perfProfile'] = perf_profile
        if qnn_v1:
          for t_idx in range(n_thread):
            tpnr_config['models'][t_idx]['modelPath'] = os.path.join(on_device_path,model)
          with open(os.path.join(host_path,"tpnr_config_{}_{}_{}T.json".format(model.split('.serialized.bin')[0], perf_profile, str(n_thread))), "w") as outfile:
            json.dump(tpnr_config, outfile, indent = 4)
        if qnn_v2:
          for t_idx in range(n_thread):
            tpnr_config['models'][t_idx]['modelPath'] = os.path.join(on_device_path,model)
            tpnr_config['testCase']['threads'][t_idx]['backendConfig'] = 'customParamV2_{}.json'.format(perf_profile)
          with open(os.path.join(host_path,"tpnr_config_{}_{}_{}T.json".format(model.split('.serialized.bin')[0], perf_profile, str(n_thread))), "w") as outfile:
            json.dump(tpnr_config, outfile, indent = 4)

  os.system("chmod -R 777 {}".format(os.path.join(host_path,"*")))

# if __name__=='__main__':
#     makeConfig('model.bin','/data/local/tmp/',100,1)

