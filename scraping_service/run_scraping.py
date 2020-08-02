import codecs
import os, sys

from django.contrib.auth import get_user_model

proj = os.path.dirname(os.path.abspath('manage.py'))
sys.path.append(proj)
os.environ['DJANGO_SETTINGS_MODULE'] = 'scraping_service.settings'

import django

django.setup()

from django.db import DatabaseError
from scraping.persers import *
from scraping.models import Vacancy, City, Language, Error, Url

User = get_user_model()

parsers = (
    (jobs_dev, 'jobs_dev'),
    (jobs_tut, 'jobs_tut')
)


def get_settings():
    """Настройки по умолчанию"""
    qs = User.objects.filter(send_email=True).values()  # Получим словари
    settings_lst = set((q['city_id'], q['language_id']) for q in qs)
    return settings_lst


def get_urls(_settings):
    """"""
    qs = Url.objects.all().values()
    url_dict = {(q['city_id'], q['language_id']): q['url_data'] for q in qs}
    urls = []
    for pair in _settings:
        tmp = {}
        tmp['city'] = pair[0]
        tmp['language'] = pair[1]
        tmp['url_data'] = url_dict[pair]
        urls.append(tmp)
    return urls


settings = get_settings()
url_list = get_urls(settings)

# city = City.objects.filter(slug='minsk').first()
# language = Language.objects.filter(slug='python').first()

jobs, errors = [], []
for data in url_list:

    for func, key in parsers:
        url = data['url_data'][key]
        j, e = func(url, city=data['city'], language=data['language'])
        jobs += j
        errors += e
    # print(jobs)

for job in jobs:
    # l = Language(name='Python')
    # l.save()
    v = Vacancy(**job)
    # v.save()
    try:
        v.save()
    except DatabaseError:
        print('Ошибка')
if errors:
    er = Error(data=errors).save()
# h = codecs.open('work.json', 'w', 'utf-8')
# h.write(str(jobs))
# h.close()
