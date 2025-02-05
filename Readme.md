# MechSimulator
Mech simulator

## Setup
### Linux
Setup env
```bash
git clone https://github.com/Benjamin-Kilpatrick/mechsimulator.git
cd mechsimulator

python -m venv venv
source ./venv/bin/activate
pip install -r Requirements.txt
```

setup dependancy for docs
```bash
sudo apt-get install doxygen graphviz
```

### Windows
Setup env
```cmd
# todo
```


## Run
```bash
source ./venv/bin/activate
cd bin
python run.py <some job file>
```

## Docs Generation

### Windows
```commandline
doxygen Doxyfile
```
### Linux
```bash
doxygen Doxyfile-linux
```
