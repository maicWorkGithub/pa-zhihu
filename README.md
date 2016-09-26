# pa-zhihu

## 环境

 - python 3.3以上
 - gevent(现在不需要了)
 - lxml
 - requests
 - pymysql(现在不需要了)
 - pymongo
 - 登陆界面，是模仿的7sdream的[zhihu-py3](https://github.com/7sDream/zhihu-py3)。

## 20160909更新

**只能使用邮箱帐号登录**

折腾了好久, 之前的就不说了吧。

这个项目本来是实验多协程的，但是知乎一直给429，一次也就能跑三个协程，后来还是算了，但是一个慢慢跑吧，也就不给服务器平添压力了。反正我也不在乎时间。

运行程序是进入到`pzhihu`文件夹, 然后`python3 single2.py`

之所以会起1,2,3类的名字是想记录版本,大家见谅...


## 更新

- 2016-09-11（下午）直接还有这样的【该用户暂时被反作弊限制，0秒后跳转到知乎首页】，关键是页面上只有一个这玩意，又跪了。真的给知乎跪了
- 2016-09-11（晚上）如果连续三分钟没有存储任何人物信息，就中断爬虫，并发送邮件提醒[这个还没做]（一个账号被封的经验总结）
- 2016-09-25 lxml在解析[这个页面](https://www.zhihu.com/people/光明) 的时候一直`etree.XMLSyntaxError: switching encoding: encoder error`, 现在不知道怎么解决, 还是用回了`BeautifulSoup`, 累~~
- 2016-09-25 (晚上) 打包成package(~~我要开始装逼了~~)

