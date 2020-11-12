from scripts import pywlapi
from datetime import datetime

def run(server, token, userlist, someday):
    some_day = datetime.strptime(someday, '%d.%m.%Y')
    now = datetime.now()
    eid = pywlapi.login(host=server, token=token, user='')['eid']
    users = userlist.split('\n')
    ok = []
    err = []
    print(users)
    for user in users:
        try:
            print(user)
            svc = 'core/search_items'
            params = {"spec": {"itemsType": "user",
                               "propName": "sys_name",
                               "propValueMask": user,
                               "sortType": "sys_name"},
                      "force": 1,
                      "flags": 5,
                      "from": 0,
                      "to": 0}
            r = pywlapi.request(host=server, svc=svc, params=params, eid=eid)
            print(r)
            id = r['items'][0]['bact']
            svc = 'account/get_account_data'
            params = {"itemId": id, "type": ""}
            days_counter = pywlapi.request(host=server, svc=svc, params=params, eid=eid)['daysCounter']
            days_add = (some_day - now).days - days_counter
            description = f'Access is open until {someday}'
            svc = 'core/batch'
            params = [
                {'svc': 'account/do_payment',
                 'params': {"itemId": id,
                            "balanceUpdate": "0.0",
                            "daysUpdate": days_add,
                            "description": description}
                 },
                {'svc': 'account/enable_account',
                 'params': {"itemId": id,
                            "enable": 1}
                 }
            ]
            r = pywlapi.request(host=server, svc=svc, params=params, eid=eid)

            if r == [{}, {}]:
                ok.append(user)
                # print(ok)
            else:
                err.append(user)
        except IndexError as ex:
            print(ex)
            err.append(user)
    ok_str = f'<b>Updated to {someday}:</b>\n\n' + '\n'.join(ok)
    err_str = '<b>Errors:</b>\n\n' + '\n'.join(err)
    if ok and err:
        msg = f'{ok_str}\n<b>==================</b>\n{err_str}'
    elif ok:
        msg = ok_str
    elif err:
        msg = err_str
    else:
        msg = 'Wrong List!'
    return msg
