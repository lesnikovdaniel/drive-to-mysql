 # Подключаем необходимые библиотеки
from __future__ import print_function
from googleapiclient import discovery           # API Goole Drive
from httplib2 import Http                       # библиотека для работы с http-запросами
from oauth2client import file, client, tools    # библиотека для работы с типом авторизации oauth2
import pymysql                                  # библиотека для работы с СУБД MySQL
from pymysql.cursors import DictCursor          # курсор БД из пакета pymysql
import re                                       # встроенная библиотека регулярных выражений


def list_files():
    SCOPES = 'https://www.googleapis.com/auth/drive.readonly.metadata'  # определение области видимостей прав пользователя для работы с Google Drive
    store = file.Storage('token.json')  # ключ к Google API
    creds = store.get()     # определение хранилища данных для входа
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    DRIVE = discovery.build('drive', 'v3', http=creds.authorize(Http())) # объект, для подключения к Google API

    files = DRIVE.files().list(fields='files(id,name,createdTime,modifiedTime,size,webViewLink)').execute().get('files', []) # получаем список файлов на диске, с метаданными типа id,name,createdTime,modifiedTime,size,webViewLink

    return files

files = list_files() # массив из объектов, где каждый объект это файл

for item in files:
    rematch = re.search(r'(^.*)_([А-Я].*).csv', item['name'])   # регулярное выражение для обработки имени файла откуда берется регион и название data_set
    update_date = re.match(r'(\d{4}-\d{2}-\d{2})T(\d{2}(:)\d{2}:\d{2}?)',item['modifiedTime']) # регулярное выражение обработки времени изменения файла в Google Drive
    fileId = item['id']
    if rematch : region = str(rematch.group(1)) # достаём регион
    if rematch : data_set_name = str(rematch.group(2)) # достаём имя data_set
    if update_date : datetime = str(update_date.group(1))+" "+str(update_date.group(2)) # достаём время изменения файла на диске

    try:
        # объявляем соединения с БД
        connection = pymysql.connect(
                host="172.17.0.2", # поменять
                database="test",# поменять
                user="root",# поменять
                password="my-secret-pw",# поменять
                cursorclass=DictCursor, # НЕ МЕНЯТЬ
                autocommit=True # НЕ МЕНЯТЬ
            )
        
        checkRegion = """ 
            INSERT INTO data_set_owner (region) 
            SELECT '{}' FROM DUAL
            WHERE NOT EXISTS 
            (SELECT * FROM data_set_owner WHERE region='{}');
            """.format(region,region)

        cursorObject = connection.cursor()
        cursorObject.execute(checkRegion)
        connection.commit()

        checkQuery="SELECT EXISTS (SELECT 1 FROM data_set_passport WHERE owner_kpp=(SELECT owner_kpp FROM data_set_owner WHERE region='{}') AND data_set_name='{}');".format(region,data_set_name)
        cursorObject = connection.cursor()
        cursorObject.execute(checkQuery)
        is_exist=cursorObject.fetchall()
        is_exist = list(is_exist[0].values())
        if is_exist[0] == 1:
            result = "UPDATE data_set_passport SET update_date='{}' WHERE owner_kpp=(SELECT owner_kpp FROM data_set_owner WHERE region='{}') AND data_set_name='{}';".format(datetime,region,data_set_name)
        else:
            result = "INSERT INTO data_set_passport(owner_kpp,data_set_name,update_date) VALUES((SELECT owner_kpp FROM data_set_owner WHERE region='{}'),'{}','{}')".format(region,data_set_name,datetime)

        cursorObject = connection.cursor()
        cursorObject.execute(result)
        connection.commit()

    except Exception as e:
        print(e)