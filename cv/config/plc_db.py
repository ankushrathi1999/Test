SIG_SEND_HEART_BIT = "PCHeartBit"
SIG_SEND_RESULT_MID1 = "PCResultMID1"
SIG_SEND_RESULT_MID2 = "PCResultMID2"
SIG_SEND_START_TRIGGET_ACK = "PCStartTriggerAck"
SIG_SEND_END_TRIGGET_ACK = "PCEndTriggerAck"
SIG_RECV_HEART_BIT = "PLCHeartBit"
SIG_RECV_PSN = "PLCPSNData"
SIG_RECV_MODEL = "PLCVehicleModelData"
SIG_RECV_CHASSIS = "PLCChassisData"
SIG_RECV_COLOR = "PLCColorData"
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
		"key": SIG_RECV_COLOR,
		"type": "str",
		"pos": 46,
		"size": 3,
	},
    {
		"key": SIG_SEND_HEART_BIT,
		"type": "array",
		"headdevice": "D16075",
	},
    {
		"key": SIG_SEND_RESULT_MID1,
		"type": "array",
		"headdevice": "D16051",
	},
    {
		"key": SIG_SEND_RESULT_MID2,
		"type": "array",
		"headdevice": "D16151",
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
