SIG_SEND_HEART_BIT = "PCHeartBit"
# SIG_SEND_DATA_HANDSHAKE_START = "PCReadyToStart"
# SIG_SEND_DATA_HANDSHAKE_END = "PCRunning"
# SIG_SEND_RESULT = "PCOverallResult"
# SIG_SEND_RESULT_TRIGGER = "PCOverallResultTrigger"
SIG_RECV_HEART_BIT = "PLCHeartBit"
# SIG_RECV_EMERGENCY_OK = "PLCEmergencyHealthy"
SIG_RECV_PSN = "PLCPSNData"
SIG_RECV_MODEL = "PLCVehicleModelData"
SIG_RECV_CHASSIS = "PLCChassisData"
# SIG_RECV_DATA_TRIGGER = "PLCOverallDataTrigger"
SIG_RECV_START_TRIGGER = "PLCStartTrigger"
SIG_RECV_END_TRIGGER = "PLCEndTrigger"
# SIG_RECV_RESULT_HANDSHAKE_START = "PLCInspectionEndTrigger"
# SIG_RECV_RESULT_HANDSHAKE_END = "PLCDataSavedAck"


PLC_SIGNALS = [
	{
		"key": SIG_RECV_HEART_BIT,
		"type": "int",
		"startByte": 0,
        "size": 1,
	},
    {
		"key": SIG_RECV_START_TRIGGER,
		"type": "bool",
		"startByte": 1,
		"size": 1,
	},
    {
		"key": SIG_RECV_END_TRIGGER,
		"type": "bool",
		"startByte": 2,
		"size": 1,
	},
	{
		"key": SIG_RECV_PSN,
		"type": "str",
		"startByte": 3,
		"size": 4,
	},
    {
		"key": SIG_RECV_MODEL,
		"type": "str",
		"startByte": 7,
		"size": 15,
	},
    {
		"key": SIG_RECV_CHASSIS,
		"type": "str",
		"startByte": 22,
		"size": 15,
	},
    {
		"key": SIG_SEND_HEART_BIT,
		"type": "int",
		"startByte": 37,
        "size": 1,
	},
]

PLC_SIGNAL_LOOKUP = {x["key"]: x for x in PLC_SIGNALS}
