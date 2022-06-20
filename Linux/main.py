from arc_logger import ArcLoggerLevel,ArcLogger
import platform
from datetime import datetime
import os
import subprocess
import json
from shutil import make_archive
import socket

timestamp_format = "%Y-%m-%d %H-%M-%S"
#workdir = "/tmp/azcmagent-troubleshooter-{}-{}".format(datetime.datetime.now().strftime(timestamp_format),platform.node())
workdir = "C:\\Users\\omerroth\\AppData\Local\\Temp\\azcmagent-troubleshooter-{}-{}".format(datetime.now().strftime(timestamp_format),platform.node())
troubleshooter_log = workdir + "\\troubleshooter.log"
#troubleshooter_log = workdir + "/troubleshooter.log"


def initialize_script() -> None:

    # check if himds service installed on Linux machine
    # If not, exit 
    if not os.system("systemctl is-active --quiet himdsd.services"):
        print("\u001b[31;1mCould not find himds service on machine, please make sure Azure Connected Machine Agent is installed")
        exit -1

    try:
        # Create work folder
        os.makedirs(workdir)
    
        # Create instance of logger
        global logger
        logger = ArcLogger(troubleshooter_log)

    except Exception as e:
        print("\u001b[31mFailed to initialize script: {}\u001b[0m".format(e))
        exit -1
    
def show_agent_details() -> None:
    show_cmd = "azcmagent show -j"

    try:
        logger.writeLineToLog(ArcLoggerLevel.Debug,"AgentDetails","running command: \"{}\"".format(show_cmd))
        raw_agent_details = str(subprocess.run(show_cmd.split(), stdout=subprocess.PIPE).stdout)

        agent_details = json.loads(raw_agent_details.replace("\\n","\n")[2:-2])

    except Exception as e:
        logger.writeLine(ArcLoggerLevel.Error,"AgentDetails","Failed to run command \"{}\". Error: {}".format(show_cmd,e))
        return
    
    logger.writeLine(ArcLoggerLevel.Info,"AgentDetails","Azure Connected Machine Agent Details")
    logger.writeLine(ArcLoggerLevel.Info,"AgentDetails","-"*37)
    logger.writeLine(ArcLoggerLevel.Info,"AgentDetails","Machine Name:\t\t{}".format(agent_details["resourceName"]))
    logger.writeLine(ArcLoggerLevel.Info,"AgentDetails","Version:\t\t{}".format(agent_details["agentVersion"]))
    logger.writeLine(ArcLoggerLevel.Info,"AgentDetails","Region:\t\t\t{}".format(agent_details["location"]))
    logger.writeLine(ArcLoggerLevel.Info,"AgentDetails","State:\t\t\t{}".format(agent_details["status"]))
    
    if agent_details["httpsProxy"]:
        logger.writeLine(ArcLoggerLevel.Info,"AgentDetails","HTTP Proxy:\t\t\t{}".format(agent_details["httpsProxy"]))

        if agent_details["proxyBypass"]:
            logger.writeLine(ArcLoggerLevel.Info,"AgentDetails","Proxy Bypass:\t\t\t\t{}".format(agent_details["proxyBypass"]))
        else:
            logger.writeLineToLog(ArcLoggerLevel.Info,"AgentDetails","Proxy Bypass:\t\t\t\tnot configured")
    else:
        logger.writeLineToLog(ArcLoggerLevel.Info,"AgentDetails","HTTP Proxy:\t\t\tnot configured")

    if agent_details["agentErrorCode"]:
        logger.writeLine(ArcLoggerLevel.Warn,"AgentDetails","Agent Error:\t{}: {}".format(agent_details["agentErrorCode"],agent_details["agentErrorDetails"]))
    
    # Print services to console, unlike PS, we don't auto formatting so we do it manually.
    logger.writeLineToConsole(ArcLoggerLevel.Info,"\nServices:",True)

    logger.writeLineToConsole(ArcLoggerLevel.Info,"{:<20} {:<20} {:<8}".format("Display Name","Service Name","State"),True)
    for row in agent_details["services"]:
        logger.writeLineToConsole(ArcLoggerLevel.Info,"{:<20} {:<20} {:<8}".format(row["displayName"],row["serviceName"],row["status"]),True)
    
    services_table_parse = lambda row: "Service: {} ({}): {}".format(row["displayName"],row["serviceName"],row["status"])
    logger.writeTableToLog(ArcLoggerLevel.Info,"AgentDetails",agent_details["services"],services_table_parse)


    global agent_region
    agent_region = agent_details["location"]

def collect_arc_logs() -> None:
    zip_name = F"{workdir}/azcmagent-logs-{datetime.now().strftime(timestamp_format)}-{platform.node()}.zip"
    zip_cmd = F"azcmagent logs -o {zip_name}"

    logger.writeLineToLog(ArcLoggerLevel.Debug,"ArcLogsCollector",F"Running command: {zip_cmd}")

    try:
        result = subprocess.run(zip_cmd.split(),capture_output=True, text=True)
        if result == 0:
            logger.writeLine(ArcLoggerLevel.Info,"ArcLogsCollector","Arc logs collected successfully")
        else:
            # slice specific to the way azcmagent logs output errors
            raise result.stdout.split("=")[-1]
    except Exception as e:
        logger.writeLine(ArcLoggerLevel.Error,"ArcLogsCollector",F"Failed to collect arc logs. Reason: {e}")

def network_check() -> None:
    logger.writeLineToLog(ArcLoggerLevel.Debug,"NetworkCheck","Perfrming network check")

    try:
        dns_addr = "gbl.his.arc.azure.com"
        # Check if the host server is defined to use a private link by resolving the DNS address for his.
        # If the address resolves to 10.x.x.x or 172.x.x.x then we're running in a private link environment.
        logger.writeLineToLog(ArcLoggerLevel.Debug,"NetworkCheck",F"Resolving DNS for \"{dns_addr}\" to determine if there's a use of Private Link")
        his_ip = socket.gethostbyname(dns_addr)

        if his_ip[0:2] in ("10","172"):
            logger.writeLineToLog(ArcLoggerLevel.Debug,"NetworkCheck","Private Link detected, will use --use-private-link flag")

            network_cmd = F"azcmagent check --location {agent_region} -j --use-private-link"
        else:
            logger.writeLineToLog(ArcLoggerLevel.Debug,"NetworkCheck","Private Link not found.")
            network_cmd = F"azcmagent check --location {agent_region} -j"

        logger.writeLineToLog(ArcLoggerLevel.Debug,"Networkcheck",F"Running command \"{network_cmd}\".")
        
        result = subprocess.run(network_cmd.split(),capture_output=True, text=True)

        if result.returncode != 0:
            # Slice specific to the stderr of 'azcmagent check' command.
            # Will return the msg of last line in the error 
            raise result.stderr.split('\n')[-2].split('=')[-1].replace('"',"")

        output = json.loads(result.stdout)    
        logger.writeLineToConsole(ArcLoggerLevel.Info,"Network Check:",True)
        parse_cmd = lambda row: "{:<55} {:<15} {:<15} {:<15} {:<25}".format(row["endpoint"],row["reachable"],row["private"],row["tls"],row["proxy status"])

        logger.writeLineToConsole(ArcLoggerLevel.Info,"{:<55} {:<15}  {:<15}  {:<15}  {:<25}".format("Endpoint","Reachable","isPrivate","TLS Version","Proxy Bypass"),True)
        for row in output:
            logger.writeLineToConsole(ArcLoggerLevel.Info,parse_cmd(row),True)
        
        logger.writeTableToLog(ArcLoggerLevel.Info,"NetworkCheck",output,parse_cmd)

    except Exception as e:
        logger.writeLine(ArcLoggerLevel.Error,"NetworkCheck",F"Failed to check network. Reason: {e}")

def collect_extensions() -> None:
    #extensions_reports_dir = "/var/lib/GuestConfig/extension_reports"
    extensions_reports_dir = "C:\\ProgramData\\GuestConfig\\extension_reports"

    logger.writeLineToLog(ArcLoggerLevel.Debug,"ExtensionReport",F"Collecting extension reports from: {extensions_reports_dir}")

    try:
        logger.writeLine(ArcLoggerLevel.Info,"ExtensionReport","Found Extensions:")
        parse_cmd = lambda row: F""
        logger.writeLine(ArcLoggerLevel.Info,"ExtensionReport","Found Extensions:")
        for file in os.listdir(extensions_reports_dir):
             with open(file,'r') as content:
                report = json.load(content)



    except Exception as e:
        logger.writeLine(ArcLoggerLevel.Error,"ExtensionReport",F"Failed to collect extension reports. Reason: {e}")




# Start Main
initialize_script()

show_agent_details()