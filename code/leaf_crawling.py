from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import requests
import pandas as pd
import time
import os

############################# 드라이버 설정 #############################

# chrome options
options = Options()
options.add_argument("--headless") # 백그라운드로 실행

# webdriver 설정
service = Service(executable_path=ChromeDriverManager().install()) 
driver = webdriver.Chrome(service=service, options=options)

############################ csv 파일 초기화 ############################

# 잎을 관상하는 실내식물
leaf_info_columns = ["이름", "학명", "영명", "유통명", "과명", "원산지", "TIP"]
leaf_detail_columns = ["이름", "분류", "생육형태", "생장높이", "생장너비", "실내정원구성", 
                       "생태형", "잎형태", "잎무늬", "잎색", "꽃피는 계절", "꽃색", 
                       "열매 맺는 계절", "열매색", "향기", "번식방법", "번식시기"]
leaf_manage_columns = ["이름", "관리수준", "관리요구도", "광요구도", "배치장소",
                       "생장속도", "생육적온", "겨울최저온도", "습도", "비료", "토양", 
                       "물주기-봄", "물주기-여름", "물주기-가을", "물주기-겨울", "병충해"]

leaf_info_df = pd.DataFrame(columns=leaf_info_columns)
leaf_detail_df = pd.DataFrame(columns=leaf_detail_columns)
leaf_manage_df = pd.DataFrame(columns=leaf_manage_columns)

# 건조에 강한 실내식물
dry_info_columns = ["이름", "학명", "유통명", "형태분류", "원산지", "꽃", "엽색변화", "뿌리형태", 
                    "생장형", "생장속도", "특성", "월동온도", "생육온도"]
dry_manage_columns = ["이름", "광", "물주기", "번식", "관리수준", "관리요구도", "배치장소", "병충해", "TIP"]

dry_info_df = pd.DataFrame(columns=dry_info_columns)
dry_manage_df = pd.DataFrame(columns=dry_manage_columns)

# 분류
list_columns = ["name", "class"]
list_df = pd.DataFrame(columns=list_columns)

############################# 크롤링 공통 #############################

def get_text_or_empty(xpath):
    """
    요소에서 텍스트를 추출하거나 요소가 없을 경우 빈 문자열 반환
    """
    try:
        return driver.find_element(By.XPATH, xpath).text.strip()
    except:
        return ""

def get_info_dict(label_xpath, value_xpath):
    """
    크롤링 데이터를 딕셔너리 형태로 반환 (끝날 때까지 자동 탐색)
    """
    info_dict = {}
    i = 1  # 인덱스 초기화

    while True:
        try:
            column_name = get_text_or_empty(label_xpath.format(i=i))
            column_value = get_text_or_empty(value_xpath.format(i=i))

            if not column_name and not column_value:
                break

            info_dict[column_name] = column_value
            i += 1
        except:
            break
    return info_dict

def download_img(name, xpath):
    """
    지정된 xpath의 이미지를 name.jpg로 저장
    """
    try:
        img_url = driver.find_element(By.XPATH, xpath).get_attribute('src')
        os.makedirs('./img', exist_ok=True)

        if img_url:
            response = requests.get(img_url)
            if response.status_code == 200:
                file_path = f'./img/{name}.jpg'
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f"이미지 저장 완료: {file_path}")
    
    except:
        print(f"이미지 저장 실패: {name}.jpg")
        pass

############################# leaf 크롤링 #############################

def get_leaf_info():
    """
    식물별 상세 정보 크롤링
    """
    name = get_text_or_empty('//*[@id="contentForm"]/div[2]/div/div/dl/dt/strong')
    download_img(name, '//*[@id="contentForm"]/div[2]/div/div/dl/dd/div[1]/div/dl/dd/img')

    # 기본 정보 - leaf_info.csv
    info_values = get_info_dict(
        label_xpath = '//*[@id="contentForm"]/div[2]/div/div/dl/dd/div[2]/ul/li[{i}]/label',
        value_xpath = '//*[@id="contentForm"]/div[2]/div/div/dl/dd/div[2]/ul/li[{i}]/span'
    )
    info_values['이름'] = name
    leaf_info_df.loc[len(leaf_info_df)] = info_values

    # 상세 정보 - leaf_detail.csv
    detail_values = get_info_dict(
        label_xpath = '//*[@id="contentForm"]/div[4]/table/tbody/tr[{i}]/th',
        value_xpath = '//*[@id="contentForm"]/div[4]/table/tbody/tr[{i}]/td'
    )
    detail_values['이름'] = name
    leaf_detail_df.loc[len(leaf_detail_df)] = detail_values

    # 관리 정보 - leaf_manage.csv
    manage_values = get_info_dict(
        label_xpath = '//*[@id="contentForm"]/div[5]/table/tbody/tr[{i}]/th',
        value_xpath = '//*[@id="contentForm"]/div[5]/table/tbody/tr[{i}]/td'
    )
    manage_values['이름'] = name
    leaf_manage_df.loc[len(leaf_manage_df)] = manage_values

    # 리스트 정보 - list.csv
    list_df.loc[len(list_df)] = {"name": name, "class": "leaf"}

def get_leaf_page(base_url, start, end):
    """
    각 페이지를 방문하여 잎을 관상하는 실내식물 정보 크롤링
    """
    print("잎을 관상하는 실내식물 크롤링 시작:")
    for p in range(start, end+1):
        try:
            # 페이지 이동
            if p == 1:
                driver.get(base_url)
            elif p == 11:
                driver.get(base_url)
                next_xpath = '//*[@id="gardenPlant"]/div[3]/a[1]'
                driver.find_element(By.XPATH, next_xpath).click()
            elif p == 21:
                driver.get(base_url)
                next_xpath = '//*[@id="gardenPlant"]/div[3]/a[1]'
                driver.find_element(By.XPATH, next_xpath).click()
                next_xpath = '//*[@id="gardenPlant"]/div[3]/a[3]'
                driver.find_element(By.XPATH, next_xpath).click()
            elif p%10 == 0:
                next_xpath = '//*[@id="gardenPlant"]/div[3]/span[10]/a'
                driver.find_element(By.XPATH, next_xpath).click()
            else:
                next_xpath = f'//*[@id="gardenPlant"]/div[3]/span[{p%10}]/a'
                driver.find_element(By.XPATH, next_xpath).click()
            time.sleep(2)
            
            # 식물 정보 크롤링
            for plant in range(1, 9):
                try:
                    # 식물 페이지로 이동
                    if p == 10 and plant > 6:
                        plant_xpath = f'//*[@id="gardenPlant"]/div[2]/ul/i/i/li[{plant-5}]/a'
                    else:
                        plant_xpath = f'//*[@id="gardenPlant"]/div[2]/ul/li[{plant}]/a'
                    driver.find_element(By.XPATH, plant_xpath).click()
                    time.sleep(2)

                    # 식물 정보 크롤링
                    get_leaf_info()

                    # 이전 페이지로 이동
                    driver.back()
                    time.sleep(2)
                
                except Exception as e:
                    print(f"Error processing plant {plant}: {e}")
                    continue

        except Exception as e:
            print(f"Error processing page {p}: {e}")
            continue

############################## dry 크롤링 ##############################

def get_dry_info():
    """
    식물별 상세 정보 크롤링
    """
    name = get_text_or_empty('//*[@id="contentForm"]/div[2]/div/div/dl/dt/strong')
    download_img(name, '//*[@id="contentForm"]/div[2]/div/div/dl/dd/div[1]/div/img')

    # 기본 정보 - dry_info.csv
    info_values = get_info_dict(
        label_xpath = '//*[@id="sedumInfo"]/div/div[1]/ul/li[{i}]/strong',
        value_xpath = '//*[@id="sedumInfo"]/div/div[1]/ul/li[{i}]/span'
    )
    info_values['이름'] = name
    dry_info_df.loc[len(dry_info_df)] = info_values

    # 관리 정보 - manage.csv
    manage_values = get_info_dict(
        label_xpath = '//*[@id="sedumInfo"]/div/div[2]/ul/li[{i}]/strong',
        value_xpath = '//*[@id="sedumInfo"]/div/div[2]/ul/li[{i}]/span'
    )
    manage_values['이름'] = name
    dry_manage_df.loc[len(dry_manage_df)] = manage_values

    # 리스트 정보 - list.csv
    list_df.loc[len(list_df)] = {"name": name, "class": "dry"}

def get_dry_page(base_url, start, end):
    """
    각 페이지를 방문하여 ㅓㄱㄴ조에 강한 실내식물 정보 크롤링
    """
    print("건조에 강한 실내식물 크롤링 시작:")
    for p in range(start, end+1):
        try:
            # 페이지 이동
            if p == 1:
                driver.get(base_url)
            elif p == 11:
                driver.get(base_url)
                next_xpath = '//*[@id="gardenPlant"]/div[3]/a[1]'
                driver.find_element(By.XPATH, next_xpath).click()
            elif p%10 == 0:
                next_xpath = '//*[@id="gardenPlant"]/div[3]/span[10]/a'
                driver.find_element(By.XPATH, next_xpath).click()
            else:
                next_xpath = f'//*[@id="gardenPlant"]/div[3]/span[{p%10}]/a'
                driver.find_element(By.XPATH, next_xpath).click()
            time.sleep(2)
            
            # 식물 정보 크롤링
            for plant in range(1, 9):
                try:
                    # 식물 페이지로 이동
                    plant_xpath = f'//*[@id="gardenPlant"]/div[2]/ul/li[{plant}]/a'
                    driver.find_element(By.XPATH, plant_xpath).click()
                    time.sleep(2)

                    # 식물 정보 크롤링
                    get_dry_info()

                    # 이전 페이지로 이동
                    driver.back()
                    time.sleep(2)
                
                except Exception as e:
                    print(f"Error processing plant {plant}: {e}")
                    continue

        except Exception as e:
            print(f"Error processing page {p}: {e}")
            continue

############################# csv 파일 저장 #############################

def save_csv():
    """
    크롤링한 정보를 csv 파일로 저장
    """
    # 잎을 관상하는 실내식물
    leaf_info_df.to_csv("leaf_info.csv", index=False, encoding='utf-8-sig')
    leaf_detail_df.to_csv("leaf_detail.csv", index=False, encoding='utf-8-sig')
    leaf_manage_df.to_csv("leaf_manage.csv", index=False, encoding='utf-8-sig')

    # 건조에 강한 실내식물
    dry_info_df.to_csv("dry_info.csv", index=False, encoding='utf-8-sig')
    dry_manage_df.to_csv("dry_manage.csv", index=False, encoding='utf-8-sig')

    # 분류
    list_df.to_csv("list.csv", index=False, encoding='utf-8-sig')

############################### 실행 ###############################

# 잎을 관상하는 실내 식물
leaf_url = 'https://www.nongsaro.go.kr/portal/ps/psz/psza/contentMain.ps?menuId=PS00376&pageUnit=8'

# 건조에 강한 실내식물
dry_url = 'https://www.nongsaro.go.kr/portal/ps/psz/psza/contentMain.ps?menuId=PS04099&pageUnit=8'

get_leaf_page(leaf_url, 1, 28)
get_dry_page(dry_url, 1, 13)

save_csv()
driver.quit()
print('크롤링 완료!')