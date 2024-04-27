SIG_SEND_HEART_BIT = "PCHeartBit"
SIG_RECV_HEART_BIT = "PLCHeartBit"
SIG_RECV_PSN = "PLCPSNData"
SIG_RECV_MODEL = "PLCVehicleModelData"
SIG_RECV_CHASSIS = "PLCChassisData"
SIG_RECV_START_TRIGGER = "PLCStartTrigger"
SIG_RECV_END_TRIGGER = "PLCEndTrigger"

PLC_SIGNALS = [
	{
		"key": SIG_RECV_HEART_BIT,
		"type": "int",
		"pos": None,
	},
    {
		"key": SIG_RECV_START_TRIGGER,
		"type": "bool",
		"pos": 18,
	},
    {
		"key": SIG_RECV_END_TRIGGER,
		"type": "bool",
		"pos": 19,
	},
	{
		"key": SIG_RECV_PSN,
		"type": "int",
		"pos": 0,
	},
    {
		"key": SIG_RECV_MODEL,
		"type": "str",
		"pos": 24,
		"size": 12,
	},
    {
		"key": SIG_RECV_CHASSIS,
		"type": "str",
		"pos": 6,
		"size": 17,
	},
    {
		"key": SIG_SEND_HEART_BIT,
		"type": "int",
		"pos": None,
	},
]

PLC_SIGNAL_LOOKUP = {x["key"]: x for x in PLC_SIGNALS}
