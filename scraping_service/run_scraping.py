import asyncio
import codecs
import os, sys
import datetime as dt

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

jobs, errors = [], []


def get_settings():
    """Настройки по умолчанию"""
    qs = User.objects.filter(send_email=True).values()  # Получим словари
    settings_lst = set((q['city_id'], q['language_id']) for q in qs)
    return settings_lst


def get_urls(_settings):
    qs = Url.objects.all().values()
    url_dict = {(q['city_id'], q['language_id']): q['url_data'] for q in qs}
    urls = []
    for pair in _settings:
        if pair in url_dict:
            tmp = {}
            tmp['city'] = pair[0]
            tmp['language'] = pair[1]
            url_data = url_dict.get(pair)
            if url_data:
                tmp['url_data'] = url_dict.get(pair)
                urls.append(tmp)
    return urls


async def main(value):
    func, url, city, language = value
    job, err = await loop.run_in_executor(None, func, url, city, language)
    errors.extend(err)
    jobs.extend(job)


settings = get_settings()
url_list = get_urls(settings)

# city = City.objects.filter(slug='minsk').first()
# language = Language.objects.filter(slug='python').first()
import time

start = time.time()
loop = asyncio.get_event_loop()
tmp_tasks = [(func, data['url_data'][key], data['city'], data['language'])
             for data in url_list
             for func, key in parsers]

# for data in url_list:
#
#     for func, key in parsers:
#         url = data['url_data'][key]
#         j, e = func(url, city=data['city'], language=data['language'])
#         jobs += j
#         errors += e
#     # print(jobs)

if tmp_tasks:
    tasks = asyncio.wait([loop.create_task(main(f)) for f in tmp_tasks])
    loop.run_until_complete(tasks)
    loop.close()

print(time.time() - start)
for job in jobs:
    # l = Language(name='Python')
    # l.save()
    v = Vacancy(**job)
    # v.save()
    try:
        v.save()
        print('Вакансия сохранена')
    except DatabaseError:
        print('Ошибка')
if errors:
    qs = Error.objects.filter(timestamp=dt.date.today())
    if qs.exists():
        err = qs.first()
        err.data.update({'errors': errors})
        err.save()
    else:
        er = Error(data=f'errors:{errors}').save()
print(time.time() - start)
# h = codecs.open('work.json', 'w', 'utf-8')
# h.write(str(jobs))
# h.close()
