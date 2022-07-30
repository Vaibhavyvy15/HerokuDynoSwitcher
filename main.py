# https://github.com/HuzunluArtemis/HerokuDynoSwitcher
# License: https://github.com/HuzunluArtemis/HerokuDynoSwitcher/blob/main/LICENSE

import time, os, heroku3, requests, datetime

def changeDyno(api, name, islem=0):
    # islem: 1: start app, 0: stop app
    try:
        heroku_conn = heroku3.from_key(api)
        app = heroku_conn.app(name)
        proclist = app.process_formation()
        for po in proclist: app.process_formation()[po.type].scale(islem)
        return True
    except Exception as e:
        print(e)
        return False

CONFIG_FILE_URL = str(os.environ.get('CONFIG_FILE_URL',""))
print(f"\n[CHECK] HuzunluArtemis/HerokuDynoSwitcher")
try:
    if len(CONFIG_FILE_URL.strip()) == 0:
        raise TypeError
    try:
        if os.path.isfile('dynos'): os.remove('dynos')
        res = requests.get(CONFIG_FILE_URL)
        if res.status_code == 200:
            f = open('dynos', 'wb+')
            f.write(res.content)
            f.close()
        else:
            print(f"Failed to download config.env {res.status_code}")
    except Exception as e:
        print(f"Error while get config file: {e}")
        exit(1)
except TypeError:
    print("Your CONFIG_FILE_URL was empty. Please read readme.")
    exit(1)

try:
    dynos = open("dynos", "r", encoding="UTF-8").read().strip().split("\n\n")
    if os.path.isfile('dynos'): os.remove('dynos')
except Exception as e:
    print(f"Error while reading config file: {e}")
    exit(1)

now = failed = success = 0
for dyno in dynos:
    now += 1
    try:
        name1, api1, name2, api2 = dyno.split("\n")
    except Exception as e:
        print(f"[#{now}] Error when parsing item: {now}. Skipped.")
        continue
    print(f"\n[#{now}] Changing the dyno.")
    proc = changeDyno(api1, name1, 1 if datetime.datetime.now().day == 1 else 0)
    if not proc:
        print(f"[#{now}] First app cannot stopped. Skipped.")
        failed += 1
    else:
        print(f"[#{now}] First app stopped. Waiting 5 secs.")
        success += 1
    time.sleep(5)
    proc = changeDyno(api2, name2, 0 if datetime.datetime.now().day == 1 else 1)
    if not proc:
        print(f"[#{now}] Second app cannot started. Skipped.")
        failed += 1
    else:
        print(f"[#{now}] Second app started. Waiting 5 secs.")
        success += 1
    print(f"\nTotal Process (start, stop) Success: {success} Failed: {failed}")
    time.sleep(5)
print(f"\nThanks for using HuzunluArtemis/HerokuDynoSwitcher\nTotal Process (start, stop) Success: {success} Failed: {failed}")
