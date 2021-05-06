from bs4 import BeautifulSoup
import requests
import csv
from pprint import pprint
from requests.compat import urljoin
import os

'''
通常ステータスのキーとバリューレベルごとに分けて辞書型で返却するメソッド
param: status_key: str , status_value: int 
return: dict = {
        攻撃力：LV30 : 422,
        攻撃力：LV50 : 732,
        攻撃力：LV70 : 1002,
}
'''
def status_rename_key_value_return_dict(status_key, status_value):
    if  " - " in status_value:
        status_revalues = status_value.split(" - ") 
        status_rekeys = [status_key + ":LV30", status_key + ":LV50", status_key + ":LV70"]
        status_tmp_dict = {k: v for k, v in zip(status_rekeys, status_revalues)}
        return status_tmp_dict

'''
クローリングしたステータスの情報をキー名とバリュー（ステータス値）に分けたメソッド
return status_dict_result: dict
'''
def status_dict_result(soup):     
    status_keys = [n.get_text() for n in soup.select('.item-detail tr th')]
    status_values = [n.next_sibling.next_sibling.get_text() for n in soup.select('.item-detail th')]

    status_dict = {k: v for k, v in zip(status_keys, status_values)}
    status_dict_result = {}
    for key, value in status_dict.items():
        if key == "HP" or key == "攻撃力" or key == "防御力" or key == "素早さ":
            dic = status_rename_key_value_return_dict(key, value)   
            status_dict_result.update(dic)
        else:
            status_dict_result.update({key : value})    
    return status_dict_result  


'''
マスエフェクトの枠と条件を一つに合わせるメソッド
param: mass_keys: array
return mass_blocks: array
'''
def mass_rename_key_return_array(mass_keys):
    mass_blocks = []        
    for i in range(5,len(mass_keys)): 
        for j in range(0,5):
            mass_blocks.append(mass_keys[j] + mass_keys[i]) 
    return mass_blocks        

'''
クローリングしたなすエフェクトの情報をキー名とバリュー（ステータス値）に分けたメソッド
return status_dict_result: dict
'''     
def mass_dict_result(soup):
    mass_keys = mass_rename_key_return_array([n.get_text() for n in soup.select('.mass-effect tr th') if len(n) != 0])
    mass_values = [n.get_text() for n in soup.select('.mass-effect tr td')]
    
    mass_dict_result = {k: v for k, v in zip(mass_keys, mass_values)}
    return mass_dict_result       

'''
クローリングしたメギド名とマスエフェクト情報（名、特徴）をキー名とバリュー（ステータス値）に分けたメソッド
return status_dict_result: dict
'''
def megidoname_effectname_return_dict(soup):
    megido_name = soup.select_one('h1.section-title').get_text()
    effect_name = soup.select_one('h2:nth-child(10).sub-title2').get_text()
    effect_features = soup.select_one('div.mt10.mb10').get_text()
    return { "メギド名" : megido_name , "マスエフェクト名" : effect_name , "マスエフェクトの特徴" : effect_features}

'''
メギドごとの画像をmegido_imgフォルダに保存するメソッド
'''    
def megido_getImages_request(soup, megido_name, url):
    item_image = soup.select_one('.item-image img')
    link_img = item_image.get("src")
    mkdir_path = 'megido_img/'
    # 相対URLから絶対URLに変換しリクエスト
    image = urljoin(url, link_img)
    save_path = mkdir_path + '{}.png'.format(megido_name)
    re = requests.get(image)
    #ディレクトリ作成して保存
    0 if os.path.exists(mkdir_path) else os.mkdir(mkdir_path)
    with open(save_path, 'wb') as f:
        f.write(re.content)
    print(save_path)

'''
クローリングしたメギドの情報をcsvに１行ずつ保存するメソッド
'''
def csv_write_megido_dict(megido_dict):
    target_dicts = megido_dict["megido"]
    mkdir_path = 'megido_data/'
    #ディレクトリ作成して保存
    0 if os.path.exists(mkdir_path) else os.mkdir(mkdir_path)
    with open(mkdir_path + 'megido_status.csv', 'w') as f:
        # dialectの登録
        csv.register_dialect('dialect01', doublequote=True, quoting=csv.QUOTE_ALL)
        # DictWriter作成
        writer = csv.DictWriter(f, fieldnames=target_dicts[0].keys(), dialect='dialect01')
        # CSVへの書き込み
        writer.writeheader()
        for target_dict in target_dicts:
            writer.writerow(target_dict)


def megido_crawler():
    megido_name = '/megido/バエル'
    info_list = []
    while megido_name != None:
        url = "https://megido72-portal.com" + megido_name
        res = requests.get(url)
        print(res)
        soup = BeautifulSoup(res.text, "html.parser")

        status = status_dict_result(soup)
        mass_effect = mass_dict_result(soup)
        info = megidoname_effectname_return_dict(soup)

        tmp = { "info" : info, "status" : status, "mass_effect" : mass_effect }
        info_list.append(tmp)
        pprint(tmp)

        megido_section_title = soup.select_one('h1.section-title').get_text()
        print(megido_section_title)
        megido_getImages_request(soup, megido_section_title, url)
        if megido_section_title == 'アンドロマリウス':
            megido_name = None
            print('finish')
        else:
            megido_name = soup.select_one(".next a").get('href')

    megido_dict = { "megido" : info_list }
    csv_write_megido_dict(megido_dict)

if __name__ == '__main__':
    pprint(megido_crawler())