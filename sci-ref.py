# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re

def check(paper):
    driver = webdriver.Firefox()
    driver.get('http://apps.webofknowledge.com/')

    # search settings

    sid = filter(lambda x: x.find('SID') == 0, driver.current_url.split('&'))[0]

    driver.get('http://apps.webofknowledge.com/WOS_CitedReferenceSearch_input.do?locale=zh_CN&errorKey=&viewType=input&product=WOS&search_mode=CitedReferenceSearch&' + sid)

    driver.find_element_by_class_name('settings-item').find_element_by_xpath('h4').click()
    try:
        cbs = driver.find_elements_by_xpath('//input[@type="checkbox" and @name="editions"]')
        if not cbs[0].is_selected():
            cbs[0].click()
        for cb in cbs[1:]:
            if cb.is_selected():
                cb.click()
    except:
        pass


    # input paper title

    driver.find_element_by_id('s2id_select1').click()
    driver.find_element_by_id('select2-results-1').find_elements_by_tag_name('li')[-1].click()

    driver.find_element_by_id('value(input1)').click()
    driver.find_element_by_id('value(input1)').clear()

#     s = unicode('Distributed data management using mapreduce')
    s = unicode(paper)
    driver.find_element_by_id('value(input1)').send_keys(s)

    # begin search
    driver.find_elements_by_id('WOS_CitedReferenceSearch_input_form_sb')[-1].click()


    #--------------------------------------------------------------------------------------------------

    # show full titles

    empty = False
    while True:
        try:
            driver.find_element_by_id('show_exp_titles_link').click()
            break
        except:
            try:
                driver.find_element_by_id('noRecordsDiv')
                empty = True
                break
            except:
                pass
            time.sleep(1)

    if empty:
#        print 'no result for "%s"' % paper
        driver.quit()
        return

    table = driver.find_element_by_id('records_chunks')
    tbody = table.find_elements_by_tag_name('tbody')[-1]
    tr = tbody.find_elements_by_tag_name('tr')[0]
    td = tr.find_elements_by_tag_name('td')

    td[1].find_elements_by_tag_name('span')[2].click()
    author = td[1].find_elements_by_tag_name('span')[1].text.strip()

#     title = td[2].find_element_by_xpath('span[2]/span').text
    full_title = td[2].find_element_by_xpath('span[2]').text.strip()
    if full_title.find(u'标题') >= 0:
        full_title = full_title[:full_title.find(u'标题')]
        full_title = full_title.strip()
    year = td[3].text.strip()
    volume = td[4].text.strip()
    season = td[5].text.strip()
    page = td[6].text.strip()
    
#     print title
    
    from_header = [u'来源', u'卷', u'期', u'页', u'出版年']
    from_var = [full_title, volume, season, page, year]
    
    detail = u''
    for header, var in zip(from_header, from_var):
        if var:
            detail += header + ': ' + var + ' '
    print u'标题: ' + paper
    print u'作者: ' + author
    print re.sub(r'\s+', ' ', detail)

    # driver.find_elements_by_name('Select All')[0].click()
    # time.sleep(3)
    for cb in driver.find_elements_by_xpath('//input[@name="isickref" and @type="checkbox"]'):
        cb.click()

    while True:
        try:
            driver.find_elements_by_name('Finish Search')[0].click()
            break
        except:
            time.sleep(1)

    while True:
        try:
            total_cites = int(driver.find_elements_by_class_name('title4')[0].find_element_by_xpath('span').text)
            break
        except:
            time.sleep(1)
    
    print u'该文共被引用%d次' % (total_cites, )

    # # select all page
    # # driver.find_elements_by_class_name('page-options-inner-left')[0].find_element_by_xpath('ul/li/input').click()
    # driver.find_element_by_class_name('SelectPageChk').click()
    # driver.find_element_by_class_name('addToMarkedListButton').click()
    # try:
    #     driver.find_element_by_xpath('//input[@name="add"]').click()
    # except:
    #     pass
    # next = driver.find_element_by_class_name('paginationNext')
    # while next.get_attribute('class').find('paginationNextDisabled') < 0:
    #     next.click()
    # #     driver.find_elements_by_class_name('page-options-inner-left')[0].find_element_by_xpath('ul/li/input').click()
    #     driver.find_element_by_class_name('SelectPageChk').click()
    #     driver.find_element_by_class_name('addToMarkedListButton').click()
    #     try:
    #         driver.find_element_by_xpath('//input[@name="add"]').click()
    #     except:
    #         pass
    #     next = driver.find_element_by_class_name('paginationNext')


    index = 1
    while index <= total_cites:
        while True:
            try:
                record = driver.find_element_by_id('RECORD_' + str(index)).find_element_by_xpath('div[3]');
                break
            except:
                time.sleep(1)

        for i in range(10):
            try:
                record = driver.find_element_by_id('RECORD_' + str(index)).find_element_by_xpath('div[3]');
            except:
                break
            
            while True:
                record = driver.find_element_by_id('RECORD_' + str(index)).find_element_by_xpath('div[3]');
                t = record.find_element_by_xpath('div[1]').text.strip()
                a = record.find_element_by_xpath('div[2]').text.strip()
                j = record.find_element_by_xpath('div[3]').text.strip()
                if not t or not a or not j:
                    time.sleep(1)
                else:
                    break

#             print index
            print u'标题:', t
            print a
            j = j.replace('\n', '')
            j = re.sub(r'\s+', ' ', j);
            print j

            index += 1

        if index <= total_cites:
            driver.find_element_by_class_name('paginationNext').click()

    driver.quit()

# check('Adaptive logging: Optimizing logging and recovery costs in distributed in-memory databases')
# check("Competence-Based Song Recommendation: Matching Songs to One's Singing Skill")

with open('papers.txt') as f:
    for paper in f:
        if not paper.startswith('#'):
            check(paper[:-1])
            print ''

#check('Targeted advertising in public transportation systems with quantitative evaluation')

