import argparse
from threadAnalysis import optimumThreadAnalysis
from calling_cpp import main
if __name__=="__main__":

    parser = argparse.ArgumentParser(description="Running Optimum thread analysis")
    parser.add_argument("-snpe", "--gen_snpe", default=False, action="store_true", help="Flag to generate analysis for SNPE")
    parser.add_argument("-qnnv1", "--gen_qnn_v1", default=False, action="store_true", help="Flag to generate analysis for QNN 1.x")
    parser.add_argument("-qnnv2", "--gen_qnn_v2", default=False, action="store_true", help="Flag to generate analysis for QNN 2.x")
    parser.add_argument("-duration", dest="duration", required=True, default=10, type=int, action="store", help="duration for model to execute")
    parser.add_argument("-snpe_exec_path", dest="snpe_exec_path", required=False, action="store", help="exec path with required libs and model files (.dlc) to execute on device")
    parser.add_argument("-qnn_exec_path", dest="qnn_exec_path", required=False, action="store", help="exec path with required libs and model files (.so/.serialiized.bin) to execute on device")
    parser.add_argument('-host', dest='hostname', required=False, default="localhost",action="store", help="Hostname where device is connected. DEFAULT=localhost")
    parser.add_argument('-did', dest='device', required=False, default=None, action="store", help="Device Id")
    parser.add_argument('-max_threads', dest='max_threads', required=False, default=10, type=int, action="store", help="Number of threads to use while execution. Goes from 1 to n")
    parser.add_argument('-avg_run', dest='avg_run_each_model', required=False, default=3, type=int, action="store", help="Number of runs to perform for each model, final inf/sec will be avg of these runs")
    parser.add_argument('-mem', dest='vtcm_mem', required=False, default=8, type=int, action="store", help="VTCM Memory of device; ex: -mem 2")
    parser.add_argument('-dsp', dest='dsp_arch', required=False, default="v69", type=str, action="store", help="DSP aarch of device; Ex: -dsp v68")

    args = parser.parse_args()

    opt_analysis = optimumThreadAnalysis(args)
    opt_analysis.executeOndevice()
