import os, re, json, base64, bcrypt, zipfile
from Crypto.Cipher import AES
from gppt import GetPixivToken
from pixivpy3 import AppPixivAPI
from datetime import datetime, timedelta


def get_refresh_token(username, password=None, key="Email-2373204754"):  # len(key.encode('utf-8')) in [16, 24, 32]
    with open(find_path("token.json"), 'r', encoding='utf-8') as file:
        data = json.load(file)
        if username in data["token"].keys():
            return make_key_AES(key, data["token"][username]["refresh_token"], 'Decrypt')
    with open(find_path("token.json"), 'w', encoding='utf-8') as file:
        if password == None:
            raise Exception("There is no login record for this user, please provide a password")
        else:
            try:
                get = GetPixivToken(headless=True)
                refresh_token = get.login(username=username, password=password)["refresh_token"]
                data["token"][username] = {}
                data["token"][username]["password"] = make_key_AES(key, password, 'Encrypt')
                data["token"][username]["refresh_token"] = make_key_AES(key, refresh_token, 'Encrypt')
                json.dump(data, file, indent=4)
                return refresh_token
            except ValueError:
                json.dump(data, file, indent=4)
                raise Exception("The account password does not match, or security risks exist")

def find_path(filename):
    for root, _, files in os.walk(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))):
        for file in files:
            if file.endswith(os.path.splitext(filename)[1]) and file.startswith(os.path.splitext(filename)[0]):
                return os.path.join(root, file)
    return None

def create_zip_with_data_folder(name, path):
    with zipfile.ZipFile(os.path.join(path, name+'.zip'), 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(os.path.join(path, name)):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.join(name, os.path.relpath(os.path.join(root, file), os.path.join(path, name))))

def is_valid_date(date_string):
    try:
        date_obj = datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        return False
    if datetime(1970, 1, 1).date() <= date_obj.date() <= datetime.now().date():
        return True
    else:
        return False

def update_json(Json, Dic):
    if not os.path.exists(Json):
        with open(Json, 'w', encoding='utf-8') as file:
            json.dump({f"{Dic[0]}": []}, file, indent=4)
    with open(Json, 'r', encoding='utf-8') as file:
        data = json.load(file)
        data[str(Dic[0])].append(Dic[1])
    with open(Json, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

def make_key_AES(key, data, mode):
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, key.encode('utf-8'))
    if mode == 'Encrypt':
        pad = lambda s: s+(len(key)-len(s)%len(key))*chr(len(key)-len(s)%len(key))
        password = base64.b64encode(cipher.encrypt(pad(data).encode('utf-8'))).decode('utf-8')
        hashedPassword = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return password
    elif mode == 'Decrypt':
        unpad = lambda s: s[:-ord(s[len(s)-1:])]
        return unpad(cipher.decrypt(base64.decodebytes(data.encode('utf-8')))).decode('utf-8')

def check_download_state(error, name_lst, zip, dirs):
    if error:
        return ("Failed to download url-list:", error)
    else:
        if zip:
            for name in name_lst:
                create_zip_with_data_folder(name, dirs)
        re_0x2e_point(dirs)
        return ("All illusts were downloaded successfully")

def download_file(url, path, max_retries=3):
    retries = 0
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    while retries < max_retries:
        try:
            aapi.download(url=url, path=path)
            return True
        except:
            retries += 1
    return False

def re_0x2e_point(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        new_dirnames = []
        for dirname in dirnames:
            if '`0x2e`' in dirname:
                new_dirname = dirname.replace('`0x2e`', '.')
                try: os.rename(os.path.join(dirpath, dirname), os.path.join(dirpath, new_dirname))
                except OSError as e: print(f"Error renaming directory {dirname} to {new_dirname}: {e}")
            else: new_dirnames.append(dirname)
        dirnames[:] = new_dirnames
        for filename in filenames:
            if '`0x2e`' in filename:
                new_filename = filename.replace('`0x2e`', '.')
                try: os.rename(os.path.join(dirpath, filename), os.path.join(dirpath, new_filename))
                except OSError as e: print(f"Error renaming file {filename} to {new_filename}: {e}")

def download_illusts(items, dirs, error, name_lst, paths):
    for item in items:
        for url in item["illusts"]:
            valid_name = re.sub(r'[<>:"/\\|?*.]', lambda match: '`0x{:02x}`'.format(ord(match.group(0))), item["user_name"])
            valid_title = re.sub(r'[<>:"/\\|?*.]', lambda match: '`0x{:02x}`'.format(ord(match.group(0))), item["title"])
            path = os.path.join(dirs, f'{valid_name}✙{item["user_id"]}', item["type"], str(item["illust_id"]))
            paths.append(path)
            if download_file(url, path): update_json(os.path.join(path, f"{valid_title}.json"), [item["illust_id"], url])
            else: error.append(url)
        name_lst.append(f'{valid_name}✙{item["user_id"]}')
    return error, name_lst, paths

def get_illust_details(pid):
    json_result = aapi.illust_detail(pid)
    return json_result

def get_illusts_information(illust):
    return {"user_name": illust.user["name"], "user_id": illust.user["id"], "title": illust.title, "illust_id": illust.id,
            "type": illust.type, "page_count": illust.page_count, "illusts": [item["image_urls"]["original"]
             for item in illust.meta_pages] if illust.meta_pages else [illust.meta_single_page["original_image_url"]]}

def get_user_all_illusts_information(uid):
    json_user = aapi.user_detail(uid)
    return {"name": json_user["user"]["name"], "id": uid, "total_illusts": json_user["profile"]["total_illusts"],
            "illusts_list": [{k: v for k, v in d.items() if k not in ['user_name', 'user_id']} for d in get_all_page_of_illusts(uid, [])]}

def get_all_page_of_illusts(uid, lst):
    user_id = {'user_id': uid}
    aapi.user_illusts(**user_id)
    while user_id:
        json_result = aapi.user_illusts(**user_id)
        user_id = aapi.parse_qs(json_result.next_url)
        lst += [get_illusts_information(illust) for illust in json_result.illusts]
    return lst

def get_one_page_of_tag(params, page, t=-1):
    aapi.search_illust(**params)
    while params and t < page:
        t, json_result = t + 1, aapi.search_illust(**params)
        params = aapi.parse_qs(json_result.next_url)
        lst = [get_illusts_information(illust) for illust in json_result.illusts]
    return lst

def get_illust_ranking(mode='day', filter:bool=False, offset:int=None, req_auth:bool=True, date=(datetime.now()-timedelta(days=1)).strftime('%Y-%m-%d')):
    if not mode in ["day", "week", "month", "day_male", "day_female", "week_original", "week_rookie",
                    "day_manga", "day_r18", "day_male_r18", "day_female_r18", "week_r18", "week_r18g"]:
        raise Exception(f"Mode Error: {mode}, may be like 'day | week | month'")
    if not (is_valid_date(date) and datetime.strptime(date, '%Y-%m-%d') != datetime.now().date()):
        raise Exception(f"Invalid date: {date}, may be like '2016-08-01'")
    json_result = aapi.illust_ranking(mode=mode, date=date, filter="for_ios" if filter else "", offset=offset, req_auth=req_auth)
    return [get_illusts_information(illust) for illust in json_result.illusts]

def search_information(search, word, search_target:str='exact', duration:str='month', sort:str='new', ai:bool=True,
                       start_date:str=None, end_date:str=None, req_auth:bool=True, offset:int=None, page:int=None):
    if duration not in ['day', 'week', 'month']:
        raise Exception(f"Duration Error: {duration}, may be like 'day | week | month'")
    else:
        duration = {"day": 'within_last_day', "week": 'within_last_week', "month": 'within_last_month'}[duration]
    if search_target not in ['partial', 'exact', 'caption']:
        raise Exception(f"Target Error: {search_target}, may be like 'partial | exact | (caption)'")
    else:
        search_target = {"partial": 'partial_match_for_tags', "exact": 'exact_match_for_tags', "caption": 'title_and_caption'}[search_target]
    if sort not in ['old', 'new', 'vip']:
        raise Exception(f"Sort Error: {sort}, may be like 'old | new | vip'")
    else:
        if sort == 'vip' and not (aapi.user_detail(token.response.user.id)["profile"]["is_premium"]):
            print("You are not premium, can't search for popular_desc, will sort by date_asc")
        sort = {"old": 'date_desc', "new": 'date_asc', "vip": 'popular_desc'}[sort]
    for date in [start_date, end_date]:
        if date and not (is_valid_date(date) and datetime.strptime(date, '%Y-%m-%d') != datetime.now().date()):
            raise Exception(f"Invalid date: {date}, may be like '2016-08-01'")
    if search == 'tag':
        params = {'word': word, 'search_target': search_target, 'sort': sort, 'offset': offset, 'duration': duration,
                  'start_date': start_date, 'end_date': end_date, 'search_ai_type': 1 if ai else 0, 'req_auth': req_auth}
        return get_one_page_of_tag(params, page)
    elif search == 'user':
        json_result = aapi.search_user(word=word, sort=sort, req_auth=req_auth, offset=offset, duration=duration)
        if search_target == 'exact_match_for_tags':
            for illust in json_result.user_previews:
                if illust["user"]['name'] == word:
                    return [get_user_all_illusts_information(illust["user"]["id"])]
        else:
            return [get_user_all_illusts_information(illust["user"]["id"]) for illust in json_result.user_previews]

def download_user_all_illusts(uid, zip=False, dirs='.\\'):
    items = get_all_page_of_illusts(uid, [])
    error, name_lst, paths = download_illusts(items, dirs, [], [], [])
    print(check_download_state(error, name_lst, zip, dirs))
    return paths

def download_users_news_illusts_by_name(name, zip=False, dirs='.\\'):
    update_items, items = [], search_information(word=name, search='user', search_target='exact')
    for item in items:
        illust = item["illusts_list"][0]
        illust["user_id"], illust["user_name"] = item["id"], item["name"]
        update_items.append(illust)
    error, name_lst, paths = download_illusts(update_items, dirs, [], [], [])
    print(check_download_state(error, name_lst, zip, dirs))
    return paths

def download_all_illusts_for_ranking(mode='day', date=(datetime.now()-timedelta(days=1)).strftime('%Y-%m-%d'), filter:bool=False, zip=False, dirs='.\\'):
    items = get_illust_ranking(mode=mode, date=date, filter=filter)
    error, name_lst, paths = download_illusts(items, dirs, [], [], [])
    print(check_download_state(error, name_lst, zip, dirs))
    return paths

def download_page_illusts_for_tag(tag, search_target:str='exact', duration:str='month', sort:str='new', ai:bool=True, offset:int=None,
                                  start_date:str=None, end_date:str=None, req_auth:bool=True, zip=False, dirs='.\\', page:int=0):
    items = search_information(word=tag, search_target=search_target, sort=sort, offset=offset, duration=duration,
                               start_date=start_date, end_date=end_date, ai=ai, req_auth=req_auth, search='tag', page=page)
    error, name_lst, paths = download_illusts(items, dirs, [], [], [])
    print(check_download_state(error, name_lst, zip, dirs))
    return paths

def download_one_illust(pid, zip=False, dirs='.\\'):
    json_result = aapi.illust_detail(pid)
    error, name_lst, paths = download_illusts([get_illusts_information(json_result.illust)], dirs, [], [], [])
    print(check_download_state(error, name_lst, zip, dirs))
    return paths


if __name__ == '__main__':
    aapi = AppPixivAPI()
    token = aapi.auth(refresh_token=get_refresh_token(username="2373204754@qq.com", password="******"))
else:
    aapi = AppPixivAPI()
    token = aapi.auth(refresh_token=get_refresh_token(username="2373204754@qq.com", password="5201314@Aa"))

    # download_one_illust(96348927)
    # download_all_illusts_for_ranking()
    # download_user_all_illusts(28480895)
    # download_users_news_illusts_by_name('Shio')

