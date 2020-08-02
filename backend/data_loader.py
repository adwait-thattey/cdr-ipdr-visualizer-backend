import pickle
from data.models import CDR, IPDR
import datetime
from dateutil.parser import parse

f = open("./media/final_data.pickle", mode="rb")
data = pickle.load(f)
f.close()

for d in data:
    try:
        d['to_number'] = str(int(d['to_number']))
    except:
        pass

x = 0
for d in data:
    CDR.objects.create(**d)
    x += 1
    print(x)

# f = open("./media/ipdr_final_data.pickle", mode="rb")
# ipdata = pickle.load(f)
# f.close()
#
# for d in ipdata:
#     d1 = parse(d['date'])
#     d2 = parse(d['time'])
#     dc = datetime.datetime.combine(d1.date(), d2.time())
#     d['timestamp'] = dc
#     del d['date'], d['time']
#
#
# print("date parsing done")
# x = 0
# for d in ipdata:
#     IPDR.objects.create(
#         start_time= d.get('timestamp'),
#         duration = d.get('duration'),
#
#         private_ip = d.get('private ip'),
#         private_port = d.get('private port'),
#         public_ip = d.get('public ip'),
#         public_port = d.get('public port'),
#         destination_ip = d.get('destination ip'),
#         destination_port = d.get('destination port'),
#
#         from_number = d.get('from_number'),
#         imei = d.get('imei'),
#         imsi = d.get('imsi'),
#         cell_id = d.get('cell_id'),
#
#         location_lat = d.get('location_lat'),
#         location_long = d.get('location_long'),
#
#         upload_data_volume = d.get('upload data volume'),
#         download_data_volume = d.get('download data volume'),
#     )
#     x+=1
#     print(x)
