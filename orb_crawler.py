from bs4 import BeautifulSoup
import requests
import time
from requests.compat import urljoin
import csv
import os
from pprint import pprint

'''
クローリングしたステータスの情報をキー名とバリュー（ステータス値）に分けたメソッド
return status_dict_result: dict
'''
def orb_dict_result(soup):
    status_keys = [n.get_text() for n in soup.select('.item-detail tr th')]
    status_values = [n.next_sibling.next_sibling.get_text() for n in soup.select('.item-detail th')]
    status_dict = {k: v for k, v in zip(status_keys, status_values)}
    return status_dict

'''
オーブごとの画像をmegido_imgフォルダに保存するメソッド
'''    
def orb_getImages_request(soup, orb_name, url):
    item_image = soup.select_one('.orb-image img')
    link_img = item_image.get("src")
    mkdir_path = 'orb_img/'
    # 相対URLから絶対URLに変換しリクエスト
    image = urljoin(url, link_img)
    save_path = mkdir_path + '{}.png'.format(orb_name)
    re = requests.get(image)
    #ディレクトリ作成して保存
    0 if os.path.exists(mkdir_path) else os.mkdir(mkdir_path)
    with open(save_path, 'wb') as f:
        f.write(re.content)
    print(save_path)


'''
クローリングしたオーブの情報をcsvに１行ずつ保存するメソッド
'''
def csv_write_orb_dict(orb_dict):
    target_dicts = orb_dict["orb"]
    mkdir_path = 'orb_data/'
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

def orb_crawler():
    orb_name = '/orb/コボルト（ラッシュ）'
    info_list = []
    while orb_name != None:
        url = "https://megido72-portal.com" + orb_name
        res = requests.get(url)
        print(res)
        soup = BeautifulSoup(res.text, "html.parser")

        status = orb_dict_result(soup)
        orb_getImages_request(soup, "ココボルト", url)

        tmp = { "status" : status }
        info_list.append(tmp)
        pprint(tmp)

        orb_section_title = soup.select_one('h1.section-title').get_text()
        print(orb_section_title)
        orb_getImages_request(soup, orb_section_title, url)
        if orb_section_title == '火殻竜':
            orb_name = None
            print('finish')
        else:
            orb_name = soup.select_one(".next a").get('href')
        time.sleep(1)
        
    megido_dict = { "orb" : info_list }
    csv_write_orb_dict(megido_dict)

if __name__ == '__main__':
    pprint(orb_crawler())


