import re
import Levenshtein # pip install python-Levenshtein
from collections import OrderedDict

def getPairsFromText(txt):
    """将文本拆分成若干组[实体-金额]配对"""
    pattern = re.compile(r'\d+\.\d{2}\ ')   # 查找形如 ***.** 的数字
    items = re.split(pattern, txt)
    items = [t.split("\n")[-1] for t in items][:-1] # 去掉最后\n之前的文本
    amounts = pattern.findall(txt)
    amounts = [float(a) for a in amounts]
    items = devideitem(items) # 版面分析的临时替代方案。计算空item数量，将之前的长item暴力拆分
    counts = [1] * len(amounts)
    pairs = list(zip(items[:-1], amounts, counts))
    return pairs

def devideitem(items):
    """TODO 版面分析的临时替代方案。计算空item数量，将之前的长item拆分分配"""
    def removeSymbol(e):
        return e.replace(" ", "")
    def splitItemsNaive(e, c):
        """没有任何额外信息，按字符长度平均拆分"""
        len1 = len(e) // c
        es = []
        for i in range(c):
            es.append(e[i*len1:i*len1+len1])
        return es
    def splitItems(e,c):
        """ 将e拆分为[表头，物品×c，表尾]"""
        # 试图在e中找c个物品共有字段，作为物品的间隔符
        dict1 = OrderedDict() # 词频统计
        ws = e.split(" ")
        for w in ws:
            dict1[w] = dict1.get(w, 0) + 1
        for w, c1 in dict1.items():
            if c1==c: #首个重复了c次的词
                print("table div word: {}".format(w))
                es = e.split(w)
                if len(es)==c+1:
                    es = es[1:]
                break
        else:
            es = splitItemsNaive(e,c)
        return es
        
    r1 = []
    c = 0
    for i, e in enumerate(reversed(items)): #倒序循环
        if len(removeSymbol(e))==0: # 金额前面是空字符串，说明遇到了表格
            c += 1 # 表格物品计数
            continue
        elif c!=0: # 表格情况的表头，起始的item需要被拆分成c份，与c个金额对应
            es = splitItems(e, c)
            r1 += list(reversed(es))
            c = 0
        else:# 非表格情况，添加正常物品
            r1.append(e)
    r1 = list(reversed(r1))
    return r1
    

def removeBadCase(pairs0):
    pairs = []
    for pair in pairs0:
        e,a,c = pair
        if checkInvalidAmount(a): # 金额异常
            continue
        if c==1 and checkInvaliditem(e): # 无效实体
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
        ratio = Levenshtein.ratio(i0,i1) # 文本编辑距离/句长
        return ratio>0.6
        
    itemDict = dict()
    for i1, a1,c1 in pairs1:
        for i0, (a0,c0) in itemDict.items():
            if isSameitem(i0, i1):
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
    pairs = merge(pairs) # 合并同类item
    pairs = removeBadCase(pairs) # TODO 消除无效项
    for e, a, c in pairs:
        print(" item: {},\n total amount: {:.2f},\n count: {},\n".format(e,a,c))

