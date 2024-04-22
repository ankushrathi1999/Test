SIG_SEND_HEART_BIT = "PCHeartBit"
SIG_SEND_DATA_HANDSHAKE_START = "PCReadyToStart"
SIG_SEND_DATA_HANDSHAKE_END = "PCRunning"
SIG_SEND_RESULT = "PCOverallResult"
SIG_SEND_RESULT_TRIGGER = "PCOverallResultTrigger"
SIG_RECV_HEART_BIT = "PLCHeartBit"
SIG_RECV_EMERGENCY_OK = "PLCEmergencyHealthy"
SIG_RECV_DATA = "PLCOverallData"
SIG_RECV_DATA_TRIGGER = "PLCOverallDataTrigger"
SIG_RECV_RESULT_HANDSHAKE_START = "PLCInspectionEndTrigger"
SIG_RECV_RESULT_HANDSHAKE_END = "PLCDataSavedAck"


PLC_SIGNALS = [
	# {
	# 	"key": SIG_SEND_HEART_BIT,
	# 	"type": "bool",
	# 	"offsetByte": 0,
	# 	"offsetBit": 0,
	# },
	# {
	# 	"key": SIG_SEND_HANDSHAKE_START,
	# 	"type": "bool",
	# 	"offsetByte": 0,
	# 	"offsetBit": 2
	# },
	# {
	# 	"key": SIG_SEND_DATA_LOG,
	# 	"type": "bool",
	# 	"offsetByte": 0,
	# 	"offsetBit": 3
	# },
	# {
	# 	"key": SIG_SEND_HANDSHAKE_END,
	# 	"type": "bool",
	# 	"offsetByte": 0,
	# 	"offsetBit": 4
	# },
	# {
	# 	"key": SIG_SEND_RESULT,
	# 	"type": "int",
	# 	"offsetByte": 12,
	# 	"offsetBit": 0
	# },
	# {
	# 	"key": SIG_RECV_HEART_BIT,
	# 	"type": "bool",
	# 	"offsetByte": 14,
	# 	"offsetBit": 0
	# },
    # {
	# 	"key": SIG_RECV_EMERGENCY_OK,
	# 	"type": "bool",
	# 	"offsetByte": 14,
	# 	"offsetBit": 1
	# },
	# {
	# 	"key": SIG_RECV_HANDSHAKE_ACK,
	# 	"type": "bool",
	# 	"offsetByte": 14,
	# 	"offsetBit": 4
	# },
	# {
	# 	"key": SIG_RECV_PART_DATA,
	# 	"type": "str",
	# 	"offsetByte": 16,
	# 	"offsetBit":0
	# },
	# {
	# 	"key": SIG_RECV_PART_TYPE,
	# 	"type": "int",
	# 	"offsetByte": 66,
	# 	"offsetBit":0
	# }
]

PLC_SIGNAL_LOOKUP = {x["key"]: x for x in PLC_SIGNALS}
