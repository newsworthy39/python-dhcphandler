from pprint import pprint
import pynetbox
import sys, getopt
from request import Request as Request

# v1_reservations_notify
def v1_reservations(req):

    # clear the file, hmm. danger.
    filename = "./reservations/reservations.conf";
    with open(filename, "wb") as file:
            file.truncate(0)

    # tenants
    vms = req.nb.virtualization.virtual_machines.filter(tenant_id=req.tenant_id, has_primary_ip=True)

    for vm in vms:
        address = req.nb.ipam.ip_addresses.get(vm.primary_ip4.id)
        # host vif-567836 {
        #     fixed-address 192.0.2.7;
        #     hardware ethernet 52:59:33:D1:FC:09;
        #     option host-name "i-434238";
        # }
        # only write good ones.
        if None is not address.assigned_object_type and  "virtualization" in address.assigned_object_type :

            client_ip = address.address.split("/")[0]
            client_vif = address.assigned_object.name
            client_hostname = address.dns_name.split(".")[0]
            client_mac = "52:52:52:52:52:52"
            client_dns = [ "10.0.92.38" ]
            client_router = "192.168.57.1"

            # Find vif mac
            macs = req.nb.virtualization.interfaces.filter(name=address.assigned_object.name)
            for mac in macs:
              # print("mac", mac.mac_address)
                client_mac = mac.mac_address
            
            # write it out
            with open ("./reservations/reservations.conf", 'a') as f:
                f.write("host {} {{\n\tfixed-address {};\n\thardware ethernet {};\n\toption host-name \"{}\";\n\toption domain-name-servers {};\n\toption routers {};\n}}\n".format(
                    client_vif,
                    client_ip,
                    client_mac,
                    client_hostname,
                    ",".join(client_dns),
                    client_router
                ))

            # finally let reload know
            with open ("./reservations/.reload", 'a') as f:
                f.write("changed")


# Main
def main(argv):

    # necessary arguments
    prefix = "10.10.10.10/32"
    target = "http://netbox.portfolio.cloud"
    tenant = 0

    # opts.
    opts, args = getopt.getopt(argv,"ht:p:d:",["tenant=","prefix=","destination="])
    for opt, arg in opts:
      if opt == '-h':
         print ('test.py -t <tenantid> -p <prefix> -d <destination> ')
         sys.exit()
      elif opt in ("-t", "--tenant"):
         tenant = arg
      elif opt in ("-p", "--prefix"):
         prefix = arg
      elif opt in ("-r", "--destination"):
         target = arg

    # translate the UUID to the local ID from SSOT.
    import config
    nbpy = pynetbox.api(url=config.target,token=config.token)
    nbtenant = nbpy.tenancy.tenants.get(uuid=tenant).id

    print("use API-endpoint:{} TenantUUID: {} tenantID: {} Prefix: {}".format(target, tenant, nbtenant, prefix))

    # create object
    req = Request(nb = nbpy,prefix = prefix,tenant_id = nbtenant)

    # reservations
    v1_reservations(req)

if __name__ == "__main__":
    main(sys.argv[1:])
