from multiprocessing import Pipe,connection
from _Message import _Message
import json
import os

class _BackgroundProcess:
    def __init__(self,
                 process_name,
                 conn:connection.Connection,
                 config_file_path = 'config_RADAR.json'):
        """Initialization process for all background processes

        Args:
            process_name (str): the name of the process
            conn (connection): connection to the parent process (RADAR)
            config_file_path (str, optional): path to the RADAR config file. Defaults to 'config_RADAR.json'.
        """
        
        #processes exit flag (call from RADAR to exit the process)
        self.exit_called = False
        
        #save process name
        self._process_name = process_name
        
        #establish connection to the parent class (radar)
        self._conn_RADAR = conn
        
        #get the Radar class configuration as well
        try:
            self.config_Radar = self._ParseJSON(config_file_path)
        except FileNotFoundError:
            print("{}.__init__: could not find {} in {}".format(self._process_name, config_file_path,os.getcwd()))
            return
        
        return
    
    def _ParseJSON(self,json_file_path):
        """Read a json file at the given path and return a json object

        Args:
            json_file_path (str): path to the JSON file

        Returns:
            _type_: json
        """
        
        #open the JSON file
        f = open(json_file_path)
        content = ''
        for line in f:
            content += line
        return json.loads(content)
    
    def _conn_send_init_status(self,init_success:bool = True):
        
        #determine which message to send
        if init_success == True:
            msg = _Message(_Message.INIT_SUCCESS)
        else:
            msg = _Message(_Message.INIT_FAIL)
        
        self._conn_RADAR.send(msg)
    
    def _conn_send_message_to_print(self,message:str):
        """Send a message to the Radar object to print on the terminal

        Args:
            message (str): The message to be printed on the terminal
        """
        self._conn_RADAR.send(_Message(_Message.PRINT_TO_TERMINAL,message))

    def run(self):
        pass

    def close(self):
        pass