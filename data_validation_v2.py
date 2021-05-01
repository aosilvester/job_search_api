import json
import io


# grab all json and merge into one list
all_postings = []
def combine_json():
    jobsite_json_lists = [
        io.open('json_files\\indeed_scraped_postings.json', 'r', encoding="utf-8"),
        io.open('json_files\\glassdoor_scraped_postings.json', 'r', encoding="utf-8"),
        io.open('json_files\\monster_scraped_postings.json', 'r', encoding="utf-8"),
    ]

    for jobsite in jobsite_json_lists:
        job_postings = json.loads(jobsite.read())
        for posting in job_postings:
            all_postings.append(posting)



def validate(all_postings):
    flagged_duplicates = []
    reviewed_items = []
    first_run_uniques = []
    seen = []
    truly_unique = []
    validated_list = []
    for posting in all_postings:
        posting = ensure_key_and_value(posting)
        posting['first_run_unique'] = 'False'
        reviewed_item = {
            'company': posting['company'],
            'job_title': posting['job_title'],
            'salary': posting['salary'],
        }
        if reviewed_item in seen:
            flagged_duplicates.append(posting)
            reviewed_items.append(reviewed_item)
        else:
            seen.append(reviewed_item)
            posting['first_run_unique'] = 'True'
            first_run_uniques.append(posting)
    for posting in first_run_uniques:
        reviewed_item = {
            'company': posting['company'],
            'job_title': posting['job_title'],
            'salary': posting['salary'],
        }
        if reviewed_item in reviewed_items:
            flagged_duplicates.append(posting)
        else:
            posting['duplicate_check'] = 'unique'
            truly_unique.append(posting)

    for posting in flagged_duplicates:
        posting['duplicate_check'] = 'duplicate'

    for item in truly_unique:
        validated_list.append(item)
    for item in flagged_duplicates:
        validated_list.append(item)
    print(f'Total Job Postings: {len(validated_list)}. Truly Unique: {len(truly_unique)}. Flagged as Duplicate: {len(flagged_duplicates)}')
    return validated_list

def ensure_key_and_value(job):
    # confirms if job has required parameters for data validation. 
    # includes keys and a value of 'None' if not
    required_parameters = [
        'company',
        'job_title',
        'salary',
    ]
    for param in required_parameters:
        job_check = str(job)
        if param not in job_check:
            job[param] = 'None'
        if not job.get(param):
            job[param] = 'None'
    # print(job)

    company = False
    job_title = False
    salary = False
    try:
        for key, value in job.items():
            if job[key] is None:
                job[key] = 'None'
            # print(key, value, len(value))

    except:
        print(job)

    return job



def write_to_json(validated_list):
    initial_posting = True
    # print(len(validated_list))
    for posting in validated_list:
    #     print(json.dumps(posting))
        # print(item['duplicate_check'])
        # print(str(posting))
        if initial_posting:
            write_scraped_file = open('validated_postings.json', 'w')
            write_scraped_file.write('[')
            write_scraped_file.write(str(json.dumps(posting)))
            write_scraped_file.write(']')
            initial_posting = False
            write_scraped_file.close()
        else:
            read_scraped_file = open('validated_postings.json', 'r')
            existing_postings = json.loads(read_scraped_file.read())
            existing_postings.append(posting)
            read_scraped_file.close()
            write_scraped_file = open('validated_postings.json', 'w')
            write_scraped_file.write(str(json.dumps(existing_postings)))
            write_scraped_file.close()




combine_json()
validated_list = validate(all_postings)
write_to_json(validated_list)