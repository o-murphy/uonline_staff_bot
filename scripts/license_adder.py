from scripts import pywlapi
from datetime import datetime


def getacc(host, token, account):
    try:
        eid = pywlapi.login(host=host, token=token, user='')['eid']
        svc = 'core/search_items'
        params = {"spec": {"itemsType": "avl_resource",
                           "propName": "sys_name",
                           "propValueMask": account,
                           "sortType": "sys_name"},
                  "force": 1,
                  "flags": 5,
                  "from": 0,
                  "to": 0}
        items = pywlapi.request(host=host, svc=svc, params=params, eid=eid)['items']
        empty = []
        if items == empty:
            raise IndexError
        id = ''
        for item in items:
            if account == item['nm']:
                id = item['bact']
                return id
        if id == '':
            raise IndexError
    except IndexError as e:
        print(e)
        id = 'wrong'
        return id


def adder(host, token, id, add):
    eid = pywlapi.login(host=host, token=token, user='')['eid']
    svc = 'account/get_account_data'
    params = {"itemId": id, "type": ""}
    acc = pywlapi.request(host=host, svc=svc, params=params, eid=eid)
    total = acc['settings']['personal']['services']['avl_unit']['maxUsage']
    print(total)
    svc = "account/update_billing_service"
    params = {
        "itemId": id,
        "name": "avl_unit",
        "type": 2,
        "intervalType": "0",
        "costTable": f"{total+add}:0;-1"
    }
    pywlapi.request(host=host, svc=svc, params=params, eid=eid)
    return(f'Total: {total+add}')
    #
    # return total

    #
    # svc = 'account/get_account_data'
    # params = {"itemId": id, "type": ""}
    # days_counter = pywlapi.request(host=server, svc=svc, params=params, eid=eid)['daysCounter']
    # pass
    #
