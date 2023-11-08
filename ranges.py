from pprint import pprint
import pynetbox
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys, getopt, ipaddress
from request import Request as Request

def v1_ranges(req):
    # clear the file, hmm. danger.
    filename = "./reservations/ranges.conf";
    with open(filename, "wb") as file:
            file.truncate(0)

    ranges = req.nb.ipam.ip_ranges.filter(tenant_id=req.tenant_id,role_id=req.nb.ipam.roles.get(name="DHCP").id)
    for rng in ranges:
        if ipaddress.IPv4Network(rng.start_address, False) == ipaddress.IPv4Network(req.prefix):
            # only write good ones.
            with open ("./reservations/ranges.conf", 'a') as f:
                f.write("subnet {} netmask {} {{\n\tdeny-unknown-clients;\n\tpool {{\n\t\t range {} {};\n\t\t}}\n\t}}\t\n".format(
                    ipaddress.IPv4Network(req.prefix)[0],
                    ipaddress.IPv4Network(req.prefix).netmask,
                    rng.start_address.split("/")[0],
                    rng.end_address.split("/")[0],
            ))

#       # finally let reload know
        with open ("./reservations/.reload", 'a') as f:
            f.write("changed")

# Main
def main(argv):

    # bind-defaults, thx
    serverport = 8081
    hostname = "10.0.92.149"
    
    # optional arguments
    prefix = "10.10.10.10/32"
    target = "http://netbox.portfolio.cloud"
    tenant = 0

    # opts.
    opts, args = getopt.getopt(argv,"ht:p:d:",["tenant=","bind=","prefix=","destination="])
    for opt, arg in opts:
      if opt == '-h':
         print ('test.py -t <tenantid> -b <bind> -p <prefix> -d <destination>')
         sys.exit()
      elif opt in ("-t", "--tenant"):
         tenant = arg
      elif opt in ("-p", "--prefix"):
         prefix = arg
      elif opt in ("-d", "--destination"):
         target = arg

    # translate the UUID to the local ID from SSOT.
    nbpy = pynetbox.api(url=target,token='98e073778ad41232f12d2b4dd7dd0d445f173f59')
    nbtenant = nbpy.tenancy.tenants.get(uuid=tenant).id

    print("use API-endpoint:{} TenantUUID: {} tenantID: {} Prefix: {}".format(target, tenant, nbtenant, prefix))

    # create object
    req = Request(nb = nbpy,
                   prefix = prefix,
                   tenant_id = nbtenant)
    
    v1_ranges(req)


if __name__ == "__main__":
    main(sys.argv[1:])
