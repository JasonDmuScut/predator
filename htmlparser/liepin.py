import bs4

import utils.tools


def catchman(htmlsource):
    bs = bs4.BeautifulSoup(htmlsource)
    up_data = bs.findAll(class_='table-list-peo')
    down_data = bs.findAll(class_='table-list-info')
    results = []
    for index in range(len(up_data)):
        storage_data = {'peo':[], 'info':[]}
        index_bs = up_data[index]
        checkbox = index_bs.find(class_='checkbox')
        storage_data['id'] = checkbox['value']
        storage_data['data-name'] = checkbox['data-name']
        storage_data['data-userid'] = checkbox['data-userid']
        storage_data['recommend'] = \
            index_bs.find(class_='icons16 icons16-recommend') is not None
        storage_data['elite'] = \
            index_bs.find(class_='icons16 icons16-elite') is not None

        mark = index_bs.find(class_='mark')
        storage_data['name'] = mark.text
        storage_data['href'] = mark['href']
        storage_data['title'] = mark['title']
        storage_data['data-id'] = mark['data-id']
        for td in up_data[index].findAll('td'):
            info = utils.tools.replace_tnr(td.text)
            if info:
                storage_data['peo'].append(info)
        for td in down_data[index].findAll('td'):
            if info:
                storage_data['info'].append(td.text)
        results.append(storage_data)
    return results