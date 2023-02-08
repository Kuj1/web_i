from config import Config
from forms import CheckForm

import os
import time
import concurrent.futures
from datetime import datetime

import asyncio
from flask import Flask, render_template, redirect, url_for, request, send_file, flash
from flask_bootstrap import Bootstrap

import aiohttp
from bs4 import BeautifulSoup


# Timeout: total = total time for connection all proxies (in s.)
#          connect = time to connect each of the proxies (in s.)
TIMEOUT = aiohttp.ClientTimeout(total=300, connect=5)

# Number of worker: the maximum number of processes
NUM_WORKERS = 10
LINK = 'http://checkip.dyndns.org'

# Fraud score: parameter from the json response
FRAUD_SCORE = 25

data_folder = os.path.join(os.getcwd(), 'result_data')
get_folder = os.path.join(os.getcwd(), 'uploaded_file')
unchecked_file = os.path.join(os.getcwd(), get_folder)
checked_proxy = os.path.join(os.getcwd(), data_folder)

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}


app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap(app)


def pop_the_key(keys) -> str:
    return keys.pop()


async def check_proxy(params, key, url, score):
    date_time = datetime.now().strftime('%d.%m.%Y_%H:%M')

    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), timeout=TIMEOUT, headers=headers) as session:
            async with session.get(url, proxy=params) as resp:
                body = await resp.text()
                soup = BeautifulSoup(body, 'lxml')

                ip = soup.find('body').text.replace('Current IP Address:', '').strip()

            for i_key in key:
                api_url = f'https://ipqualityscore.com/api/json/ip/{i_key}/{ip}'

                async with session.get(url=api_url) as resp:
                    r = await resp.json()
                    message = r['message']
                    if message == 'Success':
                        fraud_score = r['fraud_score']

                        print(f'{fraud_score} {api_url} {ip} {params}')
                        # !!!!
                        if fraud_score <= score:
                            with open(os.path.join(data_folder, f'checked_by_api_proxy.txt'), 'a') as checked:
                                pre_proxy = params.replace('http://', '').split('@')[::-1]
                                original_proxy = ':'.join(pre_proxy)
                                checked.write(f'{original_proxy}\n')
                        break
                    else:
                        with open(os.path.join(data_folder, f'expired_key.txt'), 'a') as checked:
                            pre_proxy = params.replace('http://', '').split('@')[::-1]
                            original_proxy = ':'.join(pre_proxy)
                            checked.write(f'Stop in {original_proxy} >>> Api-key: {i_key}\n')
                        continue

    except Exception as ex:
        with open(os.path.join(data_folder, f'log_{date_time}.txt'), 'a') as log:
            message = 'An exception of type {0} occurred.\n[ARGUMENTS]: {1!r}'.format(type(ex).__name__, ex.args)
            log.write(f'\n[PROXY]: {params}\n[ERROR]: {ex}\n[TYPE EXCEPTION]: {message}\n' + '-' * len(message))

    await asyncio.sleep(.15)


def get_and_output(params, key, url, score):
    asyncio.run(check_proxy(params, key, url, score))


def main() -> None:
    modified_proxy = list()
    api_keys = list()
    with open(os.path.join(unchecked_file, 'proxies.txt'), 'r') as prox:
        proxies = ''.join(prox.readlines()).strip().split('\n')
        for proxy in proxies:
            proxy_params = proxy.split(':')
            usefully_proxy_params = f'http://{proxy_params[2]}:{proxy_params[3]}@{proxy_params[0]}:{proxy_params[1]}'
            modified_proxy.append(usefully_proxy_params)

    with open(os.path.join(unchecked_file, 'api_key.txt'), 'r') as keys:
        for key in keys:
            api_key = key.replace('\n', '').strip()
            api_keys.append(api_key)

    # get_and_output(url=LINK, score=FRAUD_SCORE)

    start = time.time()
    workers = NUM_WORKERS

    futures = []
    length_data = len(modified_proxy)

    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        for i_prox in modified_proxy:
            new_future = executor.submit(
                get_and_output,
                params=i_prox,
                key=api_keys,
                url=LINK,
                score=FRAUD_SCORE
            )
            futures.append(new_future)
            length_data -= 1

    concurrent.futures.wait(futures)
    stop = time.time()
    print(stop-start)


@app.route('/', methods=['GET', 'POST'])
# @app.route('/enter_info', methods=['GET', 'POST'])
def upload_file():
    if not os.path.exists(data_folder):
        os.mkdir(data_folder)

    if not os.path.exists(get_folder):
        os.mkdir(get_folder)

    form = CheckForm()

    if form.validate_on_submit():
        with open(os.path.join(get_folder, 'proxies.txt'), 'w') as proxy:
            proxy.write(f'{form.proxy.data}\n')
        with open(os.path.join(get_folder, 'api_key.txt'), 'w') as proxy:
            proxy.write(f'{form.api_key.data}\n')
        print('{}, {}'.format(
            form.proxy.data, form.api_key.data))

        path_to_valid_proxy = os.path.join(data_folder, 'checked_by_api_proxy.txt')
        if os.path.exists(os.path.join(checked_proxy, 'checked_by_api_proxy.txt')):
            os.remove(os.path.join(checked_proxy, 'checked_by_api_proxy.txt'))
        if os.path.exists(os.path.join(checked_proxy, 'expired_key.txt')):
            os.remove(os.path.join(checked_proxy, 'expired_key.txt'))
        files = request.files.getlist("file")

        for file in files:
            if file.filename == '':
                return redirect(url_for('index'))

            if not os.path.exists(get_folder):
                os.mkdir(get_folder)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

        main()
        if os.path.exists(path_to_valid_proxy):
            with open(path_to_valid_proxy, 'r') as checked:
                checked_row = checked.read().strip()
            return render_template('info.html', form=form, checked_row=checked_row)
        elif os.path.exists(os.path.join(checked_proxy, 'expired_key.txt')):
            return render_template('no_valid_key.html', form=form)
        else:
            return render_template('no_valid_proxy.html', form=form)
    return render_template('index.html', title='Check it', form=form)


if __name__ == '__main__':
    app.run(debug=True)
