# pa-zhihu

## 环境

 - python 3.3以上
 - gevent
 - lxml
 - requests
 - pymysql
 - mysql
 - sqlite
 - 虽然我写了登陆界面，但是是抄的7sdream的，而且没有多次测试。所以现在登陆的cookie file是用7sdream的[zhihu-py3](https://github.com/7sDream/zhihu-py3)生成的。

## 计划

- 以一个用户的首页为起始页，开始爬用户关注的人。
- 得到每个用户的相关信息
- 得到数据之后聚合分析一下

~~活跃度这个最终还是放弃了，因为时效性太高，而这个项目的初衷是学习爬虫的并发-->得到定制化的数据-->实验数据库-->实验可视化~~


## person

|zhihu-ID(varchar)|username(varchar)|location(varchar)|business(varchar)|gender(int-1,0,1)|company(varchar)|position(varchar)|education(varchar)|major(varchar)|agreed(int)|thanks(int)|answered(int)|asked(int)|posts(int)|collections(int)|public edition(int)|followed(int)|follower(int)|
|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
|he-shi-jun|贺师俊| 上海 |互联网|1|--|--|五角场一流的复黏大学|自由而无用的哲学|18377|3415|758|16|4|3|100|171|18809|

## 还存在的问题

- [ ] 初始化抓取的时候，需要等待第一次抓完
- [ ] 但是第一次抓完之后会直接打印Done，而我并没有设置超时
- [ ] 效率太低，好像给的8个协程一直没用满，大约2秒一个用户
- [ ] 数据写入数据库的时候，好像是同步的，数据量大的时候这个很明显
- [ ] 有时候会停在解析个人首页的状况，按ctrl+c之后就又继续了

## 下一步

- [ ] 如果要做社交网络的实验，还需要在每个人的个人字典中存入followed和follower的链接
- [ ] 试试redis
- [ ] 试试mongoDB