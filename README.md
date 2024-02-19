# Connected Machine Troubleshooter Script
Troubleshooter script for Azure Arc enabled servers [connected machine agent (azcmagent)](https://docs.microsoft.com/en-us/azure/azure-arc/servers/agent-overview).

## When to use
* When having issues onboarding azcmagent to Azure Arc.
* When extensions are not reporting correctly.
* When creating a new support ticket for Azure Arc enabled server's support team.

## Requirements
Windows:
* Powershell 5.1+.
* User that can run powershell scripts as administrator.
* This script is unsigned, and so the PowerShell execution policy would have to be set to Unrestricted in order to run it.
   To do this first check the policy with
   `Get-ExecutionPolicy`
   and note the current execution policy, e.g. `RemoteSigned`
   then set the policy temporarily to 
   `Set-ExecutionPolicy "Unrestricted"`
   then run the script and set the policy back to whatever the original noted policy setting was, e.g.
   `Set-ExecutionPolicy "RemoteSigned"`

Linux:
* Python 3.8.
* Run script as root.

## How to use
Windows:
1. Download `AZCMAgent_troubleshooter.ps1` and save it to a directory of your choice.
2. Execute the script as administrator.
3. When done, the script will generate a zip file under `%TEMP%` which includes all relevant information.

Linux:
1. Download `azcmagent_troubleshooter_script.tar.gz` and save it to a directory of your choice.
2. Extract the contents of the tar ball using `tar -xvf azcmagent_troubleshooter_script.tar.gz`.
3. Run `main.py` with root permissions.
4. When done, the script will generate a zip file under `/tmp` which includes all relevant information.

## Questions
If you have any questions on how the script works feel free to reach out to me / create an issue in this github.
