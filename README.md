# pa-zhihu

## 环境

 - python 3.3以上
 - gevent
 - lxml
 - requests
 - pymysql
 - mysql
 - sqlite
 - 登陆界面，是模仿的7sdream的[zhihu-py3](https://github.com/7sDream/zhihu-py3)。

## 20160909更新

又重新修复了一下，错误处理比较多，应该算是一个能跑的代码了吧。

这次主要是添加了`mongodb`，另外当初打算的`mysql`就不折腾了。

这次的主要目的是想在树莓派上跑，现在来看已经打到目的了。

`mongodb`的是`single2`，`sqlite`是`single`，但是因为`webParser`有修改，所以有点不兼容`sqlite`了。

这个项目本来是实验多协程的，但是知乎一直给429，一次也就能跑三个协程，后来还是算了，但是一个慢慢跑吧，也就不给服务器平添压力了。反正我也不在乎时间。
