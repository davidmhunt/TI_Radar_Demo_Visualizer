import sys
import os
import serial
import time
from _Background_Process import _BackgroundProcess
from multiprocessing import Pipe,connection
from _Message import _Message

class CLIController(_BackgroundProcess):
    """The controller class handles CLI command and control with the radar
    """

    def __init__(
            self,
            conn:connection,
            config_file_path='config_CLI_Controller.json'):
        """Initialize the controller class

        Args:
            config_file_path (str): _description_
        """
        super().__init__("CLI_Controller",
                       conn,
                       config_file_path)       

        #load the class variables
        self.TI_Radar_config_path = self.config_Radar["TI_Radar_config_path"]
        self.verbose = self.config_Radar["CLI_Controller"]["verbose"]

        #initialize the serial port
        try:
            self.CLI_port = serial.Serial(self.config_Radar["CLI_Controller"]["CLI_port"],115200,timeout=30e-3)
        except serial.SerialException:
            print("CLI_Controller.__init__:could not find serial port{}".format(self.config_CLI_Controller["CLI_port"]))
            self._conn_send_init_status(init_success=False)
            return
        
        #send configuration file to the device
        self.sensor_running = False

        #send successful init status if successful
        self._conn_send_init_status(init_success=True)
        self.run()

        return

    def run(self):
        try:
            while self.exit_called == False:
                msg = self._conn_RADAR.recv()
                self._process_Radar_command(msg)

            #once exit is called close out and return
            self.close()
        except KeyboardInterrupt:
            self.close()
            sys.exit()
    
    def close(self):
        #before exiting, close the serial port and turn the sensor off
            if self.CLI_port.is_open == True:
                #turn the sensor off
                if self.sensor_running == True:
                    self.serial_send_stop_sensing()

                #close the serial port
                self.CLI_port.close()
    
    def serial_send_config(self):
        """Send the TI Radar configuration over serial, but do not start radar sensing
        """
        
        #load in the TI Radar config file
        try:
            config = [line.rstrip('\r\n') for line in open(self.TI_Radar_config_path)]
        except FileNotFoundError:
            print("CLI_Controller.send_config:could not find {}".format(self.TI_Radar_config_path))
            return

        #send every command except for the sensor start command
        for command in config:
            if(command != "sensorStart"):
                self._serial_send_command(command)
            #don't send a sensor start command
            elif (command == "sensorStart"):
                if self.verbose:
                    self._conn_send_message_to_print("Config.sendConfigSerial: 'sensorStart' in config file. Skipping sensorStart command")
    
    def serial_send_start_sensing(self):
        """Send the sensorStart command to the sensor to begin sensing
        """
        self._serial_send_command("sensorStart")
        self.sensor_running = True

    def serial_send_stop_sensing(self):
        """Send the sensorStop command to the sensor to halt sensing
        """
        self._serial_send_command("sensorStop")
        self.sensor_running = False
    
    def _serial_send_command(self,command):
        """Send a given command string over serial

        Args:
            command (str): the command to send to the TI Radar
        """
        #send the command over serial
        self.CLI_port.write((command+'\n').encode())

        #get the response from the sensor to confirm message was received
        resp = self.CLI_port.read_until("mmwDemo:/>").decode('utf-8')
        #resp = " ".join(resp)
        if self.verbose:
            #print sent command
            self._conn_send_message_to_print("CLI_sent:/>{}".format(command))

            #print received command
            resp = resp.split("\n")
            resp.reverse()
            resp = " ".join(resp).strip("\r")
            self._conn_send_message_to_print(resp)
        return

    def _process_Radar_command(self,command:_Message):
        
        match command.type:
            case _Message.EXIT:
                self.exit_called = True
            case _Message.START_SENSOR:
                self.serial_send_start_sensing()
            case _Message.STOP_SENSOR:
                self.serial_send_stop_sensing()
            case _Message.SEND_CONFIG:
                self.serial_send_config()
            case _Message.LOAD_NEW_CONFIG:
                print("CLI_Controller._process_Radar_command: LOAD_NEW_CONFIG not enabled yet")
                pass
            case _:
                print("CLI_Controller._process_Radar_command: command not recognized")