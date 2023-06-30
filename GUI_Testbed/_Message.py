

class _Message:

    #largest hex value corresponding to a message
    _LARGEST_MESSAGE_VALUE = 0x08
    
    #init messages
    INIT_SUCCESS = 0x00
    INIT_FAIL = 0x01

    #exit messages
    EXIT = 0x02
    
    #print messages
    PRINT_TO_TERMINAL = 0x03

    #TI radar operation messages
    START_SENSOR = 0x04
    STOP_SENSOR = 0x05
    SEND_CONFIG = 0x06
    LOAD_NEW_CONFIG = 0x07

    #New Data Available
    NEW_DATA = 0x08


    def __init__(self,type,value = None):
        
        #check message type
        self.type = type
        if type > _Message._LARGEST_MESSAGE_VALUE:
            raise InvalidMessageType(type)
        pass

        #set message value
        self.value = value

class InvalidMessageType(Exception):

    def __init__(self,message_type):
        self.message = "{} is not a valid message type".format(message_type)
        super().__init__(message_type)