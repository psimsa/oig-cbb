import asyncio
import json

import aiohttp

baseurl = 'https://www.oigpower.cz/cez/'
loginurl = 'inc/php/scripts/Login.php'
getstatsurl = 'json.php'

user = '[oig email]'
pwd = '[oig password]'


async def login(username: str, password: str) -> aiohttp.ClientSession:
    print('Logging in')
    login_command = {"email": username, "password": password}

    session = aiohttp.ClientSession()
    async with session.post(baseurl + loginurl, data=json.dumps(login_command),
                            headers={'Content-Type': 'application/json'}) as response:
        if response.status == 200:
            responsecontent = await response.text()
            if responsecontent == '[[2,"",false]]':
                # Save PHPSESSID to cookies.txt
                phpsessid = session.cookie_jar.filter_cookies(baseurl).get('PHPSESSID')
                if phpsessid:
                    with open('cookies.txt', 'w') as f:
                        f.write(phpsessid.value)
            else:
                await session.close()
                raise Exception('Login failed')
    return session


async def getStatsUsingSavedCookiesOrLogin(username: str, password: str) -> object:
    try:
        with open('cookies.txt', 'r') as f:
            phpsessid: str = f.read()
            async with aiohttp.ClientSession(headers={'Cookie': f'PHPSESSID={phpsessid}'}) as session:
                return await getstats(session)
    except:
        async with await login(username, password) as session:
            return await getstats(session)


async def getstats(session: aiohttp.ClientSession) -> object:
    toReturn: object
    async with session.get(baseurl + getstatsurl) as response:
        if response.status == 200:
            toReturn = await response.json()
            # the response should be a json dictionary, otherwise it's an error
            if not isinstance(toReturn, dict):
                await session.close()
                raise Exception('Error getting stats')
    return toReturn


def printStatistics(stats: object):
    for key in stats:
        print(f'Unit ID: {key}')
        panelsOutputL1 = stats[key]["dc_in"]["fv_p1"]
        print(f'Panels output string 1: {panelsOutputL1} W')
        panelsOutputL2 = stats[key]["dc_in"]["fv_p2"]
        print(f'Panels output string 2: {panelsOutputL2} W')
        panelsOutputPct = stats[key]["dc_in"]["fv_proc"]
        print(f'Panels output pct: {panelsOutputPct} %')
        batteryPct = stats[key]["batt"]["bat_c"]
        print(f'Battery pct: {batteryPct} %')
        consumptionL1 = stats[key]["ac_out"]["aco_pr"]
        print(f'Consumption line 1: {consumptionL1} W')
        consumptionL2 = stats[key]["ac_out"]["aco_ps"]
        print(f'Consumption line 2: {consumptionL2} W')
        consumptionL3 = stats[key]["ac_out"]["aco_pt"]
        print(f'Consumption line 3: {consumptionL3} W')
        consumptionTotal = stats[key]["ac_out"]["aco_p"]
        print(f'Consumption total: {consumptionTotal} W')
        gridOutputL1 = stats[key]["ac_in"]["aci_wr"]
        print(f'Grid output line 1: {gridOutputL1} W')
        gridOutputL2 = stats[key]["ac_in"]["aci_ws"]
        print(f'Grid output line 2: {gridOutputL2} W')
        gridOutputL3 = stats[key]["ac_in"]["aci_wt"]
        print(f'Grid output line 3: {gridOutputL3} W')
        gridOutputTotal = gridOutputL1 + gridOutputL2 + gridOutputL3
        print(f'Grid output total: {gridOutputTotal} W')
        outputToday = stats[key]["dc_in"]["fv_ad"]
        print(f'Output today: {outputToday} Wh')
        consumptionToday = stats[key]["ac_out"]["en_day"]
        print(f'Consumption today: {consumptionToday} Wh')
        gridConsumptionToday = stats[key]["ac_in"]["ac_ad"]
        print(f'Grid consumption today: {gridConsumptionToday} Wh')
        gridDeliveryToday = stats[key]["ac_in"]["ac_pd"]
        print(f'Grid delivery today: {gridDeliveryToday} Wh')
        batteryChargeToday = stats[key]["batt"]["bat_apd"]
        print(f'Battery charge today: {batteryChargeToday} Wh')
        batteryDischargeToday = stats[key]["batt"]["bat_and"]
        print(f'Battery discharge today: {batteryDischargeToday} Wh')
        lastCall = stats[key]["device"]["lastcall"]
        print(f'Last call: {lastCall}')
        operationMode = stats[key]["box_prms"]["mode"]
        print(f'Operation mode: {operationMode}')


async def main():
    stats = await getStatsUsingSavedCookiesOrLogin(user, pwd)
    printStatistics(stats)

if __name__ == '__main__':
    asyncio.run(main())
