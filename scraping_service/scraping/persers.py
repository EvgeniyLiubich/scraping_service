import requests
import codecs
from bs4 import BeautifulSoup as BS
from random import randint

__all__ = ('jobs_dev', 'jobs_tut')

headers = [{'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:47.0) Gecko/20100101 Firefox/47.0',
            'Accept': 'text/html, application/xhtml+xml, application/xml;q=0.9,*/*;q=0.8'},
           {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/449.0.2623.112 Safari/537.36',
            'Accept': 'text/html, application/xhtml+xml, application/xml;q=0.9,*/*;q=0.8'},
           {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:53.0) Gecko/20100101 Firefox/53.0',
            'Accept': 'text/html, application/xhtml+xml, application/xml;q=0.9,*/*;q=0.8'}
           ]


def jobs_dev(url, city=None, language=None):
    jobs = []
    errors = []
    domain = 'https://jobs.dev.by'
    if url:
        resp = requests.get(url, headers=headers[randint(0, 2)])

        if resp.status_code == 200:
            soup = BS(resp.content, 'html.parser')
            main_div = soup.find('div', class_="vacancies-list__body js-vacancies-list__body")
            if main_div:
                div_lst = main_div.find_all('div',
                                            attrs={'class': 'vacancies-list-item__body js-vacancies-list-item--open'})
                for div in div_lst:
                    title = div.find('a')
                    href = title['href']
                    content = div.a.text
                    company = div.find('div', class_="vacancies-list-item__company").text
                    jobs.append({'title': title.text, 'url': domain + href,
                                 'description': content, 'company': company,
                                 'city_id': city, 'language_id': language})
                    # print(company, '----', content, '----', domain+href)
                    # print(jobs)
            else:
                errors.append({'url': url, 'title': 'Div do not response'})
        else:
            errors.append({'url': url, 'title': 'Page do not response'})
    return jobs, errors


def jobs_tut(url, city=None, language=None):
    jobs = []
    errors = []
    if url:
        resp = requests.get(url, headers=headers[randint(0, 2)])
        # print(resp.status_code)

        if resp.status_code == 200:
            soup = BS(resp.content, 'html.parser')
            main_div = soup.find('div', class_="vacancy-serp")

            if main_div:
                div_lst = main_div.find_all('div', attrs={'class': 'vacancy-serp-item'})
                for div in div_lst:
                    title = div.find('a', attrs={'class': 'bloko-link HH-LinkModifier'}).text
                    href = div.find('a').get('href')
                    content = div.find('div', attrs={'class': 'g-user-content'}).text
                    company = div.find('div', attrs={'class': 'vacancy-serp-item__meta-info'}).text
                    jobs.append({'title': title, 'url': href,
                                 'description': content, 'company': company,
                                 'city_id': city, 'language_id': language})

                    # print(title, '---', company, '-----', href, '----', content)
            else:
                errors.append({'url': url, 'title': 'Div do not response'})
        else:
            errors.append({'url': url, 'title': 'Page do not response'})
    return jobs, errors


if __name__ == '__main__':
    url = 'https://jobs.tut.by/search/vacancy?st=searchVacancy&text=&specialization=1&industry=7&area=1002&salary=&currency_code=BYR&experience=doesNotMatter&order_by=relevance&search_period=&items_on_page=50&no_magic=true&L_save_area=true&customDomain=1'
    jobs, errors = jobs_tut(url)
    print(jobs)

    h = codecs.open('work.json', 'w', 'utf-8')
    h.write(str(jobs))
    h.close()
