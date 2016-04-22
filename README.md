# pa-zhihu

## 计划

- 以一个用户的首页为起始页，开始爬用户关注的人。
- 得到每个用户的相关信息
- 得到数据之后聚合分析一下

## 步骤

- 拿到用户URL，从地址得到用户的唯一ID(知乎的)
- 用户首页得到除关注的人之外的所有信息
- 爬用户关注的人的列表, 爬到一堆人的URL
- 重复上面的动作

active level = 两个月内的活动数量，简单的相加，或者回答X3+提问X2+赞同X1

这个有点坑，要看回答，提问，点赞三个页面，而且点赞的页面还没有具体时间



valid level 主要是看是不是死人(比如葛巾...sad)或者马甲(僵尸号), 比如我的小号，就是被过滤的对象

比重依次为: 公共编辑, 收藏, 文章, 回答, 提问, 得到感谢, 关注者, 资料完整度(6个), 得到赞同,

暂时的计算方法是: [1.5, 1.4, 1.3, 1.2, 1.1, 1, 1, 1, 0.9],

等比较几个用户之后, 再给出一个标准线


## MySQL

|ID(auto-increase)|zhihu-ID(varchar)|username(varchar)|location(varchar)|business(varchar)|gender(int-1,0,1)|company(varchar)|position(varchar)|education(varchar)|major(varchar)|agreed(int)|thanks(int)|answered(int)|asked(int)|posts(int)|collections(int)|public edition(int)|followed(int)|follower(int)|focused topic(list)|activity level(int)|valid level(float)|
|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
|1|he-shi-jun|贺师俊| 上海 |互联网|1|--|--|五角场一流的复黏大学|自由而无用的哲学|18377|3415|758|16|4|3|100|171|18809|['前端开发', 'JavaScript', 'CSS', '前端工程师'， 'HTML', 'HTML5', 'nodejs', '中国好声音（电视节目）', '字体', '盛大网络', '字体排印', '两性关系', '中国好歌曲（电视节目）', '知乎社区', '冷知识', '我是歌手（第二季）', '字体设计', '语言', '百姓网', '科学松鼠会', '三体（系列小说）', '编译原理', '编译器', '成人内容', '奇葩说', '58 同城与赶集网合并案', 'AlphaGo']|--|--|

## 最后

这个坑有点大, 而且现在还有点吹牛逼的嫌疑, 23333
我尽量做, 嗯嗯.