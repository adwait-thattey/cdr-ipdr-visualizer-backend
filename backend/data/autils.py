import datetime
import random

from django.db.models import Q

from data.models import Person, CDR, Service, IPDR

import datetime


def generate_random_datetime(start, end):
    """Generate a random datetime between `start` and `end`"""
    return start + datetime.timedelta(
        # Get a random amount of seconds between `start` and `end`
        seconds=random.randint(0, int((end - start).total_seconds())),
    )


now_time = datetime.datetime.now()
past_time = now_time - datetime.timedelta(weeks=10)


def get_single_user_analytics(p):
    other_persons = Person.objects.exclude(id=p.id)
    pmobiles = p.mobile_numbers.all()
    users_obj = []
    for u in other_persons[:50]:
        obj = {}
        obj['id'] = u.id
        obj['name'] = u.name
        mobiles = u.mobile_numbers.all()
        if len(mobiles) <= 0:
            obj['total_duration'] = 0
            obj['total_times'] = 0
            obj['last_called'] = datetime.datetime.now() - datetime.timedelta(days=300, hours=17)
        else:
            existing_cdrs = CDR.objects.filter(Q(from_number=mobiles[0].number) | Q(to_number=mobiles[0].number))
            obj['total_times'] = existing_cdrs.count()
            obj['total_duration'] = len(existing_cdrs) * random.randint(5, 30)
            obj['last_called'] = generate_random_datetime(past_time, now_time)
        users_obj.append(obj)

    services_obj = []
    if len(pmobiles) > 0:
        pmob = pmobiles[0]
        for s in Service.objects.all().order_by('id')[:10]:
            sobj = {}
            sobj['id'] = s.id
            sobj['total_times'] = random.randint(0, 100)
            sobj['total_data'] = random.randint(10, 100) * sobj['total_times']
            sobj['total_duration'] = sobj['total_times'] * random.randint(5, 30)

            services_obj.append(sobj)

    daterange = []
    cur_time = past_time
    while cur_time < now_time:
        daterange.append(cur_time)
        cur_time += datetime.timedelta(days=random.randint(1, 3))

    cdr_data = []
    for d in daterange:
        tottime = random.randint(10, 3000)
        cdr_data.append({str(d): tottime})

    ipdr_data = []
    for d in daterange:
        tottime = random.randint(10, 3000)
        ipdr_data.append({str(d): tottime})

    final_obj = {
        'users': users_obj,
        'services': services_obj,
        'cdr': cdr_data,
        'ipdr': ipdr_data
    }

    print(final_obj)
    return final_obj
