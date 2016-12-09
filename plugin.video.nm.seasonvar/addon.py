from xbmcswift2 import xbmcgui

import xbmcswift2
import requests
from BeautifulSoup import BeautifulSoup

plugin = xbmcswift2.Plugin()


@plugin.route('/')
def index():
    return [{'label': 'Settings',
             'path': plugin.url_for('settings')}
            ]


@plugin.route('/settings/')
def settings():
    storage = plugin.get_storage()
    keys = storage.keys()

    label = 'Activate'
    if 'svid' in keys or 'api_key' in keys:
        label = 'Reactivate'

    return [
            {'label': 'Config',
             'path': plugin.url_for('config')},
            {'label': label,
             'path': plugin.url_for('activate')},
            ]


@plugin.route('/settings/config')
def config():
    plugin.open_settings()


@plugin.route('/settings/activate/')
def activate():

    username = plugin.get_setting('username')
    password = plugin.get_setting('password')

    # http --headers --form POST 'http://seasonvar.ru/?mod=login' login=xxxx@gmail.com password=xxxx

    session = requests.Session()

    dialog = xbmcgui.DialogProgress()
    dialog.create('Activation', 'Login to seasonvar.ru')

    response = session.post('http://seasonvar.ru/?mod=login', data={
        'login': username, 'password': password}, allow_redirects=False)

    try:
        response.cookies['svid']
    except KeyError:
        plugin.notify('Problems with login, please check login and password '
                      'and try again')
        plugin.log.error('Login error')
        dialog.close()
        plugin.finish(succeeded=False)

    dialog.update(50, 'Get API Key')

    response = session.get('http://seasonvar.ru?mod=api')
    if response.status_code == 200:
        try:
            soup = BeautifulSoup(response.text)
            key = \
                soup.findAll(value=lambda (value): value and len(value) == 8)[
                    0][
                    'value']
            storage = plugin.get_storage()
            storage['api_key'] = key
            storage['svid'] = response.cookies['svid']

        except KeyError:
            plugin.notify(
                'Problems with login, please check login and password '
                'and try again')
            plugin.log.error('Api error')
            dialog.close()
            plugin.finish(succeeded=False)

        plugin.notify('Excellent!')
        plugin.log.error('Success!')
        dialog.close()
        plugin.finish()


if __name__ == '__main__':
    plugin.run()
