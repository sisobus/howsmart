#-*- coding:utf-8 -*-
__author__ = 'sisobus'
import commands
import os

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
        1:'거실가구', '거실가구':1 , 2:'sofa', 'sofa':2 , 3:'footstool', 'footstool':3 , 4:'카펫', '카펫':4 , 5:'레이블', '레이블':5 , 6:'mediastorage', 'mediastorage':6 , 7:'조명', '조명':7 , 8:'의자', '의자':8 , 9:'커튼', '커튼':9 ,
        10:'침실가구', '침실가구':10 , 11:'침대', '침대':11 , 12:'서랍', '서랍':12 , 13:'의자', '의자':13 , 14:'거울', '거울':14 , 15:'침구', '침구':15 , 16:'bedsidetable', 'bedsidetable':16 , 17:'조명', '조명':17 , 18:'커튼', '커튼':18 , 19:'케비넷', '케비넷':19 , 20:'장농', '장농':20 , 21:'화장대', '화장대':21 ,
        22:'서재', '서재':22 , 23:'책상', '책상':23 , 24:'소파', '소파':24 , 25:'카펫', '카펫':25 , 26:'의자', '의자':26 , 27:'테이블', '테이블':27 , 28:'mediastorage', 'mediastorage':28 , 29:'서랍장', '서랍장':29 , 30:'조명', '조명':30 , 31:'커튼', '커튼':31 ,
        32:'주방가구', '주방가구':32 , 33:'테이블', '테이블':33 , 34:'hardware', 'hardware':34 , 35:'의자', '의자':35 , 36:'조명', '조명':36 ,
        37:'화장실', '화장실':37 , 38:'싱크', '싱크':38 , 39:'showers', 'showers':39 , 40:'변기', '변기':40 , 41:'캐비넷', '캐비넷':41 ,
        42:'제작가구(Builtin)', '제작가구(Builtin)':42 , 43:'장농', '장농':43 , 44:'화장실싱크대', '화장실싱크대':44 , 45:'싱크대', '싱크대':45 , 46:'커튼', '커튼':46 ,
        47:'조명', '조명':47 , 48:'천정조명', '천정조##':48 , 49:'램프', '램프':49 , 50:'벽부형', '벽부형':50 , 51:'화장실조명', '화장실조명':51 , 52:'팬던트', '팬던트':52 , 53:'유아용', '유아용':53 ,
        54:'인테리어소품', '인테리어소품':54 , 55:'미술품(조각)', '미술품(조각)':55 , 56:'카펫', '카펫':56 , 57:'데코제품', '데코제품':57 , 58:'거울', '거울':58 , 59:'쿠션', '쿠션':59 , 60:'액자(그림)', '액자(그림)':60 , 61:'커튼', '커튼':61 ,
        62:'유아/주니어가구', '유아/주니어가##':62 , 63:'침대', '침대':63 , 64:'데코', '데코':64 , 65:'침구', '침구':65 , 66:'카펫', '카펫':66 , 67:'책상', '책상':67 , 68:'조명', '조명':68 , 69:'의자', '의자':69 ,
        70:'오피스', '오피스':70 , 71:'책상', '책상':71 , 72:'회의실의자', '회의실의자':72 , 73:'조명', '조명':73 , 74:'의자', '의자':74 , 75:'탕비실장', '탕비실장':75 , 76:'커튼', '커튼':76 , 77:'회의테이블', '회의테이블':77 , 78:'storage', 'storage':78 ,
        79:'상업', '상업':79 , 80:'테이블', '테이블':80 , 81:'싱크대', '싱크대':81 , 82:'의자', '의자':82
    }
    return d

def get_shop_category_list():
    shop_category_dict = get_shop_category_dictionary()
    l = []
    for i in xrange(1,83,1):
        cur = (str(i), shop_category_dict[i])
        l.append(cur)
    return l

def get_shop_category_1st_list():
    ret = [1,10,22,32,37,42,47,54,62,70,79]
    return ret

def get_shop_category_2nd_list():
    ret = []
    shop_category_1st_list = get_shop_category_1st_list()
    for i in xrange(1,83,1):
        if i in shop_category_1st_list:
            continue
        ret.append(i)
    return ret

def get_shop_category_tree():
    shop_category_1st_list = get_shop_category_1st_list()
    ret = [ [] for i in xrange(len(shop_category_1st_list))]
    ret[0] = [ i for i in xrange(2,10) ]
    ret[1] = [ i for i in xrange(11,22)]
    ret[2] = [ i for i in xrange(23,32)]
    ret[3] = [ i for i in xrange(33,37)]
    ret[4] = [ i for i in xrange(38,42)]
    ret[5] = [ i for i in xrange(43,47)]
    ret[6] = [ i for i in xrange(48,54)]
    ret[7] = [ i for i in xrange(55,62)]
    ret[8] = [ i for i in xrange(63,70)]
    ret[9] = [ i for i in xrange(71,79)]
    ret[10] = [ i for i in xrange(80,83)]

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