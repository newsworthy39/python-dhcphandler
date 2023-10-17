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
    target = "http://10.0.92.150:8000"
    tenant = 0

    # opts.
    opts, args = getopt.getopt(argv,"ht:b:c:d",["tenant=","bind=","prefix=","destination="])
    for opt, arg in opts:
      if opt == '-h':
         print ('test.py -t <tenantid> -b <bind> -p <prefix> -d <destination>')
         sys.exit()
      elif opt in ("-t", "--tenant"):
         tenant = int(arg)
      elif opt in ("-b", "--bind"):
         hostname = arg
      elif opt in ("-p", "--prefix"):
         prefix = arg
      elif opt in ("-r", "--destination"):
         target = arg

    # create object
    req = Request(nb = pynetbox.api(url=target,
                    token='02c0dc3f1989ddebe6b776198d0e1d25987b73ad'),
                   tenantid = tenant,
                   prefix = prefix,
                   tenant = tenant)
    
    v1_ranges(req)


if __name__ == "__main__":
    main(sys.argv[1:])
