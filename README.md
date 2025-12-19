## Mi Watch/Band Linux Status App

### Server
```
cd server
python -m venv env
source env/bin/activate
pip install fastapi uvicorn
python main.py
# Don't forget to replace server address in watch index.ux page
```

### Watch

### 1. Install

```
npm install
npm run start
```

### 2. Build

```
npm run build
npm run release
```

### 3. Watch Mode

```
npm run watch
```
### 4. 代码规范化配置
代码规范化可以帮助开发者在git commit前进行代码校验、格式化、commit信息校验

使用前提：必须先关联git

macOS or Linux
```
sh husky.sh
```

windows
```
./husky.sh
```


## 了解更多

你可以通过我们的[官方文档](https://iot.mi.com/vela/quickapp)熟悉和了解快应用。


![watch app](./Server(python)/app.png)