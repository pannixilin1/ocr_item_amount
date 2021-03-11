import re
import Levenshtein # pip install python-Levenshtein

def getPairsFromText(txt):
    """将文本拆分成若干组[实体-金额]配对"""
    pattern = re.compile(r'\d+\.\d{2}')   # 查找形如 ***.**的数字
    items = re.split(pattern, txt)
    items = [t.split("\n")[-1] for t in items] # 去掉最后\n之前的文本
    amounts = pattern.findall(txt)
    amounts = [float(a) for a in amounts]
    items = devideitem(items) # 版面分析的临时替代方案。计算空item数量，将之前的长item拆分分配
    counts = [1] * len(amounts)
    pairs = list(zip(items[:-1], amounts, counts))
    return pairs

def devideitem(items):
    """TODO 版面分析的临时替代方案。计算空item数量，将之前的长item拆分分配"""
    def removeSymbol(e):
        return e.replace(" ", "")
    def splititemByNum(e, c):
        """没有任何额外信息，只能暴力拆分"""
        len1 = len(e) // c
        es = []
        for i in range(c):
            es.append(e[i*len1:i*len1+len1])
        return es
    r1 = []
    c = 0
    for i, e in enumerate(reversed(items)):
        if len(removeSymbol(e))==0: # 空字符串
            c += 1
            continue
        else:
            if c==0:
                r1.append(e)
            else:
                es = splititemByNum(e, c)
                r1 += es
                c = 0
    r1 = list(reversed(r1))
    return r1
    

def removeBadCase(pairs0):
    pairs = []
    for pair in pairs0:
        e,a,c = pair
        if checkInvalidAmount(a): # 金额异常
            continue
        if checkInvaliditem(e): # 无效实体
            continue
        pairs.append(pair)
    return pairs

def checkInvalidAmount(amount):
    return amount==0

def checkInvaliditem(item):
    """TODO 判断实体是否为干扰项，方案1：干扰项词表倒排检索+编辑距离，方案2：NER+分类器"""
    return False
    
def merge(pairs1):
    def isSameitem(i0, i1):
        #return i0==i1
        ratio = Levenshtein.ratio(i0,i1) # 计算莱文斯坦比 (文本编辑距离/句长)
        return ratio>0.6
        
    itemDict = dict()
    for i1, a1,c1 in pairs1:
        for i0, (a0,c0) in itemDict.items():
            if isSameitem(i0, i1): # 如果物品相同
                itemDict[i0] = (a0+a1, c0+c1) # 金额汇总，数量汇总
                break
        else:#没有找到相同物品
            itemDict[i1] = (a1, 1) # 新建物品(金额，条目数量)
    r1 = [(e,a,c) for e, (a,c) in itemDict.items()]
    return r1
    
if __name__ == "__main__":
    with open("./sample text and report.txt") as f:
        txt = f.read()
    pairs = getPairsFromText(txt) # 临时版，检测金额，将文本拆分
    #pairs = getPairsFromRectangles(txtList, rectList) # TODO 进阶版，对文本框和位置信息进行版面分析得到配对
    pairs = removeBadCase(pairs) # 消除无效项
    pairs = merge(pairs) # 合并同类item
    for e, a, c in pairs:
        print(" item: {},\n total amount: {:.2f},\n count: {},\n".format(e,a,c))

