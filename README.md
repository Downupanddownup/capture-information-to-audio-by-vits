### 项目声明：

​		此项目是基于huggingface网站上[zomehwh](https://huggingface.co/zomehwh)所提供的vits项目[vits-uma-genshin-honkai](https://huggingface.co/spaces/zomehwh/vits-uma-genshin-honkai)，二次开发而来。基于zomehwh的要求，**请勿将模型用于任何商业项目，否则后果自负**。

### 功能介绍

​		此项目可以完成新闻资讯的抓取，管理和音频转换，目前集成了虎嗅首页和观察者网国际新闻两个资讯来源，支持本地txt文件转换，提供了横向扩展资讯来源的插件模块，如果有扩展资讯来源的需求，可以根据二开文档，设计自己的抓取插件。文章数据采用json和txt文件存储，在启动项目之前，请先前往vits-uma-genshin-honkai项目的model目录下，下载config.json和G_953000.pth文件，放入本项目的model（如果没有，就创建一个）目录下。

### 设计初衷

​		上个月，我偶然发现了vits-umagenshin-honkai这个项目，发现它对游戏角色的音色模仿比较出色，尤其是在没有情绪起伏的朗读状态下，接近原角色的朗读效果，于是我就萌生了利用vits的AI模型为自己朗读资讯的想法。

经过大半个月的体验，我得出一个结论：**只要能够获取优质的中文文本资料，那么坐在办公室里，就可以听遍天下奇闻轶事！**

与基于视觉信号进行的文字阅读相比，音频有如下优势：

* 低精力消耗
* 不会阻塞当前行为

​		低精力消耗：我不清楚别人阅读文本的流程是怎样的，但是我是按照查看文章-提取文字-心里默念-分析想象这种顺序进行文本阅读的，而音频可以帮助我直接跳过前三个步骤，直接进行分析与想象，这使我可以听完数篇文章之后，也不会疲劳。当然，如果需要深入分析，还是需要回去结合文章进行精读的，但是只是了解资讯，音频就足以应付大部分情况了。

​		不会阻塞当前行为：当进行文字阅读时，我无法进行其他行为，但是听取音频时不会，这意味着，除了睡觉以外的绝大部分时间，都可以利用音频来获取资讯，这极大的扩展了获取信息的时间。

想象一下如下场景：

1. 每天上下班的时候看近期的新闻事件
2. 发现了一篇好文章，看了一遍觉得还理解的不充分
3. 有些有用，但是自己不一定看得进去的文章或是书籍，比如《毛选》、《置身事内》
4. 其他高耗时，但低精力消耗的场景，比如要做几个小时的火车，可能会看资讯或小说打发时间

这些场景下都可以将文本转换为音频，给自己提供一种更加轻松的资讯获取方式或是娱乐方式

### 转换性能

​		vits支持CPU推理和GPU推理，默认采用CPU，如果有高性能的GPU，推荐使用GPU推理，可将config.yaml中device_type的值，由cpu改为cuda。

| 设备            | 1042个字符转换时间-未开启齿音弱化（秒） |
| --------------- | --------------------------------------- |
| i9-13900HX      | 68                                      |
| RTX 4080 Laptop | 5                                       |

### 安装教程

​		需要安装git、python、ffmepg，如果需要使用GPU推理，还需要配置机器学习环境，安装CUDA和PyTorch，需要注意python和CUDA以及PyTorch的版本之间的对应关系。其他的话，还有不少依赖库，但是忘了是哪些，根据运行时的错误提示安装吧。

### 调整演讲人

​		由于时间有限，没有设计演讲人的界面配置功能，如果有调整演讲人朗读属性的需求，可以在vits这个tab下，尝试需要的朗读参数，点击submit后，会将设置属性打印到窗口中，将这些属性保存到./config/voice.json文件中，就可以调整演讲人的朗读属性了。

### 与ChatGPT协作开发的体验

​		因为此前对于python这门语言的了解，仅限于一些最基础的语法，所以在开发图形界面、设计插件系统、添加资讯内容管理方面遇到了不少需要进行技术可行性验证的问题，在这些问题上，ChatGPT给我提供了巨大的帮助，以前可能会在某个技术的实现方式上，由于没有找对相关文档，导致数个小时都没有进展的情况，大幅减少了，从而可以让我将主要的精力集中在产品功能的业务逻辑的实现上。

​		当然，目前对于ChatGPT的探索依然十分初级，如何让ChatGPT能够像同事一样更加深入的融合到，产品功能的业务逻辑的开发过程中来，还需要研究。

​		以下是ChatGPT帮助我解决的问题：

1. 找到gradio中，更新控件状态的方法
2. 设计一套极简的插件系统，作为参考
3. 实现将vits源码中，转换数据绕过浏览器，直接保存为wav音频的方法
4. 设计一个基础的json文件管理工具
5. 设计一个基础的yaml文件管理工具
6. 实现快速比较两个python对象的属性是否完全一致的方法
7. 实现日期变量的格式转换与比较
8. 如何更好的实现python对象的属性的默认值设置
9. 如何根据字符串变量动态获取python对象的属性与函数
10. 如何将wav音频转换为mp3
11. 如何合并音频
12. 如何消除音频中的齿音
13. java中，常用功能在python中的对应方法
14. 如何匹配文本中的所有英文单词
15. 解决python中的模块引用问题

### 二开文档

​		为了使这个程序具备更好的扩展性，我设计了三类插件：文章抓取插件（articleFetch）、音频转换前，文章内容处理插件（dealWithBeforeConvertAudio）、转换后，音频处理插件（dealWithAfterConvertAudio）。我在项目plugin_demo目录下，提供了三类插件的demo，如有需要可以将它们复制到extensions目录下，重启项目，可以查看插件使用效果。

​		**注意：在开发爬虫时需要遵守网站的 Robots 协议以及相关规定和道德标准，合理控制爬取频率，避免对网站造成负面影响。**

#### 文章抓取插件（articleFetch）

​		设计此插件的目的是，可以通过添加插件的方式，扩展更多的资讯来源

| 接口函数           | 函数说明           | 输入参数                                              | 示例                                                         | 返回参数                           | 示例                                                         |
| ------------------ | ------------------ | ----------------------------------------------------- | ------------------------------------------------------------ | ---------------------------------- | ------------------------------------------------------------ |
| description        | 提供插件的说明     | 无                                                    | 无                                                           | 字符串                             | "获取XXX的资讯"                                              |
| open_param         | 是否启用自定义参数 | 无                                                    | 无                                                           | bool值                             | False                                                        |
| plugin_param_list  | 自定义参数列表     | 无                                                    | 无                                                           | PluginParam数组，见PluginParam说明 | []                                                           |
| fetch_article_list | 抓取文章id列表     | 无                                                    | 无                                                           | 包含文章id的数组                   | [{"id": 11}]                                                 |
| fetch_article      | 抓取文章内容       | article_id<br>article<br>article_list<br>param_values | 11<br/>{"id": 11}<br/>[{"id": 11}]<br/>[{"key":"test","value":11}] | 一个包含文章属性的字典             | {     'article_id': 11,<br>     'title': title,<br/>     'author': '未知', <br/>    'publish_date': '2023年05月02日,     <br/>'content': '内容',<br/>     'link': ‘’,<br/>     'extra': ''} |

#### 音频转换前，文章内容处理插件（dealWithBeforeConvertAudio）

​		设计此插件的目的是，由于本项目只支持中文朗读（实际上也支持日语，但我没处理），所以对于英文单词需要一些特殊处理，这种处理方式不唯一，所以以插件形式开放

| 接口函数                  | 函数说明           | 输入参数                             | 示例                                                         | 返回参数                           | 示例                 |
| ------------------------- | ------------------ | ------------------------------------ | ------------------------------------------------------------ | ---------------------------------- | -------------------- |
| description               | 提供插件的说明     | 无                                   | 无                                                           | 字符串                             | "使用对照表替换英文" |
| open_param                | 是否启用自定义参数 | 无                                   | 无                                                           | bool值                             | False                |
| plugin_param_list         | 自定义参数列表     | 无                                   | 无                                                           | PluginParam数组，见PluginParam说明 | []                   |
| deal_with_article_content | 处理文章内容       | content<br>Article_1<br>param_values | '文章内容'<br/>Article_1对象<br/>[{"key":"test","value":11}] | 字符串                             | '处理后的内容'       |

#### 转换后，音频处理插件（dealWithAfterConvertAudio）

​		设计此插件的目的是，提供音频转换完成之后，可以进行其他处理，比如将转换的音频合并成一个

| 接口函数          | 函数说明           | 输入参数                                                     | 示例                                                         | 返回参数                           | 示例       |
| ----------------- | ------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ---------------------------------- | ---------- |
| description       | 提供插件的说明     | 无                                                           | 无                                                           | 字符串                             | "合并音频" |
| open_param        | 是否启用自定义参数 | 无                                                           | 无                                                           | bool值                             | False      |
| plugin_param_list | 自定义参数列表     | 无                                                           | 无                                                           | PluginParam数组，见PluginParam说明 | []         |
| deal_with_audio   | 处理音频           | wav_path_list<br>ArticleVoice_list<br>param_values<br>default_output_path<br>default_audio_format<br> | ['E:\1.wav']<br/>ArticleVoice数组<br/>[{"key":"test","value":11}]<br>'E:\output'<br>'mp3' | 无                                 | 无         |



#### 插件自定义参数（PluginParam）

​		设计自定义参数的目的，是为了让插件的设计具备更多的灵活性，目前支持两类自定义参数：数字输入（Number）和下拉选择（Dropdown）

##### Number参数

| 参数名称   | 参数说明             | 参数示例          |
| ---------- | -------------------- | ----------------- |
| param_type | 参数类型，固定Number | Number            |
| param_key  | 参数key              | test_param_1      |
| label      | 参数说明             | 这是测试参数数字1 |
| value      | 默认数值             | 101               |

##### Dropdown参数

| 参数名称      | 参数说明               | 参数示例                 |
| ------------- | ---------------------- | ------------------------ |
| param_type    | 参数类型，固定Dropdown | Dropdown                 |
| param_key     | 参数key                | test_param_2             |
| label         | 参数说明               | 这是测试参数下拉2        |
| default_value | 默认选中               | 哈哈                     |
| multiselect   | 是否复选               | True                     |
| choices       | 可选项                 | ['呵呵', '哈哈', '花花'] |

















