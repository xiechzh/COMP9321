import requests
import xlrd
import json
import codecs
import time
from collections import OrderedDict
import dicttoxml
from xml.dom.minidom import parseString
###   根据输入可以写个函数


china_url = "http://api.worldbank.org/v2/en/country/CHN?downloadformat=excel"
American_url = "http://api.worldbank.org/v2/en/country/ASM?downloadformat=excel"
GDP_url = "http://api.worldbank.org/v2/en/indicator/NY.GDP.MKTP.KD.ZG?downloadformat=excel"

def request_file(countryName):
    country_url = "http://api.worldbank.org/v2/en/country/" + countryName + "?downloadformat=excel"
    r = requests.get(country_url)
    filename = countryName + ".xlsx"
    with open(filename,'wb') as f:
        f.write(r.content)
    data = xlrd.open_workbook(filename)
    return data


def get_country_code():
    r = requests.get("http://api.worldbank.org/v2/en/indicator/SI.POV.DDAY?downloadformat=excel")
    filename = "countryCode.xlsx"
    with open(filename,'wb') as f:
        f.write(r.content)
    data = xlrd.open_workbook(filename)
    sheet_0 = data.sheet_by_index(0)
    country_code_value = sheet_0.col_values(1)[5:]
    print('-----------------------\n',country_code_value)

    return country_code_value


#     change the file, which download from website, to json format
def excel_to_json(countryName):
    data = request_file(countryName)
    sheet_0 = data.sheet_by_index(0)
    rows = sheet_0.nrows
    cols = sheet_0.ncols
    columes_value = sheet_0.row_values(3)
    #country_code = sheet_0.cell_value(5,1)
    convert_dict = OrderedDict()
    #country_list = []
    #indicator_dict = OrderedDict()

    #        country name as key, all content of this country as value.
    #        indicator Name as key, all data with years as value
    #        include the information like space and black
    for row in range(4,rows):
        year_dict = OrderedDict()
        year_list = []
        #year_dict[columes_value[3]] = sheet_0.cell_value(row,3)
        for col in range(44,cols):
            if sheet_0.cell_value(row, col) != '' and sheet_0.cell_value(row, col) != ' ':
                year_dict[columes_value[col]] = sheet_0.cell_value(row,col)

        #year_list.append(year_dict)
        convert_dict[sheet_0.cell_value(row,2)] = year_dict
        #country_list.append(indicator_dict)

    json_data = json.dumps(convert_dict, indent=4, separators=(',', ':'))
    json_file = countryName + ".json"
    #with codecs.open(json_file, 'w') as ff:
    #    ff.write(json_data)

    return json_data

gdp_url = "http://api.worldbank.org/v2/en/indicator/NY.GDP.MKTP.KD.ZG?downloadformat=excel"
central_gov_debt_url = "http://api.worldbank.org/v2/en/indicator/GC.DOD.TOTL.GD.ZS?downloadformat=excel"


url_uni = "http://api.worldbank.org/v2/en/indicator/SE.XPD.TERT.PC.ZS?downloadformat=excel"
url_research = "http://api.worldbank.org/v2/en/indicator/GB.XPD.RSDV.GD.ZS?downloadformat=excel"
url_edu = "http://api.worldbank.org/v2/en/indicator/SE.XPD.TOTL.GD.ZS?downloadformat=excel"
url_gdp = "http://api.worldbank.org/v2/en/indicator/NY.GDP.MKTP.CD?downloadformat=excel"

def request_edu_file(url):
    r = requests.get(url)
    filename = url[48] + url[49] + url[50] + url[51] + ".xlsx"
    with open(filename,'wb') as f:
        f.write(r.content)
    data = xlrd.open_workbook(filename)
    return data



def excel_edu_json(url):
    data = request_edu_file(url)
    sheet_0 = data.sheet_by_index(0)
    rows = sheet_0.nrows
    cols = sheet_0.ncols
    columes_value = sheet_0.row_values(3)
    convert_dict = OrderedDict()

    #      country code as key, all content of this country as value.
    #      include the information like space and black
    for row in range(4,rows):
        year_dict = OrderedDict()
        for col in range(44,cols):
            if sheet_0.cell_value(row,col) != '' and sheet_0.cell_value(row,col) != ' ':
                year_dict[columes_value[col]] = sheet_0.cell_value(row,col)

        convert_dict[sheet_0.cell_value(row,1)] = year_dict

    json_data = json.dumps(convert_dict, indent=4, separators=(',', ':'))
    json_file = url[48] + url[49] + url[50] + url[51] + ".json"
    with codecs.open(json_file, 'w') as ff:
        ff.write(json_data)

    return json_data



#      transfar json document to mlab
#      把json 传到mlab上
from mongoengine import connect, StringField, IntField, Document, EmbeddedDocument, ListField, EmbeddedDocumentField, FileField
import codecs

connect(host='mongodb://winnie:908908@ds137720.mlab.com:37720/comp9321_ass3')

class Winnie(Document):
    #id = IntField(required=True, primary_key=True)
    idName = StringField(required=True)
    json_data = StringField(required=True)
    #filename = FileField(required=True)

    def __init__(self,idName,json_data, *args, **kwargs):                      #?为什么 authentication failed 了-----因为名字密码不对
        super().__init__(*args, **kwargs)
        self.idName = idName
        self.json_data = json_data

def save_information(idName,json_data):
    country_code = get_country_code()
    for code in country_code:
        json_data = excel_to_json(code)
        file = Winnie(code,json_data)
        file.save()

def save_one_information(idName,json_data):
    data_1 = excel_edu_json("http://api.worldbank.org/v2/en/indicator/NY.GDP.MKTP.CD?downloadformat=excel")
    f1 = Winnie("gdp",data_1)
    data2 = excel_to_json("http://api.worldbank.org/v2/en/indicator/SE.XPD.TOTL.GD.ZS?downloadformat=excel")
    f2 = Winnie("edu",data2)
    data3 = excel_to_json("http://api.worldbank.org/v2/en/indicator/GB.XPD.RSDV.GD.ZS?downloadformat=excel")
    f3 = Winnie("research",data3)
    data4 = excel_to_json("http://api.worldbank.org/v2/en/indicator/SE.XPD.TERT.PC.ZS?downloadformat=excel")
    f4 = Winnie("uni",data4)
    f1.save()
    f2.save()
    f3.save()
    f4.save()

    #file = Winnie(idName,json_data)
    #file.save()

def get_all_data():
    data_dict = OrderedDict()
    for line in Winnie.objects():
        data_dict[line.idName] = line.json_data
    return data_dict

def get_json_data(idName):
    json_data = Winnie.objects(idName=idName)[0].json_data
    print(json_data)
    return json_data

def delete(idName):
    Winnie.objects(idName=idName).delete()


url_uni = "http://api.worldbank.org/v2/en/indicator/SE.XPD.TERT.PC.ZS?downloadformat=excel"
url_research = "http://api.worldbank.org/v2/en/indicator/GB.XPD.RSDV.GD.ZS?downloadformat=excel"
url_edu = "http://api.worldbank.org/v2/en/indicator/SE.XPD.TOTL.GD.ZS?downloadformat=excel"
url_gdp = "http://api.worldbank.org/v2/en/indicator/NY.GDP.MKTP.CD?downloadformat=excel"


#    下面是需要调用的函数     blow is the function that teammate can use to get data

#     得到一个country的数据       get country data
def get_country_data(countryName):
    data = get_json_data(countryName)         ### get data from mlab
    dict = json.loads(data)
    return dict

#     得到rank的数据             get rank data
def get_rank_data(rankName):
    name_dict = OrderedDict()
    name_dict["gdp"] = "http://api.worldbank.org/v2/en/indicator/NY.GDP.MKTP.CD?downloadformat=excel"
    name_dict["edu"] = "http://api.worldbank.org/v2/en/indicator/SE.XPD.TOTL.GD.ZS?downloadformat=excel"
    name_dict["research"] = "http://api.worldbank.org/v2/en/indicator/GB.XPD.RSDV.GD.ZS?downloadformat=excel"
    name_dict["uni"] = "http://api.worldbank.org/v2/en/indicator/SE.XPD.TERT.PC.ZS?downloadformat=excel"
    data = get_json_data(rankName)
    dict = json.loads(data)
    return dict



