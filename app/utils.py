#-*- coding:utf-8 -*-
__author__ = 'sisobus'
import commands
import os
import json

ALLOWED_EXTENSIONS = set(['txt','pdf','png','jpg','JPG','jpeg','JPEG','gif','GIF','zip'])

def allowedFile(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

def createDirectory(directoryName):
    if not os.path.exists(directoryName):
        command = 'mkdir %s'%directoryName
        ret = commands.getoutput(command)
        command = 'chmod 777 %s'%directoryName
        ret = commands.getoutput(command)

def get_image_path(real_image_path):
    ret = ''
    for t in real_image_path.lstrip().rstrip().split('/')[6:]: ret=ret+t+'/'
    return ret[:-1]

def get_shop_category_dictionary():
    d = {
1:'거실가구',
'거실가구':1,
2:'소파',
'소파':2,
3:'소파테이블',
'소파테이블':3,
4:'사이드테이블',
'사이드테이블':4,
5:'TV스탠드',
'TV스탠드':5,
6:'거실수납장',
'거실수납장':6,
7:'거실조명',
'거실조명':7,
8:'거실카페트',
'거실카페트':8,
9:'주방가구',
'주방가구':9,
10:'식탁',
'식탁':10,
11:'의자',
'의자':11,
12:'수납장',
'수납장':12,
13:'소가구',
'소가구':13,
14:'기타',
'기타':14,
15:'침실가구',
'침실가구':15,
16:'침대',
'침대':16,
17:'매트리스',
'매트리스':17,
18:'옷장',
'옷장':18,
19:'수납장',
'수납장':19,
20:'화장대',
'화장대':20,
21:'침실조명',
'침실조명':21,
22:'침구류',
'침구류':22,
23:'소가구',
'소가구':23,
24:'카페트',
'카페트':24,
25:'기타',
'기타':25,
26:'서재가구',
'서재가구':26,
27:'책상/테이블',
'책상/테이블':27,
28:'사무용 의자',
'사무용 의자':28,
29:'책장',
'책장':29,
30:'수납장',
'수납장':30,
31:'소가구',
'소가구':31,
32:'기타',
'기타':32,
33:'유아-주니어가구',
'유아-주니어가구':33,
34:'침대',
'침대':34,
35:'매트리스',
'매트리스':35,
36:'옷장/서랍장',
'옷장/서랍장':36,
37:'수납장',
'수납장':37,
38:'책상',
'책상':38,
39:'책장',
'책장':39,
40:'소가구',
'소가구':40,
41:'기타',
'기타':41,
42:'욕실',
'욕실':42,
43:'세면대',
'세면대':43,
44:'욕실수납',
'욕실수납':44,
45:'수도꼭지',
'수도꼭지':45,
46:'도기',
'도기':46,
47:'욕실용품',
'욕실용품':47,
48:'욕실조명',
'욕실조명':48,
49:'기타',
'기타':49,
50:'제작가구',
'제작가구':50,
51:'주방가구',
'주방가구':51,
52:'붙박이장',
'붙박이장':52,
53:'현관장',
'현관장':53,
54:'화장실가구',
'화장실가구':54,
55:'기타',
'기타':55,
56:'인테리어 소품',
'인테리어 소품':56,
57:'페브릭',
'페브릭':57,
58:'테이블웨어',
'테이블웨어':58,
59:'홈데코',
'홈데코':59,
60:'생활용품',
'생활용품':60,
61:'조명',
'조명':61,
62:'기타',
'기타':62,
63:'상업가구',
'상업가구':63,
64:'테이블',
'테이블':64,
65:'소파',
'소파':65,
66:'의자',
'의자':66,
67:'수납장',
'수납장':67,
68:'기타',
'기타':68,
69:'사무가구',
'사무가구':69,
70:'사무용 책상',
'사무용 책상':70,
71:'사무용 의자',
'사무용 의자':71,
72:'회의용 테이블',
'회의용 테이블':72,
73:'회의용 의자',
'회의용 의자':73,
74:'기타',
'기타':74,
    }
    return d

def get_shop_category_list():
    shop_category_dict = get_shop_category_dictionary()
    l = []
    for i in xrange(1,75,1):
        cur = (str(i), shop_category_dict[i])
        l.append(cur)
    return l

def get_shop_category_1st_list():
    ret = [1,9,15,26,33,42,50,56,63,69]
    return ret

def get_shop_category_2nd_list():
    ret = []
    shop_category_1st_list = get_shop_category_1st_list()
    for i in xrange(1,75,1):
        if i in shop_category_1st_list:
            continue
        ret.append(i)
    return ret

def get_shop_category_tree():
    shop_category_1st_list = get_shop_category_1st_list()
    ret = [ [] for i in xrange(len(shop_category_1st_list))]
    ret[0] = [ i for i in xrange(2,9) ]
    ret[1] = [ i for i in xrange(10,15)]
    ret[2] = [ i for i in xrange(16,26)]
    ret[3] = [ i for i in xrange(27,33)]
    ret[4] = [ i for i in xrange(34,42)]
    ret[5] = [ i for i in xrange(43,50)]
    ret[6] = [ i for i in xrange(51,56)]
    ret[7] = [ i for i in xrange(57,63)]
    ret[8] = [ i for i in xrange(64,69)]
    ret[9] = [ i for i in xrange(70,75)]

    return ret

def get_all_category():
    shop_category_dictionary = get_shop_category_dictionary()
    shop_category_tree = get_shop_category_tree()
    ret_category = []
    for i in xrange(len(shop_category_tree)):
        first_category_id = shop_category_tree[i][0]-1
        first_category_name = shop_category_dictionary[first_category_id]
        second_categories = []
        for j in xrange(len(shop_category_tree[i])):
            second_category_id = shop_category_tree[i][j]
            second_category_name = shop_category_dictionary[second_category_id]
            d = {
                'category_id': str(second_category_id),
                'category_name': str(second_category_name)
            }
            second_categories.append(d)
        d = {
            'category_id': first_category_id,
            'category_name': first_category_name,
            'child_categories': second_categories
        }
        ret_category.append(d)
    return ret_category

def convert_price_to_won(price):
    if str(price).find(',') != -1:
        return price
    reverse_str_price = str(price)[::-1]
    ret = ''
    for i in xrange(len(reverse_str_price)):
        ret = str(reverse_str_price[i])+ret
        next_i = i+1
        if next_i < len(reverse_str_price) and next_i % 3 == 0:
            ret =  ','+ret
    return ret

#
# return {  'si': [(),(),...],
#           'gu': [(),(),...],
#           'dong': [(),(),...] }
#
def get_address_list():
    with open('/home/howsmart/howsmart/app/address.json','r') as fp:
        r = json.loads(fp.read())
    ret = {
            'si': [('전체','전체')],
            'gu': [('전체','전체')],
            'dong': [('전체','전체')]
            }
    for si in r:
        ret['si'].append((si['name'],si['name']))
        for gu in si['items']:
            ret['gu'].append((gu['name'],gu['name']))
            for dong in gu['items']:
                ret['dong'].append((dong['name'],dong['name']))
    return ret

