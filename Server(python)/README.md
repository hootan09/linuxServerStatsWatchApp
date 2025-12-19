### Linux Monitor Status

```sh
python -m venv env
source env/bin/activate
pip install fastapi uvicorn

#Run:
python main.py
```


#### Fetch Data (http://localhost:8000/stats): 
```json
{"time":"15:04:22","bat":0,"cpu":1.2,"memUsed":719,"memTotal":15898,"diskTotal":"1007G","diskUsed":"7.2G","diskAvail":"949G","homeFree":"949G","uptime":"23m","load":"0.54 0.33 0.18","net":{"iface":"eth0","rx":109.0,"tx":2.1},"procs":45,"temp":0}
```