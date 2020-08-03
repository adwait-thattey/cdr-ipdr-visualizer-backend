from analytics.views import get_community_and_importance, get_n_similar_numbers, get_possible_spammers
from data.models import CDR
import parth_data
arr = list(CDR.objects.values_list('from_number', 'to_number', 'duration', 'call_type'))
d = [{'from_number':i[0], 'to_number':i[1], 'duration':i[2], 'call_type':i[3]} for i in arr]
# print(d)
# print(parth_data.data)
# obj = get_community_and_importance(d)
# obj = get_n_similar_numbers(d, 3)
obj = get_possible_spammers(d) # also send call_type in data array
print(obj)