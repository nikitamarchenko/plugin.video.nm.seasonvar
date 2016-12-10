from collections import defaultdict

from xbmcswift2 import xbmcgui
from xbmcswift2 import xbmc

from xbmcswift2 import actions

import xbmcswift2

import requests
from BeautifulSoup import BeautifulSoup

plugin = xbmcswift2.Plugin()


def is_activated():
    storage = plugin.get_storage()
    keys = storage.keys()
    return 'svid' in keys and 'api_key' in keys


@plugin.route('/')
def index():
    result = []

    if is_activated():
        result.append(
            {'label': 'Serials list by name',
             'path': plugin.url_for('serial_list')}
        )

    result.append({'label': 'Settings',
                   'path': plugin.url_for('settings')})

    result.append({'label': 'BBT',
                   'path': plugin.url_for('show_serial', season_id=14242)})

    return result


@plugin.route('/settings/')
def settings():
    return [
        {'label': 'Config',
         'path': plugin.url_for('config')},
        {'label': 'Activate',
         'path': plugin.url_for('activate')},
    ]


@plugin.route('/settings/config')
def config():
    plugin.open_settings()


@plugin.route('/settings/activate/')
def activate():
    try:
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
            plugin.notify(
                'Problems with login, please check login and password '
                'and try again')
            plugin.log.error('Login error')
            dialog.close()
            raise

        dialog.update(50, 'Get API Key')

        response = session.get('http://seasonvar.ru?mod=api')
        if response.status_code == 200:
            try:
                soup = BeautifulSoup(response.text)
                key = \
                    soup.findAll(
                        value=lambda (value): value and len(value) == 8)[
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
                raise

            plugin.notify('Excellent!')
            plugin.log.error('Success!')
            dialog.close()
    finally:
        xbmc.executebuiltin(actions.update_view(plugin.url_for('index')))


@plugin.route('/serial_list')
def serial_list():
    serials = get_serial_names_map()

    return [{
                'label': s,
                'path': plugin.url_for('serial_list_second_layer',
                                       letter=s.encode('utf-8'))
            }
            for s in sorted(serials.keys())]


@plugin.route('/serial_list_second_layer/<letter>')
def serial_list_second_layer(letter):
    serials = get_serial_names_map()
    return [{
                'label': s,
                'path': plugin.url_for('serial_list_last_layer',
                                       letters=s.encode('utf8'))
            }
            for s in sorted(serials[unicode(letter, encoding='utf-8')].keys())]


@plugin.route('/serial_list_last_layer/<letters>')
def serial_list_last_layer(letters):
    plugin.set_content('tvshows')
    letters = unicode(letters, encoding='utf-8')
    serials = get_serial_names_map()
    first = letters[0] if letters[0].isalpha() else '<Else>'
    return [{
                'label': name,
                'thumbnail': 'http://cdn.seasonvar.ru/oblojka/{0}.jpg'.format(
                    season_id),
                'path': plugin.url_for('show_serial', season_id=season_id),
                'info': {
                    'mediatype': 'tvshow',
                }
            }
            for name, season_id in serials[first][letters]]


def seasonvar_get_serial_list():
    storage = plugin.get_storage()
    data = {'key': storage['api_key'], 'command': 'getSerialList'}
    r = requests.post('http://api.seasonvar.ru/', data=data)
    if r.ok:
        r = r.json()
        return r


def serials_list_sync():
    serial_map_by_id = plugin.get_storage('serial_map_by_id', TTL=60 * 24)
    serial_names_map = plugin.get_storage('serial_names_map', TTL=60 * 24)

    if 'data' in serial_map_by_id and 'data' in serial_names_map:
        return
    dialog = xbmcgui.DialogProgress()
    dialog.create('Loading', 'Loading serials data')
    raw_list = seasonvar_get_serial_list()
    dialog.update(5, 'Sorting')
    id_dict = dict()
    temp = defaultdict(lambda: defaultdict(list))

    count = len(raw_list)
    percent = count / 100.
    step = 5
    set_percent = 5
    for i, serial in enumerate(raw_list):
        current_percent = i / percent
        if current_percent - set_percent > step:
            set_percent = int(current_percent)
            dialog.update(set_percent, 'Sorting')

        id_dict[serial['last_season_id']] = serial
        name = serial['name'].upper()
        first = name[0] if name[0].isalpha() else '<Else>'
        temp[first][name[:2]].append((serial['name'],
                                      serial['last_season_id']))

    two_letters_navigation = {}
    for k in temp.keys():
        two_letters_navigation[k] = dict()
        for kk in temp[k].keys():
            two_letters_navigation[k][kk] = temp[k][kk]

    serial_names_map['data'] = two_letters_navigation
    serial_names_map.sync()
    serial_map_by_id['data'] = id_dict
    serial_map_by_id.sync()


def get_serial_names_map():
    serial_names_map = plugin.get_storage('serial_names_map', TTL=60 * 24)
    try:
        return serial_names_map['data']
    except KeyError:
        serials_list_sync()
        return serial_names_map['data']


def seasonvar_get_serial_seasons_list(season_id):
    storage = plugin.get_storage()
    data = {'key': storage['api_key'],
            'command': 'getSeasonList',
            'id': season_id}
    r = requests.post('http://api.seasonvar.ru/', data=data)
    if r.ok:
        r = r.json()
        return r


@plugin.route('/show_serial/<season_id>')
def show_serial(season_id):
    plugin.set_content('seasons')
    seasons = seasonvar_get_serial_seasons_list(season_id)
    return [{
                'label': "{0} {1}".format("Season", s.get('season_number', 1)),
                'thumbnail': s['poster'],
                'path': plugin.url_for('show_season', season_id=s['id']),
                'info': {
                    'mediatype': 'season',
                    'tvshowtitle': s['name'],
                    'year': s['year'],
                    'genre': s['genre'],
                    'country': s['country'],
                    'season': s.get('season_number', 1),
                    'plot': s['description']
                }
            }
            for s in seasons]


def seasonvar_get_episodes_list(season_id):
    storage = plugin.get_storage()
    data = {'key': storage['api_key'],
            'command': 'getSeason',
            'season_id': season_id}
    r = requests.post('http://api.seasonvar.ru/', data=data)
    if r.ok:
        r = r.json()
        return r


@plugin.route('/show_season/<season_id>')
def show_season(season_id):
    plugin.set_content('episodes')

    # episodes.keys() [u'rating',
    # u'playlist',
    # u'name',
    # u'poster',
    # u'other_season',
    # u'poster_small',
    # u'name_original',
    # u'year',
    # u'genre',
    # u'country',
    # u'season_number',
    # u'id',
    # u'description']

    episodes = seasonvar_get_episodes_list(season_id)
    # playlist.keys() [u'subtitles', u'link', u'name', u'perevod']

    return [{
                'label': u"{0} {1}".format(e['name'], e.get('perevod', '')),
                'thumbnail': episodes['poster'],
                'path': e['link'],
                'info': {
                    'mediatype': 'episode',
                    'tvshowtitle': episodes['name'],
                    'year': episodes['year'],
                    'genre': episodes['genre'],
                    'country': episodes['country'],
                    'season': episodes.get('season_number', 1)
                },
                'is_playable': True
            }
            for e in episodes['playlist']]


if __name__ == '__main__':
    plugin.run()
