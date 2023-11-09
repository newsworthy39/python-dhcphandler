from pprint import pprint
import pynetbox
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys, getopt
from request import Request as Request
from ranges import v1_ranges as v1_ranges
from reservations import v1_reservations as v1_reservations


# Class MyHTTPServer
class MyServer(BaseHTTPRequestHandler):
    tenant_id = 0 
    nb = 0
    prefix = 0

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)

        # create object
        req = Request(nb = self.nb,
                   tenant_id = self.tenant_id,
                   prefix = self.prefix)

        #   print(post_body)
        reservations = "/api/v1/tenant/{}/reservations".format(self.tenant_id)
        if self.path.lower() == reservations:
            v1_reservations(req)

        #   print(post_body)
        reservations = "/api/v1/tenant/{}/interfaces".format(self.tenant_id)
        if self.path.lower() == reservations:
            v1_reservations(req)

        #   print(post_body)
        ranges = "/api/v1/tenant/{}/ranges".format(self.tenant_id)
        if self.path.lower() == ranges:
            v1_ranges(req)


        # send response
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

# Main
def main(argv):

    # bind-defaults, thx
    serverport = 8080
    hostname = "0.0.0.0"
    
    # optional arguments
    prefix = "10.10.10.10/32"
    target = "http://netbox.portfolio.cloud"
    tenant = 0

    # opts.
    opts, args = getopt.getopt(argv,"ht:b:p:d:",["tenant=","bind=","prefix=","destination="])
    for opt, arg in opts:
      if opt == '-h':
         print ('test.py -t <tenantid> -b <bind> -p <prefix> -d <destination>')
         sys.exit()
      elif opt in ("-t", "--tenant"):
         tenant = arg
      elif opt in ("-b", "--bind"):
         hostname, serverport = arg.split(":")
      elif opt in ("-p", "--prefix"):
         prefix = arg
      elif opt in ("-d", "--destination"):
         target = arg

    # set class defaults
    import config
    MyServer.prefix = prefix
    MyServer.nb = pynetbox.api(url=config.target, token=config.token)

    # translate the UUID to the local ID from SSOT.
    nbtenant = MyServer.nb.tenancy.tenants.get(uuid=tenant)
    MyServer.tenant_id = nbtenant.id

    print("Listening {}:{} use API-endpoint:{} TenantUUID: {} tenantID: {} Prefix: {}".format(hostname, serverport, target, tenant, MyServer.tenant_id, prefix))

    server_address = (hostname, int(serverport))
    httpd = HTTPServer(server_address, MyServer)
    httpd.serve_forever()


if __name__ == "__main__":
    main(sys.argv[1:])
