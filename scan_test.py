import nmap

scanner = nmap.PortScanner()

print("nmap version: ", scanner.nmap_version())
scanner.scan('3.216.134.138', '1-8000', '-vv')

print(scanner.scaninfo())

print("IP Status: ", scanner['3.216.134.138'].state())

lport = list(scanner['3.216.134.138']['tcp'].keys())
lport.sort()

for port in lport:
    print("Port %s is %s" %(port, scanner['3.216.134.138']['tcp'][port]['state']))
