
## TimeWatcher

> Automatically update hours card on TimeWatch

Python CLI program to help you automate filling up Timewatch card.
Integrate with `cronjob` to make this fully automated process every month.

## Usage

First install the package to your machine
```bash
pip install timewatcher
```
And execute the program when you want to fill the time
```bash
timewatcher
```
The first time you run it, you will go through the process of setting up the configuration file.
![enter image description here](https://i.ibb.co/wLdF0Tb/Screenshot-2024-02-11-at-0-51-33.png)
After you set it up for the first time, it will be save to `~/Library/Preferences/TimeWatcher/config.ini` and it can be changed in any time.

### Configuration

This is the list of the user configuration options:
- `company_number`- Mandatory, your company number in Timewatch
- `employee_number` - Mandatory, you employee number used in Timewatch
- `employee_password` - Mandatory, password used to Timewatch, by default this is your ID number
- `start_time` - Optional, the time to set as your start time in Timewatch. Default to 0900 (9 A.M)
- `end_time` - Optional, the time to set as your end time in Timewatch. Default to 1800 (6 P.M)
- `auto_end_time` - Optional, if set to `True` it will calculate the `end_time` based on the needed hours for each date in Timewatch. This mean the program can handle half days automatically using this option. The default is `True`.

### Development

If you want to run this program locally, clone the repo to your machine
```bash
https://github.com/birkagal/timewatcher
cd timewatcher
```
Initilize environment using `poetry`
```bash
poetry install --no-root
pre-commit install
```
You can make any changes you want.
To execute run the `timewatcher` command inside the directory
```bash
timewatcher
```
