#!/usr/bin/env python3

import sys
import urllib
import time
import requests

# Kano.is username & API token
kanouser = 'wobbzz'
kanoapi = 'x'

# Pushover app user key and token
pushoveruser = 'x'
pushovertoken = 'x'

# Interval in minutes to check status
interval = 10

# Acceptable hashrate. Ensure you have the right amount of 0's :)
hashrate = 12000000000000


def printstatus(status):
    # Quick check to ensure we got usable data back
    if 'w_hashrate1hr:0' in status:

        workercount = int(status['rows'])

        for i in range(workercount):
            fivemin = float(status['w_hashrate5m:{}'.format(i)])/1000000000000
            onehr = float(status['w_hashrate1hr:{}'.format(i)])/1000000000000
            oneday = float(status['w_hashrate24hr:{}'.format(i)])/1000000000000

            print("{}".format(time.strftime("%m/%d/%Y %H:%M:%S -")),
                  "Worker: {} |".format(status["workername:{}".format(i)]),
                  "5 min: {:.3f}TH/s |".format(fivemin),
                  "1 hour: {:.3f}TH/s |".format(onehr),
                  "24 hour: {:.3f}TH/s".format(oneday))


def gethashrate():
    url = ('https://www.kano.is/index.php?k=api&username='
           '{}&api={}&json=y&work=y'.format(kanouser, kanoapi))

    try:
        r = requests.get(url=url)
        return r.json()
    except:
        try:
            sendpushover("Is Kano down?: {}".format(str(sys.exc_info()[0])))
        except:
            print("Is the internet down?")


def checkhashrate(status, workers):
    if 'w_hashrate1hr:0' in status:
        workercount = int(status['rows'])

        for i in range(workercount):
            worker = status["workername:{}".format(i)]
            onehour = float(status['w_hashrate1hr:{}'.format(i)])

            if worker not in workers:
                workers[worker] = 'down'

            if onehour < hashrate:
                if workers[worker] == 'up':
                    sendpushover("{} hashrate is below desired "
                                 "average.".format(worker))
                    workers[worker] = 'down'
            elif onehour > hashrate:
                if workers[worker] == 'down':
                    sendpushover("{} hashrate has returned to "
                                 "desired average.".format(worker))
                    workers[worker] = 'up'

    return workers


def sendpushover(msg):
    print(msg)
    api = 'https://api.pushover.net/1/messages.json'
    message = {"token": "{}".format(pushovertoken),
               "user": "{}".format(pushoveruser),
               "message": "{}".format(msg)}
    # print(urllib.parse.urlencode(message))
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    requests.post(api, headers=headers,
                  data=urllib.parse.urlencode(message))
    # print(r.status_code, r.text)


def main():
    workers = dict()

    while True:
        status = gethashrate()
        workers = checkhashrate(status, workers)
        printstatus(status)
        time.sleep(interval * 60)


main()
