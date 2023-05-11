import os
import json
import numpy as np

from adb_utils.adb import Adb
from adb_utils.common import execute
from createTpnrConfig import makeConfig

from utils import *
from outputParser import *

class optimumThreadAnalysis():
    def __init__(self, args):
        self.args = args
        self.adb = Adb("adb", self.args.device, hostname=self.args.hostname)
        if self.args.snpe_exec_path is not None and self.args.snpe_exec_path[-1] == '/':
            self.args.snpe_exec_path = self.args.snpe_exec_path[:-1]
        if self.args.qnn_exec_path is not None and self.args.qnn_exec_path[-1] == '/':
            self.args.qnn_exec_path = self.args.qnn_exec_path[:-1]

    def pushFiles(self, src_path, on_device_dir):
        input_files = os.listdir(src_path)
        self.adb.shell('rm -rf {0}'.format(on_device_dir))
        logger.info("Removed existing folder {} on device.".format(on_device_dir))
        ret =True
        for file in input_files:
            return_code, out, err = self.adb.push(os.path.join(src_path,file), os.path.join(on_device_dir,file))
            ret =True
            if return_code:
                ret = False
                logger.error("ADB Push Failed!!")

        return ret

    def pullFiles(self, src_path, dest_path):
        ret = True
        return_code, out, err = self.adb.pull(src_path, dest_path)
        ret =True
        if return_code:
            ret = False
            logger.error("ADB Pull Failed!!")
        
        return ret

    def createSnpeCommand(self, model_name, on_device_dir, n_threads, perf_profile):
        shell_cmd = "cd {}; export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:{};".format(on_device_dir, on_device_dir)
        shell_cmd += "chmod -R 777 {};".format(on_device_dir)
        shell_cmd += "./snpe-throughput-net-run --duration {} ".format(self.args.duration)
        for n_thread in range(n_threads):
            shell_cmd += "--container {} --use_dsp --perf_profile {} --userbuffer_tf8 ".format(model_name, perf_profile)

        return shell_cmd

    def createQnnCommand(self, model_name, on_device_dir, n_threads, perf_profile):
        shell_cmd = "cd {}; export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:{};".format(on_device_dir,on_device_dir)
        shell_cmd += " chmod -R 777 {};".format(on_device_dir)
        shell_cmd += " ./qnn-throughput-net-run --config {} ".format(os.path.join(on_device_dir, 'tpnr_config_{}_{}_{}T.json'.format(model_name, perf_profile, str(n_threads))))

        return shell_cmd

    def parseQnnOutput(self, cmd_out,n_thread):
        t_idx = cmd_out.find('TotalTime')
        total_time = float(cmd_out[t_idx:].split('\n')[0].split(' ')[-1])*1e-6
        if t_idx == -1:
            return 0
        else:
            inf_per_thread = []
            for t_idx in range(1, n_thread+1):
                idx = cmd_out.find('htp_thread_{}:graphExecute'.format(str(t_idx)))
                inf_per_sec_util_list =  cmd_out[idx:].split('\n')[0].split(' ')
                for item in inf_per_sec_util_list:
                    if item != '' and item != 'htp_thread_{}:graphExecute:'.format(str(t_idx)):
                        inf_per_thread.append(float(item))
                        break
            total_infs = float(sum(inf_per_thread)/total_time)
            return total_infs

    def executeSnpe(self, on_device_dir):
        list_of_models = []
        for file in os.listdir(self.args.snpe_exec_path):
            if file.endswith('.dlc'):
                list_of_models.append(file)
        models_inf_per_sec_info = {}
        models_inf_per_sec_info['all_inferences'] = {}
        models_inf_per_sec_info['avg_inferences'] = {}

        for model in list_of_models:
            model_name = model.split('.')[0]
            logger.info("Processing...... {}".format(model_name))
            models_inf_per_sec_info['all_inferences'][model_name] = {}
            models_inf_per_sec_info['avg_inferences'][model_name] = {}
            for perf_profile in DEFAULT_PERF_PROFILES:
                models_inf_per_sec_info['all_inferences'][model_name][perf_profile] = {}
                models_inf_per_sec_info['avg_inferences'][model_name][perf_profile] = {}
            
                for n_thread in range(1,int(self.args.max_threads)+1):
                    models_inf_per_sec_info['all_inferences'][model_name][perf_profile][str(n_thread)+'_threads'] = []

                    shell_cmd = self.createSnpeCommand(model.split('/')[-1].split('.serialized.bin')[0], on_device_dir, n_thread, perf_profile)
                    logger.debug(shell_cmd)
                    for run_id in range(self.args.avg_run_each_model):
                        exe_status, cmd_out, err = execute('adb',
                                                            ['-s', self.adb._adb_device, '-H', self.adb._hostname, 'shell', shell_cmd],
                                                            '.',
                                                            False,
                                                            PER_TEST_TIMEOUT,
                                                            False)
                        if err:
                            logger.error("Below is the error\n{}".format(err))
                        else:
                            idx = cmd_out.find('Total throughput: ')
                            models_inf_per_sec_info['all_inferences'][model_name][perf_profile][str(n_thread)+'_threads'].append(float(cmd_out[idx:].split('Total throughput: ')[-1].split(' infs/sec')[0]))
                    
                    logger.debug('Infs/sec in each run for {} is {}'.format(model_name,models_inf_per_sec_info['all_inferences'][model_name][perf_profile][str(n_thread)+'_threads']))
                    models_inf_per_sec_info['avg_inferences'][model_name][perf_profile][str(n_thread)+'_threads'] = np.round(np.mean(models_inf_per_sec_info['all_inferences'][model_name][perf_profile][str(n_thread)+'_threads']),2)

                    if n_thread >= 2:
                        if models_inf_per_sec_info['avg_inferences'][model_name][perf_profile][str(n_thread)+'_threads'] <  models_inf_per_sec_info['avg_inferences'][model_name][perf_profile][str(n_thread-1)+'_threads']:
                            break

        # with open("snpeRuns.json", "w") as outfile:
        #     json.dump(models_inf_per_sec_info, outfile, indent = 4)
        
        return models_inf_per_sec_info

    def executeQnn(self, on_device_dir):
        list_of_models = []
        for file in os.listdir(self.args.qnn_exec_path):
            if file.endswith('.serialized.bin'):
                list_of_models.append(file)
        models_inf_per_sec_info = {}
        models_inf_per_sec_info['all_inferences'] = {}
        models_inf_per_sec_info['avg_inferences'] = {}

        for model in list_of_models:
            model_name = model.split('.')[0]
            logger.info("Processing...... {}".format(model_name))
            models_inf_per_sec_info['all_inferences'][model_name] = {}
            models_inf_per_sec_info['avg_inferences'][model_name] = {}
            for perf_profile in DEFAULT_PERF_PROFILES:
                models_inf_per_sec_info['all_inferences'][model_name][perf_profile] = {}
                models_inf_per_sec_info['avg_inferences'][model_name][perf_profile] = {}
            
                for n_thread in range(1,int(self.args.max_threads)+1):
                    models_inf_per_sec_info['all_inferences'][model_name][perf_profile][str(n_thread)+'_threads'] = []

                    shell_cmd = self.createQnnCommand(model_name, on_device_dir, n_thread, perf_profile)
                    logger.debug(shell_cmd)
                    for run_id in range(self.args.avg_run_each_model):
                        exe_status, cmd_out, err = execute('adb',
                                                            ['-s', self.adb._adb_device, '-H', self.adb._hostname, 'shell', shell_cmd],
                                                            '.',
                                                            False,
                                                            PER_TEST_TIMEOUT,
                                                            False)
                        if err:
                            logger.error("Below is the error\n{}".format(err))
                        else:
                            infs_per_sec = self.parseQnnOutput(cmd_out,n_thread)
                            models_inf_per_sec_info['all_inferences'][model_name][perf_profile][str(n_thread)+'_threads'].append(np.round(infs_per_sec,2))
                    
                    logger.debug('Infs/sec in each run for {} is {}'.format(model_name,models_inf_per_sec_info['all_inferences'][model_name][perf_profile][str(n_thread)+'_threads']))
                    models_inf_per_sec_info['avg_inferences'][model_name][perf_profile][str(n_thread)+'_threads'] = np.round(np.mean(models_inf_per_sec_info['all_inferences'][model_name][perf_profile][str(n_thread)+'_threads']),2)

                    if n_thread >= 2:
                        if models_inf_per_sec_info['avg_inferences'][model_name][perf_profile][str(n_thread)+'_threads'] < models_inf_per_sec_info['avg_inferences'][model_name][perf_profile][str(n_thread-1)+'_threads']:
                            break

        # if self.args.gen_qnn_v1:
        #     with open("qnnV1Runs.json", "w") as outfile:
        #         json.dump(models_inf_per_sec_info, outfile, indent = 4)
        # else:
        #     with open("qnnV2Runs.json", "w") as outfile:
        #         json.dump(models_inf_per_sec_info, outfile, indent = 4)
        return models_inf_per_sec_info

    def executeOndevice(self):
        if self.args.gen_snpe:
            logger.info('Running inferences for SNPE')
            on_device_dir = '/data/local/tmp/' + self.args.snpe_exec_path.split('/')[-1]
            ret = self.pushFiles(self.args.snpe_exec_path, on_device_dir)
            if ret:
                models_inf_per_sec_info_SNPE = self.executeSnpe(on_device_dir)
                createAnalysisSheet(models_inf_per_sec_info_SNPE, self.args)
                os.system("adb -s {} shell 'rm -rf {}'".format(self.args.device, on_device_dir))
            else:
                logger.error("Failed to push files on to device.... Skipping SNPE analysis")
        
        if self.args.gen_qnn_v1:
            logger.info('Running inferences for QNN')
            on_device_dir = '/data/local/tmp/' + self.args.qnn_exec_path.split('/')[-1]
            makeConfig(self.args.qnn_exec_path, on_device_dir, self.args.duration, self.args.max_threads, self.args.vtcm_mem, self.args.dsp_arch, qnn_v1=True)
            ret = self.pushFiles(self.args.qnn_exec_path, on_device_dir)
            if ret:
                models_inf_per_sec_info_QNN = self.executeQnn(on_device_dir)
                createAnalysisSheet(models_inf_per_sec_info_QNN, self.args)
                os.system("adb -s {} shell 'rm -rf {}'".format(self.args.device, on_device_dir))
            else:
                logger.error("Failed to push files on to device.... Skipping QNN analysis")

        if self.args.gen_qnn_v2:
            logger.info('Running inferences for QNN')
            on_device_dir = '/data/local/tmp/' + self.args.qnn_exec_path.split('/')[-1]
            makeConfig(self.args.qnn_exec_path, on_device_dir, self.args.duration, self.args.max_threads, self.args.vtcm_mem, self.args.dsp_arch, qnn_v2=True)
            ret = self.pushFiles(self.args.qnn_exec_path, on_device_dir)
            if ret:
                models_inf_per_sec_info_QNN = self.executeQnn(on_device_dir)
                createAnalysisSheet(models_inf_per_sec_info_QNN, self.args)
                os.system("adb -s {} shell 'rm -rf {}'".format(self.args.device, on_device_dir))
            else:
                logger.error("Failed to push files on to device.... Skipping QNN analysis")
