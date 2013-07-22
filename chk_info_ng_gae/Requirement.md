CiMon Requriement
-----

## 1. 概况

乌云站点(wooyun.org)是国内比较知名的漏洞报告平台，每天会有大量的报告，对于上面的信息，需要及时关注，但由于总总原因，不能及时发现，可能造成不必要的影响，因此，需要一个工具定时发现其中的信息。

之前由于此需求，编写本地运行的脚本，但由于不能保证时刻运行，故可用性不强，后编写出基于 google application engine 的版本，可用于部署，经过多次修改，发现在设计中存在较多的问题，需要进行重构。

## 2. 功能

###  2.1  抓取网站的最新信息：  
*  乌云站点
  1）可先获取submit的RSS，如果新增的数量为10，表示更新可能超过10个，信息可能有遗漏，获取url列表
  2）获取submit的“更多”页面，获取更新信息，获取url列表
  3）根据之前的URL列表，获取详细信息
  4）获取“最新公开的信息”，获取
* CNVD
* 
* 自定义的blog
* 微博（数据库设计，不一定实现）

###  2.2  网站监控功能
获取制定的url，记录 返回状态  页面的字符  耗时  页面是否变化（md5、304、）


###  2.3  数据接收功能
提供接口，收集信息（主动提交的）

###  2.2  功能要求
* 邮件内容可以订制（默认为通用模板）
* 发送邮件的频率可以设定
* 支持发送给管理员系统运行状况的报告（紧急及定期）
* 检查系统新版本的功能
* 提交用户建议并汇总(使用‘magic code’激活统计部分，独立模块)
* 查询最新数据的功能（管理员权限）
* 全文检索
* 数据导出的功能，csv格式
* 设计Logo及favcion.ico
* 记录版本变更状况		
* 数据的导入
* 系统运行情况进行记录
* 防止部分URL被非法调用<用refer进行判断>
* 设置抓取数据的频率
* 自定义检查（设置检查的范围，save_id范围，自定义关键字，与查询有点相似）
	

###  2.3  其他要求
* Test First(Test Driven)
* 插件系统，支持扩展 
* L10N（支持多语言）
* 后台支持task queue
* 每一种资源为一个扩展，初始化时，在ResPool中添加一行
	
 
##  3. 界面（URLs）

### 3.1  sitemap


### 3.2  URLs
*  /      		主界面   
*  /am/   		管理界面
*  /am/(signin|signout)   登陆接口
*  /am/proc/(fetch|crawl|)					系统的接口

*  /am/cfg//(add|edit|del)/.*    			最后为主键值
*  /about/(changelog|manual|faq|support) 
*  /data/(browse|search|export)/		    对数据进行操作
*  /stat/									统计及可视化展示

### 3.3  API
*  /api/takoen= & op=  & args= 
*  /sop/task/                               

##  4  业务设计

###  4.1  数据流


##  5  数据库设计

### 5.1  基本类及方法
```
class GDB_BASE(db.Model):
	
	def save(self):
		pass
	
	def list(self):
		pass
	
	def last_renew(self):
		pass
		
	def import(self):
		pass
```

### 5.2  表的设计

```
class ResPool(db.Model):
    name            = db.StringProperty()
    site_type       = db.StringProperty(required=True,choices=set(['wooyun_submit', ]))
    url             = db.StringProperty(required=True)
    last_get_date   = db.DateProperty()
    last_get_status = db.StringProperty(default='200')
    last_save_id    = db.IntegerProperty(required=True)
    # set min check time,void too many times.
    min_gap         = db.StringProperty()
	# such as  ‘Security’,'MicroBlog','Blog'
	type
	

class MonitorConfig(db.Model):
    name            = db.StringProperty(required=True)
    desc            = db.StringProperty()
    site_type       = db.StringProperty(required=True,choices=set(['wooyun_submit',]))
    last_chk_id     = db.IntegerProperty(required=True)
    key_words       = db.StringProperty()

    notice          = db.BooleanProperty(default=True)
    mail_to         = db.StringProperty()
    sent_freq       = db.StringProperty()
    since           = db.DateTimeProperty()
    daily_mail_num  = db.IntegerProperty(default=0)
    total_mail_num  = db.IntegerProperty(default=0)
    total_chk_num   = db.IntegerProperty(default=0)
	# set
	send_time       = db.StringProperty()
    # send one email  everyday or other(at 8am\14pm\16pm). eg: 08:05,16:00    
	summary_mail    = db.BooleanProperty(default=True)
	summary_fraq    = db.StringProperty()

    def get_Mon_Items(self,site_type,):
        # return a list, retime check or summary check.
        pass

class WooyunData(db.Model):
    #'link','title','desc','stauts''pubDate','author','guid'
    # rename 'WooyunData' add 'vuln_type','rank','status'
    # renew date over one month
    guid    = db.StringProperty(required=True)
    link    = db.StringProperty(required=True)
    pub_date= db.DateTimeProperty()
    title   = db.StringProperty()
    desc    = db.TextProperty()
    author  = db.StringProperty()
    detail  = db.TextProperty()
    #choices=set([u'未公开', ])
    status  = db.StringProperty(default=u'暂未公开')
    save_id = db.IntegerProperty()

class BlogData(db.Model):
	
	
class CommonData(db.Model):
	
class DailyStat(db.Model):
    # stat sys run every daily.
    # such as : save_id
    stats_id       = db.StringProperty(required=True)
    stats_at      = db.DateTimeProperty()
    count         = db.IntegerProperty(required=True)
	
class Syslog(db.Model):
	level
	type
    position
	time
	content
	
class Suggest(db.Model):
	# sent magic code to enable this function.
	time
	title
	content
	user_email
	version
	status	
	
```