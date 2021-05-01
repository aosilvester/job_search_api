import json

# print('hello world')
# test = open('test.json','r')
# json = json.loads(test.read())
indeed = open('indeed_scraped_postings.json', 'r')
json = json.loads(indeed.read())

# print('Ideal length of JSON is 5. Initial length of JSON = ', len(json))

# for item in json:
#     print(item)


def remove_duplicates(jobs):
    # first_round_unique = []
    # first_round_duplicate = []
    
    # indexes = []
    seen = []
    potential_duplicates = []
    x_duplicate = []
    first_run_uniques = []
    truly_unique = []
    validated_list = []
    for x in jobs:


        # ensure that each job dict has the required keys and relevant values for validation
        x = ensure_key_and_value(x)

        print(x)

        # Create dict of just company name, title, and salary.
        # seen_item = {
        #     'company': x['company'],
        #     'job_title': x['job_title'],
        #     'salary': x['salary'],
        # }
        seen_item={}
        # except:
        #     print('exception')
        #     # if not x.get('company')
        #     # seen_item = {
        #     #     'comapny': x.get('company'),
        #     #     'job_title':x.get('job_title')
        #     # }

        # if the item created already exists in seen_items (a duplicate), add to list of potential duplicates
        if seen_item in seen:
            # print('duplicate')
            potential_duplicates.append(x)
            x_duplicate.append(seen_item)
        else:
            seen.append(seen_item)
            first_run_uniques.append(x)
    
    # reiterate first_run_uniques over x_duplicate list, as first run uniques are inherently unique. 
    for x in first_run_uniques:
        seen_item = {
            'company': x['company'],
            'job_title': x['job_title'],
            'salary': x['salary'],
        }
        if seen_item in x_duplicate:
            # print('second check duplicate')
            potential_duplicates.append(x)
        else:
            # print('truly unique')
            x['duplicate_check'] = 'unique'
            truly_unique.append(x)
    # print(potential_duplicates)

    for item in potential_duplicates:
        item['duplicate_check'] = 'duplicate'


    for item in truly_unique:
        validated_list.append(item)
    for item in potential_duplicates:
        validated_list.append(item)
    

    print('Initial Length of postings: ', len(json))

    print('Final Length of unique postings', len(truly_unique))

    # print('***Final Check***')
    # for item in validated_list:
        # print(item['duplicate_check'])

    # print(jobs)
        

def ensure_key_and_value(job):
    required_parameters = [
        'company',
        'job_title',
        'salary',
    ]
    print(job['job_title'])
    for param in required_parameters:
        job_check = str(job)
        if param not in job_check:
            job[param] = 'None'
    return job


























remove_duplicates(json)
