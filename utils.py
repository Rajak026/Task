import logging

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

PER_TEST_TIMEOUT = 18000
DEFAULT_PERF_PROFILES = ["burst" , "low_power_saver", "power_saver"]

#config for qnn tpnr
config_skel = {
    "backends": [
      {
        "backendName": "htp_backend",
        "profilingLevel": "OFF",
        "backendPath": "<path_to_libQnnHtp.so>",
        "backendExtensions": "<path_to_libQnnHtpNetRunExtensions.so>",
        "perfProfile": "low_balanced"
      }
    ],
    "models": [
      {
        "modelName": "model_1",
        "modelPath": "<path_to_model_file>",
        "loadFromCachedBinary": True,
        "inputDataType": "FLOAT",
        "outputPath": "model_1-output",
        "outputDataType": "FLOAT_ONLY"
      }
    ],
    "contexts": [
      {
        "contextName": "htp_context_1"
      }
    ],
      "testCase": {
      "iteration": 1,
      "logLevel": "verbose",
      "threads": [
        {
          "threadName": "htp_thread_1",
          "backend": "htp_backend",
          "context": "htp_context_1",
          "model": "model_1",
          "interval": 0,
          "useRandomData": True,
          "loopUnit": "second",
          "loop": 10,
          "backendConfig":"customParamV1.json"
        }
      ]
    }
}

custom_param_config_v1 = {
    "vtcm_mb":8,
    "dsp_arch":"v69"
}

custom_param_config_v2 = {
    "graphs": {
        "vtcm_mb": 4
    },
    "devices": 
    [{
        "dsp_arch": "v69",
        "cores": 
        [{
            "perf_profile": "low_power_saver"
        }]
    }]
}
