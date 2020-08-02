from analytics.views import get_community_and_importance
from data.models import CDR
import parth_data
# arr = list(CDR.objects.values_list('from_number', 'to_number', 'duration'))
# d = [{'from_number':i[0], 'to_number':i[0], 'duration':i[2]} for i in arr]
print(parth_data.data)
obj = get_community_and_importance(parth_data.data)

# print(obj)