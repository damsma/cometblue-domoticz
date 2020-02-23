"""
<plugin key="cometblue-domoticz" name="Comet Blue radiator valve (cometblue-domoticz)" version="0.0.2">
    <description>
      Simple plugin to manage Comet Blue radiator valve
      <br/>
    </description>
    <params>
        <param field="Address" label="Bluetooth Device Address" width="300px" required="true" default=""/>
        <param field="Mode1" label="Pin-Code" width="300px" required="true" default="00000000"/>
        <param field="Mode2" label="Poll interval" width="300px" required="true" default="120"/>
    </params>
</plugin>
"""
import Domoticz
import re
import datetime
from subprocess import PIPE, run

class BasePlugin:
    def __init__(self):
        self.nextrun = datetime.datetime.now()
        self.pollinterval = 30
        return

    def onStart(self):
        if (int(Parameters["Mode2"]) >= 30):
            self.pollinterval = int(Parameters["Mode2"])

        # Create valve device
        iUnit = -1
        for Device in Devices:
            try:
                if (Devices[Device].DeviceID.strip() == "cometblue-"+str(Parameters["Address"])):
                    iUnit = Device
                    break
            except:
                pass
        if iUnit<0: # if device does not exists in Domoticz, than create it
            try:
                iUnit = 0
                for x in range(1,256):
                    if x not in Devices:
                        iUnit=x
                        break
                if iUnit==0:
                    iUnit=len(Devices)+1
                Domoticz.Device(Name="cometblue-"+str(Parameters["Address"]), Unit=iUnit, DeviceID="cometblue-"+str(Parameters["Address"]), Type=242, Subtype=1, Used=1).Create()
            except Exception as e:
                Domoticz.Debug(str(e))
                return False

        # Create temperature device
        iUnit = -1
        for Device in Devices:
            try:
                if (Devices[Device].DeviceID.strip() == "cometblue-"+str(Parameters["Address"])+"-temp"):
                    iUnit = Device
                    break
            except:
                pass
        if iUnit<0: # if device does not exists in Domoticz, than create it
            try:
                iUnit = 0
                for x in range(1,256):
                    if x not in Devices:
                        iUnit=x
                        break
                if iUnit==0:
                    iUnit=len(Devices)+1
                Domoticz.Device(Name="cometblue-"+str(Parameters["Address"])+"-temp", Unit=iUnit, DeviceID="cometblue-"+str(Parameters["Address"])+"-temp", TypeName="Temperature", Used=1).Create()
            except Exception as e:
                Domoticz.Debug(str(e))
                return False

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

        iUnit = -1
        for Device in Devices:
            try:
                if (Devices[Device].DeviceID.strip() == "cometblue-"+str(Parameters["Address"])):
                    iUnit = Device
                    break
            except:
                pass

        if(str(Command) == "Set Level"):
            #Send bluetooth command
            expCommand = ["heaterControl.exp", str(Parameters["Address"]), str(Parameters["Mode1"]), str(Level)]
            try:
                result = run(expCommand, stdout=PIPE, stderr=PIPE, universal_newlines=True, timeout=30)
            except Exception as e:
                Domoticz.Log("onCommand ERROR: "+ str(e))
                Domoticz.Log("ERROR: Timeout while trying to communicate with device. Make sure the device is on and is in the range.")
                return False
            #print(result.returncode, result.stdout, result.stderr)
            if(str(result.returncode) == "0"):
                Domoticz.Log("New temperature set correctly")
                #print("stdout: "+result.stdout)
                result = re.search(r'Current temperature(.*?) =====', result.stdout).group(1)
                result = result.replace(":", "", 1)
                result = result.replace("°C", "", 1)
                result = result.strip()

                #Update actual setpoint
                Devices[iUnit].Update(nValue=1, sValue=str(Level))

                #Update actual temperature
                iUnit = -1
                for Device in Devices:
                    try:
                        if (Devices[Device].DeviceID.strip() == "cometblue-"+str(Parameters["Address"])+"-temp"):
                            iUnit = Device
                            break
                    except:
                        pass
                Devices[iUnit].Update(nValue=1, sValue=result)

                return True
            else:
                Domoticz.Log("Undefined ERROR!")
                print(result.returncode, result.stdout, result.stderr)
                return False

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")
        now = datetime.datetime.now()

        if (now < self.nextrun):
            Domoticz.Log("Abort - waiting until : "+str(self.nextrun))
            return
        Domoticz.Log("Refreshing data...")
        self.nextrun = (datetime.datetime.now() + datetime.timedelta(seconds=self.pollinterval))

        iUnit = -1
        for Device in Devices:
            try:
                if (Devices[Device].DeviceID.strip() == "cometblue-"+str(Parameters["Address"])):
                    iUnit = Device
                    break
            except:
                pass

        #Send bluetooth command
        expCommand = ["heaterControl.exp", str(Parameters["Address"]), str(Parameters["Mode1"])]

        try:
            result = run(expCommand, stdout=PIPE, stderr=PIPE, universal_newlines=True, timeout=30)
        except Exception as e:
            Domoticz.Log("onCommand ERROR: "+ str(e))
            Domoticz.Log("ERROR: Timeout while trying to communicate with device. Make sure the device is on and is in the range.")
            self.nextrun = datetime.datetime.now()
            return False

        if(str(result.returncode) == "0"):
            #print("stdout: "+result.stdout)
            resultOldSet = re.search(r'Old set temperature(.*?) =====', result.stdout).group(1)
            resultOldSet = resultOldSet.replace(":", "", 1)
            resultOldSet = resultOldSet.replace("°C", "", 1)
            resultOldSet = resultOldSet.strip()

            result = re.search(r'Current temperature(.*?) =====', result.stdout).group(1)
            result = result.replace(":", "", 1)
            result = result.replace("°C", "", 1)
            result = result.strip()

            Domoticz.Log("Actual temperature: "+result)
            Domoticz.Log("Setpoint temperature: "+resultOldSet)

            #Update actual setpoint
            Devices[iUnit].Update(nValue=1, sValue=str(resultOldSet))

            #Update actual temperature
            iUnit = -1
            for Device in Devices:
                try:
                    if (Devices[Device].DeviceID.strip() == "cometblue-"+str(Parameters["Address"])+"-temp"):
                        iUnit = Device
                        break
                except:
                    pass
            Devices[iUnit].Update(nValue=1, sValue=result)

            return True
        else:
            Domoticz.Log("Undefined ERROR!")
            print(result.returncode, result.stdout, result.stderr)
            return False

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
