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

Linux:
* Python 3.
* run script as root.

## How to use
Windows:
1. Save the script to a directory of your choice.
4. Execute the script as administrator.
5. When done, the script will generate a zip file under `%TEMP%` which includes all relevant information.

Linux:
1. Save the script to a directory of your choice.
2. Run `main.py` with root permissions.
3. When done, the script will generate a zip file under `/tmp` which includes all relevant information.

## Questions
If you have any questions on how the script works feel free to reach out to me / create an issue in this github.
