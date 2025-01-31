from socket import AF_INET
from pyroute2.common import AF_MPLS


def get_mpls_routes(context):
    return len(tuple(context
                     .ndb
                     .routes
                     .getmany({'family': AF_MPLS})))


def test_via_ipv4(context):

    ifname = context.new_ifname
    ifaddr = context.new_ipaddr
    router = context.new_ipaddr

    l1 = get_mpls_routes(context)

    i = (context
         .ndb
         .interfaces
         .create(ifname=ifname, kind='dummy', state='up')
         .add_ip('%s/24' % (ifaddr, ))
         .commit())

    rt_spec = {'family': AF_MPLS,
               'oif': i['index'],
               'via': {'family': AF_INET, 'addr': router},
               'newdst': {'label': 0x20}}

    rt = (context
          .ndb
          .routes
          .create(**rt_spec)
          .commit())

    l2 = get_mpls_routes(context)
    assert l2 > l1
    rt.remove().commit()
    l3 = get_mpls_routes(context)
    assert l3 < l2
    assert rt.state == 'invalid'


def test_encap_mpls(context):

    ifname = context.new_ifname
    ifaddr = context.new_ipaddr
    gateway = context.new_ipaddr
    ipnet = str(context.ipnets[1].network)

    (context
     .ndb
     .interfaces
     .create(ifname=ifname, kind='dummy', state='up')
     .add_ip('%s/24' % (ifaddr, ))
     .commit())

    rt_spec = {'dst': '%s/24' % ipnet,
               'gateway': gateway,
               'encap': {'type': 'mpls', 'labels': [20, 30]}}
    (context
     .ndb
     .routes
     .create(**rt_spec)
     .commit())
