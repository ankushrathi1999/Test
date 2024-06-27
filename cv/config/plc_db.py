SIG_SEND_HEART_BIT = "PCHeartBit"
SIG_SEND_RESULT = "PCResult"
SIG_SEND_START_TRIGGET_ACK = "PCStartTriggerAck"
SIG_SEND_END_TRIGGET_ACK = "PCEndTriggerAck"
SIG_RECV_HEART_BIT = "PLCHeartBit"
SIG_RECV_PSN = "PLCPSNData"
SIG_RECV_MODEL = "PLCVehicleModelData"
SIG_RECV_CHASSIS = "PLCChassisData"
SIG_RECV_START_TRIGGER = "PLCStartTrigger"
SIG_RECV_END_TRIGGER = "PLCEndTrigger"

PLC_SIGNALS = [
	{
		"key": SIG_RECV_HEART_BIT,
		"type": "bool",
		"pos": 22,
	},
    {
		"key": SIG_RECV_START_TRIGGER,
		"type": "bool",
		"pos": 20,
	},
    {
		"key": SIG_RECV_END_TRIGGER,
		"type": "bool",
		"pos": 21,
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
		"size": 16,
	},
    {
		"key": SIG_RECV_CHASSIS,
		"type": "str",
		"pos": 6,
		"size": 17,
	},
    {
		"key": SIG_SEND_HEART_BIT,
		"type": "array",
		"headdevice": "D16075",
	},
    {
		"key": SIG_SEND_RESULT,
		"type": "array",
		"headdevice": "D16051",
	},
    {
		"key": SIG_SEND_START_TRIGGET_ACK,
		"type": "array",
		"headdevice": "D16076",
	},
    {
		"key": SIG_SEND_END_TRIGGET_ACK,
		"type": "array",
		"headdevice": "D16077",
	},
]

PLC_SIGNAL_LOOKUP = {x["key"]: x for x in PLC_SIGNALS}
