import netaddr

class Network():
   def __init__(self,ip):
     self.ip = netaddr.IPAddress(ip)

   def to_int(self):
     return int(self.ip)
   def to_hex(self):
     return hex(self.ip)
   def to_bit(self):
     return self.ip.bits()


