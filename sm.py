# 未完成版，未优化，还差点儿设计。2019.3.28 code by 小时候

from ontology.interop.System.Storage import GetContext, Get, Put, Delete
from ontology.interop.System.Runtime import CheckWitness, Notify
from ontology.interop.Ontology.Runtime import Base58ToAddress
from ontology.interop.Ontology.Native import Invoke
from ontology.builtins import sha256, concat, state
from ontology.interop.Ontology.Contract import Migrate

# KyfRoL4cSsWvxMHVGSUBY84BDfgYFPN4mqguG33njxoE5w8Nggeb   smartx 测试
admin = Base58ToAddress("ALoP6KbJgbznkkhSK51E7Bi2GoDJC8wGKv")  # 这里换成scripthash
donataddress = Base58ToAddress("AQyjYLQNRXtjr6cPoru1vpCTwehg6EQPCs")

OntContract = Base58ToAddress("AFmseVrdL9f9oyCzZefL9tG6UbvhUMqNMV")

# user
FREE_DOMAIN = bytearray(b'\x01')
THREE_DONATE_DOMAIN = bytearray(b'\x02')
FOUR_DONATE_DOMAIN = bytearray(b'\x03')

THREE_INVERT_DOMAIN = bytearray(b'\x04')
FOUR_INVERT_DOMAIN = bytearray(b'\x05')

INVITER = bytearray(b'\x06')  # 记录邀请人数
DONATE = bytearray(b'\x07')  # 记录捐赠数量

THREE_FLAG = 8  # 3位数的域名，捐赠门槛
FOUR_FLAG = 2  # 4位数的捐赠门槛

STATE_START = 1  # 是否有资格
STATE_HAVE = 2  # 是否已经使用了资格

# domain 存储方式为：domainhash+下面的枚举=相应的事

ROOT_HASH = bytearray(b'\x01')
REGISTER_ADDRESS = bytearray(b'\x02')
DOMAIN_NAME = bytearray(b'\x03')

DOMAIN_PROTOCOL = bytearray(b'\x04')
# domain  前面的都是预留，下面是关于域名解析要用的,存储方式，domainhash+ DOMAIN_PROTOCOL +type =content解析的值
PROTOCOL_ADDRESS = bytearray(b'\x01')
PROTOCOL_ONTID = bytearray(b'\x02')
PROTOCOL_NAME = bytearray(b'\x03')
PROTOCOL_INFO = bytearray(b'\x04')
PROTOCOL_EMAIL = bytearray(b'\x05')
PROTOCOL_PHONE = bytearray(b'\x06')

# 状态码的定义

# operation code
OP_REGISTER = 1 #注册
OP_DROP = 2 #销毁
OP_TRANFER = 3 #转移域名
OP_SETRESOLVE = 4 #设置解析操作
OP_DONAT = 5 #捐赠操作

# error code
ERR_EXITDOMAIN = 11  #已经被人注册了
ERR_YOUHAVE = 12 #已经达到领取额度上限了
ERR_YOUNOTHAVE = 13 #你不拥有该域名
ERR_OK = 14 #操作成功
ERR_INVIA_ZM = 15  # 域名字母上包含错误的可见字符
ERR_DOMAIN_LENGTH = 16 #域名长度
ERR_NOAUTH = 17 #没有过身份认证
ERR_ONT_NO = 18 #捐赠时，自身ont账户不足
ERR_YOU_NOT_HAVE = 19 #该域名不归你关。
ERR_RECVADDR = 20 #错误的收件人地址

ctx = GetContext()


def Main(operation, arg):
    if operation == "Register":
        if len(arg) != 4:
            return False
        return Register(arg[0], arg[1], arg[2], arg[3])

    if operation == "Resolve":
        if len(arg) != 2:
            return False
        return Resolve(arg[0], arg[1])

    if operation == "SetResolve":
        if len(arg) != 4:
            return False
        return SetResolve(arg[0], arg[1], arg[2], arg[3])

    if operation == "Transfer":
        if len(arg) != 3:
            return False
        return Transfer(arg[0], arg[1], arg[2])

    if operation == "Drop":
        if len(arg) != 2:
            return False
        return Drop(arg[0], arg[1])

    if operation == "Donat":
        if len(arg) != 2:
            return False
        return Donat(arg[0], arg[1])

    if operation == "Init":
        if len(arg) != 1:
            return False
        return Init(arg[0])
    if operation == "GetDomainReg":
        if len(arg) != 1:
            return ""
        return GetDomainReg(arg[0])

    if operation == "GetDonatCountForUser":
        if len(arg) != 1:
            return ""
        return GetDonatCountForUser(arg[0])    

    if operation == "GetInvitCountForUser":
        if len(arg) != 1:
            return ""
        return GetInvitCountForUser(arg[0])

    if operation == "MigrateContract":
        return MigrateContract(arg[0], arg[1], arg[2], arg[3], arg[4], arg[5], arg[6])

    
    return False
#获取域名的注册者
def GetDomainReg(domainhash):
    return GetDomainRegister(domainhash)

def GetDonatCountForUser(who):
    return GetUserDonatNumber(who)

def GetInvitCountForUser(who):
    invitercountkey = concat(who, INVITER)
    invitercount = GetStorage(invitercountkey)
    return invitercount


def Init(who):
    if CheckWitness(admin) == False:
        Notify(["init No",who])
        return False

    initFlag = GetStorage(admin)
    if initFlag == 1:
        Notify(["init alreadly",who])
        return False
    PutStorage(admin, 1)

    roothash = namehash("ont")
    SetDomainRegister(roothash, who)
    Notify(["init ok",roothash,who])

    return True


def MigrateContract(code, needStorage, name, version, author, email, description):
    if CheckWitness(admin) == False:
        return False
    res = Migrate(code, needStorage, name, version, author, email, description)
    if res == False:
        return False
    return True


# 捐赠 参数1：调用者本身  参数2：捐赠的ont数量，ont不可分割，所以必须为整数
def Donat(who, value):
    if CheckWitness(who) == False:
        donatNotify(ERR_NOAUTH, who, value)
        return False

    if transferONT(who, donataddress, value) == False:
        donatNotify(ERR_ONT_NO, who, value)
        return False

    dn = GetUserDonatNumber(who)
    dn = dn + value
    SetUserDonatNumber(who, dn)
    donatNotify(ERR_OK, who, value)
    if dn >= THREE_FLAG:
        stat = GetUserFreeDomainFlag(who, THREE_DONATE_DOMAIN)
        if stat != STATE_HAVE and stat != STATE_START:
            SetUserFreeDomainFlagUse(who, THREE_DONATE_DOMAIN, STATE_START)

    if dn >= FOUR_FLAG:
        stat = GetUserFreeDomainFlag(who, FOUR_DONATE_DOMAIN)
        if stat != STATE_HAVE and stat != STATE_START:
            SetUserFreeDomainFlagUse(who, FOUR_DONATE_DOMAIN, STATE_START)
    return True


# 设置域名的解析,参数1：调用者本身(scripthash) 参数2：需要被设置的域名hash  参数3：设置域名的那个类型的解析  参数4：解析的内容
def SetResolve(who, domainhash, protocol, content):
    if CheckWitness(who) == False:
        setResolveNotify(ERR_NOAUTH, who, domainhash, protocol, content)
        return False

    domainreg = GetDomainRegister(domainhash)

    if who != domainreg:
        setResolveNotify(ERR_YOUNOTHAVE, who, domainhash, protocol, content)
        return False

    domaintmp = concat(domainhash, DOMAIN_PROTOCOL)
    domaincontiankey = concat(domaintmp, protocol)
    PutStorage(domaincontiankey, content)
    setResolveNotify(ERR_OK, who, domainhash, protocol, content)
    return True


# 获取域名解析内容，参数1：需要域名hash 参数2：解析那个类型协议
def Resolve(domainhash, protocol):
    domaintmp = concat(domainhash, DOMAIN_PROTOCOL)
    domaincontiankey = concat(domaintmp, protocol)
    content = GetStorage(domaincontiankey)
    Notify([domaincontiankey,content])
    return content


# 销毁域名,参数1：调用者本身，参数2：域名hash
def Drop(who, domainhash):
    if CheckWitness(who) != True:
        dropNotify(ERR_NOAUTH, who, domainhash)
        return False

    domainreg = GetDomainRegister(domainhash)

    if who != domainreg:
        dropNotify(ERR_YOUNOTHAVE, who, domainhash)
        return False

    a = clearDomain(domainhash)
    dropNotify(ERR_OK, who, domainhash)
    return a


# 转移域名,参数1：调用者本身，参数2：接受者 参数3：转移域名的hash
def Transfer(send, recv, domainhash):
    if CheckWitness(send) != True:
        transferNotify(ERR_NOAUTH, send, recv, domainhash)
        return False

    domainreg = GetDomainRegister(domainhash)
    if send != domainreg:
        transferNotify(ERR_YOUNOTHAVE, send, recv, domainhash)
        return False

    if len(recv) != 20:
        transferNotify(ERR_RECVADDR, send, recv, domainhash)
        return False
    SetDomainRegister(domainhash, recv)
    clearProtocol(domainhash, PROTOCOL_ADDRESS)
    clearProtocol(domainhash, PROTOCOL_ONTID)
    clearProtocol(domainhash, PROTOCOL_NAME)
    clearProtocol(domainhash, PROTOCOL_INFO)
    clearProtocol(domainhash, PROTOCOL_EMAIL)
    clearProtocol(domainhash, PROTOCOL_PHONE)
    transferNotify(ERR_OK, send, recv, domainhash)

    return True


# 注册域名  参数1：调用者本身  参数2：域名name，参数3：父域名的hash如 123.ont 则这里就是ont字符串的hash ，参数4：邀请者hash
def Register(who, name, roothash, inviter):
    if CheckWitness(who) == False:
        registerNotify(ERR_NOAUTH, who, name, roothash, "", inviter)
        return False

    rootReg = GetDomainRegister(roothash)

    if rootReg != who and rootReg != admin:
        registerNotify(ERR_YOU_NOT_HAVE, who, name, roothash, "", inviter)
        return False

    domainlen = len(name)
    if domainlen < 3 or domainlen > 32:
        registerNotify(ERR_EXITDOMAIN, who, name, roothash, "", inviter)
        return False

    for index in range(0, domainlen):
        i = name[index:index + 1]
        if ((i >= 97 and i <= 122) or (i >= 48 and i <= 57)) == False:
            registerNotify(ERR_INVIA_ZM, who, name, roothash, "", inviter)
            return False

    domainhash = subnamehash(name, roothash)

    if checkHaveReg(domainhash) == True:
        registerNotify(ERR_EXITDOMAIN, who, name, roothash, domainhash, inviter)
        return False

    if domainlen == 3:
        stat = GetUserFreeDomainFlag(who, THREE_DONATE_DOMAIN)
        if stat == STATE_START:
            if registdomain(who, name, domainhash, roothash, inviter):
                SetUserFreeDomainFlagUse(who, THREE_DONATE_DOMAIN, STATE_HAVE)
                registerNotify(ERR_OK, who, name, roothash, domainhash, inviter)
                return True
        else:
            stat = GetUserFreeDomainFlag(who, THREE_INVERT_DOMAIN)
            if stat == STATE_START:
                if registdomain(who, name, domainhash, roothash, inviter):
                    SetUserFreeDomainFlagUse(who, THREE_INVERT_DOMAIN, STATE_HAVE)
                    registerNotify(ERR_OK, who, name, roothash, domainhash, inviter)
                    return True

    if domainlen == 4:
        stat = GetUserFreeDomainFlag(who, FOUR_DONATE_DOMAIN)
        if stat == STATE_START:
            if registdomain(who, name, domainhash, roothash, inviter):
                SetUserFreeDomainFlagUse(who, FOUR_DONATE_DOMAIN, STATE_HAVE)
                registerNotify(ERR_OK, who, name, roothash, domainhash, inviter)
                return True
        else:
            stat = GetUserFreeDomainFlag(who, FOUR_INVERT_DOMAIN)
            if stat == STATE_START:
                if registdomain(who, name, domainhash, roothash, inviter):
                    SetUserFreeDomainFlagUse(who, FOUR_INVERT_DOMAIN, STATE_HAVE)
                    registerNotify(ERR_OK, who, name, roothash, domainhash, inviter)
                    return True

    if domainlen > 4:
        stat = GetUserFreeDomainFlag(who, FREE_DOMAIN)
        if stat != STATE_HAVE:
            if registdomain(who, name, domainhash, roothash, inviter):
                SetUserFreeDomainFlagUse(who, FREE_DOMAIN, STATE_HAVE)
                registerNotify(ERR_OK, who, name, roothash, domainhash, inviter)
                return True
    registerNotify(ERR_YOUHAVE, who, name, roothash, domainhash, inviter)
    return False


def checkHaveReg(domainhash):
    register = GetDomainRegister(domainhash)
    if register != "":
        return True
    return False


def transferNotify(stateCode, who, recv, domainhash):
    tean = [OP_TRANFER, stateCode, who, recv, domainhash]
    Notify(tean)


def registerNotify(stateCode, regAddress, domainname, roothash, domainhash, inviter):
    info = [OP_REGISTER, stateCode, regAddress, domainname, roothash, domainhash, inviter]
    Notify(info)


def setResolveNotify(stateCode, who, domainhash, protocol, content):
    info = [OP_SETRESOLVE, stateCode, who, domainhash, protocol, content]
    Notify(info)


def donatNotify(stateCode, who, amount):
    info = [OP_DONAT, stateCode, who, amount]
    Notify(info)


def dropNotify(stateCode, who, domainhash):
    info = [OP_DROP, stateCode, who, domainhash]
    Notify(info)


def registdomain(who, domainame, domainhash, roothash, inviter):
    SetDomainName(domainhash, domainame)
    SetDomainRootHash(domainhash, roothash)
    SetDomainRegister(domainhash, who)
    if len(inviter) == 20 and inviter != who:
        invitercountkey = concat(inviter, INVITER)
        invitercount = GetStorage(invitercountkey)
        invitercount = invitercount + 1
        PutStorage(invitercountkey, invitercount)
        if invitercount >= THREE_FLAG:
            stat = GetUserFreeDomainFlag(who, THREE_INVERT_DOMAIN)
            if stat == 0:
                SetUserFreeDomainFlagUse(inviter, THREE_INVERT_DOMAIN, STATE_START)

        if invitercount >= FOUR_FLAG:
            stat = GetUserFreeDomainFlag(inviter, FOUR_INVERT_DOMAIN)
            if stat == 0:
                SetUserFreeDomainFlagUse(inviter, FOUR_INVERT_DOMAIN, STATE_START)

    return True


def clearDomain(domainhash):
    domainregkey = concat(domainhash, REGISTER_ADDRESS)
    domainrootkey = concat(domainhash, ROOT_HASH)
    domainnamekey = concat(domainhash, DOMAIN_NAME)
    DelStorage(domainregkey)
    DelStorage(domainrootkey)
    DelStorage(domainnamekey)
    clearProtocol(domainhash, PROTOCOL_ADDRESS)
    clearProtocol(domainhash, PROTOCOL_ONTID)
    clearProtocol(domainhash, PROTOCOL_NAME)
    clearProtocol(domainhash, PROTOCOL_INFO)
    clearProtocol(domainhash, PROTOCOL_EMAIL)
    clearProtocol(domainhash, PROTOCOL_PHONE)
    return True


def clearProtocol(domainhash, PROTOCAL):
    domainkey = concat(domainhash, DOMAIN_PROTOCOL)
    domprot = concat(domainkey, PROTOCAL)
    DelStorage(domprot)
    return True


def namehash(domain):
    return sha256(domain)


def subnamehash(domain, roothash):
    domain = concat(roothash, domain)
    #Notify(domain)
    return sha256(domain)


def SetDomainContent(domainhash, protocol, content):
    key = concat(domainhash, DOMAIN_PROTOCOL)
    key = concat(key, protocol)
    PutStorage(key, content)


def GetDomainContent(domainhash, protocol):
    key = concat(domainhash, DOMAIN_PROTOCOL)
    key = concat(key, protocol)
    return GetStorage(key)


def SetDomainRegister(domainhash, registeraddress):
    key = concat(domainhash, REGISTER_ADDRESS)
    return PutStorage(key, registeraddress)


def GetDomainRegister(domainhash):
    key = concat(domainhash, REGISTER_ADDRESS)
    return GetStorage(key)


def SetDomainRootHash(domainhash, roothash):
    key = concat(domainhash, ROOT_HASH)
    return PutStorage(key, roothash)


def GetDomainRootHash(domainhash):
    key = concat(domainhash, ROOT_HASH)
    return GetStorage(key)


def SetDomainName(domainhash, domainname):
    key = concat(domainhash, DOMAIN_NAME)
    return PutStorage(key, domainname)


def GetDomainName(domainhash):
    key = concat(domainhash, DOMAIN_NAME)
    return GetStorage(key)


def GetUserFreeDomainFlag(who, type):
    key = concat(who, type)
    return GetStorage(key)


def SetUserFreeDomainFlagUse(who, type, state):
    key = concat(who, type)
    return PutStorage(key, state)


def GetUserDonatNumber(who):
    key = concat(who, DONATE)
    return GetStorage(key)


def SetUserDonatNumber(who, value):
    key = concat(who, DONATE)
    return PutStorage(key, value)


def transferONT(fromaddr, toaddr, amount):
    param = state(fromaddr, toaddr, amount)
    res = Invoke(0, OntContract, "transfer", [param])
    return res


def GetStorage(key):
    return Get(ctx, key)


def PutStorage(key, value):
    Put(ctx, key, value)
    return True


def DelStorage(key):
    Delete(ctx, key)
    return True