# PlistUnpacker
在网上没有找到支持多边形裁剪的plist还原工具，不得已自己写了个，可以完美还原出散图。

可以将plist或json文件还原成散图，支持Polygon，支持中文路径。

### 环境要求
Python3.4 以上
```
pip install Pillow
pip install numpy
pip install opencv-python
``` 

### 使用方式
#### 命令行执行：
<code>python plistUnpacker.py [Directory or xxx.plist|xxx.json]</code>
