# 关于ONS的相关算法介绍
## 说明
ONS域名的功能是是实现，把区块链和生活中复杂和杂乱无章的一些hash等通过域名的方式，使其方便记忆。ONS域名的注册规则为：每个钱包地址，最多可以领取：一个大于4位的域名、2个4位数的域名、2个3位数的域名。2位数和1位数的域名暂时保留。
大于4位数的免费领取，4位数的域名领取规则：累计邀请2个人注册可以领取1个（只有一次机会）,累计捐赠2个ONT也可以领取一个（只有一次机会）。3位数域名的领取额规则为：累计邀请8个人可以领取一个（只有一次机会）,累计捐赠8个ONT可以领取一个（只有一次机会）。

域名的规则：域名的长度范围为1-32位小写字母加数字。根域名为：ont。例如：test123.ont，上述长度范围为test123的长度。

## 域名的hash算法

一个域名对应的算法为 sha256累计计算，例如:test123.ont对应的域名hash的计算规则为：前置定义sha256返回的是str ***domainhash = sha256( bin(sha256("ont") + bin("test123")) )***

## 前置状态码说明
### 操作码
名称 | 对应操作 | 值
|:---|:---|:---|
OP_REGISTER | 注册域名 | 1
OP_DROP | 销毁域名 | 2
OP_TRANFER | 转移域名 | 3
OP_SETRESOLVE | 设置域名解析 | 4
OP_DONAT | 捐赠操作 | 5

### 状态码
名称 | 对应状态| 值 (16进址值)
|:---|:---|:---|
ERR_EXITDOMAIN | 域名早已被注册 | 11(0xB)
ERR_YOUHAVE | 已经达到当前领取条件的上限 | 12(0xC)
ERR_YOUNOTHAVE | 你不拥有该域名 | 13(0xD)
ERR_OK | 操作成功 | 14(0xE)
ERR_INVIA_ZM | 域名中包含不允许的字符 | 15(0xF)
ERR_DOMAIN_LENGTH | 域名长度不符合规范 | 16(0x10)
ERR_NOAUTH | 越权操作 | 17(0x11)
ERR_ONT_NO | 账户ont不足 | 18(0x12)
ERR_YOU_NOT_HAVE | 当前根域名不属于你 | 19(0x13)

## 接口的详细说明
ons v0.1 包含以下接口：

名称 | 函数 
|:---|:---|
注册域名 | **Register**
解析域名| ***Resolve***
设置域名解析 | **SetResolve**
转移域名 | **Transfer**
销毁域名 | **Drop**
捐赠 | **Donat**
合约初始化 | **Init**
得到用户的捐赠数 | **GetDonatCountForUser**
得到用户的邀请数 | **GetInvitCountForUser**
得到域名的注册者 | **GetDomainReg**
升级合约 | **MigrateContract**

### 注册域名接口（Register）

该接口定义 ***Register(who, name, roothash, inviter)***

参数说明：

参数名称 | 说明 | 类型
|:---|:---|:---|
who | 调用者自身的scripthash| bytes
name | 域名名称，例如test123.ont 注册的name为test123|str
roothash | 根域名的hash，例如test123.ont的根为ont,这里的值为 ***sha256("ont")***|bytes
inviter | 邀请者的scripthash | bytes

#### 合约执行的结果
合约执行的结果Notify定义: ***[OP_CODE, stateCode, regAddress, domainname, roothash, domainhash, inviter]***

说明：

参数名称 | 说明 | 类型
|:---|:---|:---|
OP_CODE | 当前操作码这里是注册，操作码固定为：***OP_REGISTER***|整形
stateCode | 结果状态码 |整形
regAddress | 注册者的scripthash | hexstr
domainname | 注册的域名名称如注册test123.ont,这里返回的值为test123 | hexstr
roothash | 根域名hash | hexstr
domainhash | 域名hash | hexstr
inviter | 邀请者的scripthash | hexstr

### 域名解析
该接口定义 ***Resolve(domainhash, protocol)***
***该接口为读取接口，并不需要上链执行，利用预执行，就能立即得到结果。调用后的返回值即为结果***
参数说明：

参数名称 | 说明 | 类型
|:---|:---|:---|
domainhash | 查询域名的hash |bytes
protocol | 解析协议（见设置域名解析里面的协议定义） | 整形

### 设置域名解析(SetResolve)
该接口定义 ***SetResolve(who, domainhash, protocol, content)***

参数说明：

参数名称 | 说明 | 类型
|:---|:---|:---|
who | 调用者自身的scripthash| bytes
domainhash | 域名hash|bytes
protocol | 协议定义码|整形
content | 设置的解析内容 | 任意类型

##### protocol 定义
名称 | 说明 |值
|:---|:---|:---|
PROTOCOL_ADDRESS | 解析ONT钱包地址|1
PROTOCOL_ONTID | 解析ONTID地址|2
PROTOCOL_NAME | 解析自己名字|3
PROTOCOL_INFO | 解析任何内容（文字信息）|4
PROTOCOL_EMAIL | 解析电子邮件地址|5
PROTOCOL_PHONE | 解析电话号码|6

#### 合约执行的结果
合约执行的结果Notify定义: ***[OP_SETRESOLVE, stateCode, who, domainhash, protocol, content]***

说明：

参数名称 | 说明 | 类型
|:---|:---|:---|
OP_CODE | 当前操作码这里是设置解析，操作码固定为：***OP_SETRESOLVER***|整形
stateCode | 结果状态码 |整形
who | 捐赠者的scripthash | hexstr
domainhash | 域名hash | hexstr
protocol | 协议 | 整形
content | 内容 | hexstr



### 转移域名（Transfer）
该接口定义 ***Transfer(send, recv, domainhash)***

参数说明：

参数名称 | 说明 | 类型
|:---|:---|:---|
send | 调用者自身的scripthash| bytes
recv | 接受者的scripthash|bytes
domainhash | 域名的hash|bytes

#### 合约执行的结果
合约执行的结果Notify定义: ***[OP_TRANFER, stateCode, who, recv, domainhash]***

说明：

参数名称 | 说明 | 类型
|:---|:---|:---|
OP_CODE | 当前操作码这里是销毁，操作码固定为：***OP_TRANFER***|整形
stateCode | 结果状态码 |整形
who | 捐赠者的scripthash | hexstr
recv | 接收者scripthash | hexstr
domainhash | 域名hash | hexstr

### 销毁域名 (Drop)
该接口定义 ***Drop(who, domainhash)***

参数说明：

参数名称 | 说明 | 类型
|:---|:---|:---|
who | 调用者自身的scripthash| bytes
domainhash | 域名的hash|bytes

#### 合约执行的结果
合约执行的结果Notify定义: ***[OP_DROP, stateCode, who, domainhash]***

说明：

参数名称 | 说明 | 类型
|:---|:---|:---|
OP_CODE | 当前操作码这里是销毁，操作码固定为：***OP_DROP***|整形
stateCode | 结果状态码 |整形
who | 捐赠者的scripthash | hexstr
domainhash | 销毁的域名hash | hexstr


### 捐赠 （Donat）
该接口定义 ***Donat(who, value)***

参数说明：

参数名称 | 说明 | 类型
|:---|:---|:---|
who | 调用者自身的scripthash| bytes
value | 捐赠数量|整形


#### 合约执行的结果
合约执行的结果Notify定义: ***[OP_DONAT, stateCode, who, amount]***

说明：

参数名称 | 说明 | 类型
|:---|:---|:---|
OP_CODE | 当前操作码这里是捐赠，操作码固定为：***OP_DONAT***|整形
stateCode | 结果状态码 |整形
who | 捐赠者的scripthash | hexstr
amount | 数量 | 整形


### 得到用户的捐赠数
该接口定义 ***GetDonatCountForUser(who)***
***该接口为读取接口，并不需要上链执行，利用预执行，就能立即得到结果。调用后的返回值即为结果***
参数说明：

参数名称 | 说明 | 类型
|:---|:---|:---|
who | 用户的scripthash |bytes

### 得到用户的邀请数
该接口定义 ***GetInvitCountForUser(who)***
***该接口为读取接口，并不需要上链执行，利用预执行，就能立即得到结果。调用后的返回值即为结果***
参数说明：

参数名称 | 说明 | 类型
|:---|:---|:---|
who | 用户的scripthash |bytes


### 得到域名的注册者
该接口定义 ***GetDomainReg(domainhash)***
***该接口为读取接口，并不需要上链执行，利用预执行，就能立即得到结果。调用后的返回值即为结果***
参数说明：

参数名称 | 说明 | 类型
|:---|:---|:---|
domainhash | 域名hash |bytes