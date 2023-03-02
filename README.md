# PlistUnpacker
在网上没有找到支持多边形裁剪的plist还原工具，不得已自己写了个，参考了两个网友的代码，可以完美还原出散图。

根据TexturePacker打包的plist文件还原成散图，支持Polygon，支持中文路径。

### 环境要求
Python3.4 以上
```
pip install PIL
pip install numpy
pip install cv2
``` 

### 使用方式
#### 命令行执行：
<code>python plistUnpacker.py [Directory or xxx.plist]</code>

### 遇到问题？
推荐提issue，如果你很着急也可以直接联系我，vx:wxid_v6nucdk1jq8122
