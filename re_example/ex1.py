import re
pt="([\u4e00-\u9fa5]+桥).+?" #中文匹配的符号 （）.+？表示非贪婪匹配
l=re.findall(pt,"abc嘻嘻哈哈桥 桥 1.23 亩") #匹配桥名
print(l)


pt="(桥梁面积\s*)(-?\d+\.?\d*e?-?\d*?)(\s*亩)" #中文匹配的符号
l=re.findall(pt,"abc嘻嘻哈哈桥 桥梁面积126.23亩") #匹配桥后面的面积
print(l)



import re

words = '57×32+(36+64+36)连续梁+3×32+(32+48+32)连续梁+33×32+2×24+14×32+1×24+1×29+16×32+3×24+(64+120+64)连续梁+2×32+1×24+6×32+1×24+1×25+13×32+2×24+21×32+1×28+(32+48+32)连续梁+1×24+(40+64+40)连续梁+8×32+2×24+1×28+20×32+1×24+1×29+26×32+1×27+(40+64+40)连续梁+3×32+2×24+28×32+1×32+1×29+8×32+1×24+10×32+1×24+6×32+2×24+1×27+63×32+1×24+24×32+3×24+20×32+2×24+5×32+24×32+1×24+15×32'
p1 = re.compile(r'[(](.*?)[)]', re.S) #最小匹配
p2 = re.compile(r'[(](.*)[)]', re.S)  #贪婪匹配
rt=re.findall(p1, words)
print(rt)
rt=re.findall(p2, words)
print(rt)