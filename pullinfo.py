from pprint import pprint
import pynetbox

nb = pynetbox.api(url='http://10.0.92.150:8000/', token='02c0dc3f1989ddebe6b776198d0e1d25987b73ad')

#subnets = nb.ipam.prefixes.all()
#for subnet in subnets:
#    subnet_name = subnet["prefix"]
#    dhcp_options = subnet["custom_fields"]["dhcp_options"]

#    print ("Subnet", subnet_name, " with options ", dhcp_options)
#    pprint(dict(subnet))


ip_range = nb.ipam.ip_ranges.all()
for rang in ip_range:
    pprint(dict(rang))
