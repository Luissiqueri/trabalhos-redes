from scapy.all import *
from scapy.layers.http import *
import matplotlib.pyplot as plt
from collections import Counter
import plotly
import networkx as nx
import pandas as pd
import scipy as sp
import socket
import requests
from ip2geotools.databases.noncommercial import DbIpCity
from geopy.distance import distance
from shapely.geometry import Point
import geopandas as gpd
from geopandas import GeoDataFrame
import pandas as pds
import ipinfo
import json
from collections import OrderedDict
import os

api_key_ipinfo = "c059178683af37"

def lista_pacotes(file):
    pcap = rdpcap(file)
    p = PacketList(pcap)
    return p

#print(f"arquivo pcap {pcap}")
#print(f"tamanho arquivo{len(pcap)}")
#packet_count = {}
#contagem_pacotes(pcap, packet_count)
#grafico_contagem_pacotes(packet_count)
#print(f"lista de pacotes{p}")
#print(p[0].show())
#print(p.nsummary())
#p.conversations()
#grafico_ocorrencia_ipsrc(p)


def bytes_per_second(packet):
    return len(packet) / packet.time

def extract_src_ip(packet):
    if IP in packet:
        return packet[IP].src
    else:
        return "No IP"

def extract_dst_ip(packet):
    if IP in packet:
      return packet[IP].dst
    else:
      return "No IP"

def extract_ttl(packet):
  if IP in packet:
    return packet[IP].ttl
  else:
    return 255

async def communication_graph(p):
    handler = ipinfo.getHandlerAsync(api_key_ipinfo)
    graph = {}

    for packet in p:
        ipSrc = extract_src_ip(packet)
        ipDst = extract_dst_ip(packet)

        if ipSrc not in graph:
            graph[ipSrc] = {}
        if ipDst not in graph[ipSrc]:
            graph[ipSrc][ipDst] = {}
            graph[ipSrc][ipDst]['times'] = 0
            graph[ipSrc][ipDst]['minTTL'] = 255
        if graph[ipSrc][ipDst]['times'] <= 20:
            graph[ipSrc][ipDst]['times'] += 1
        ttl = int(extract_ttl(packet))
        if (ipDst.startswith("192.168") and ttl < graph[ipSrc][ipDst]['minTTL']):
            graph[ipSrc][ipDst]['minTTL'] = ttl

    graph
    G = nx.Graph()
    edgeWidth = []
    publicIpsTTL = {}

    for key in graph:
        for dst in graph[key]:
            if dst != "No IP" and key != "No IP":
                G.add_edge(key, dst)
                edgeWidth.insert(len(edgeWidth), (graph[key][dst]['times']))

                #capturando pacotes vindos de ips publicos em direcao à rede local
                #to ignorando outras mascaras para redes locais, eu sei
                if dst.startswith("192.168") and not key.startswith("192.168"):
                    publicIpsTTL[key] = {}
                    publicIpsTTL[key]['ttl'] = graph[key][dst]['minTTL']
                    # print(f"localizando {key}")
                    details = await handler.getDetails(key)
                    publicIpsTTL[key]['lat'] = details.latitude
                    publicIpsTTL[key]['lng'] = details.longitude
                    publicIpsTTL[key]['location'] = f"{details.city}, {details.country}"

    publicIpsOrderedByTTL = dict(sorted(publicIpsTTL.items(), key=lambda x: x[1]['ttl'], reverse=True))

    '''print("Hosts ordenados do mais próximo para o mais longe (baseado no TTL):\n")

    for publicIp in publicIpsOrderedByTTL:
        print(f"{publicIp} TTL = {publicIpsTTL[publicIp]['ttl']}")
        print(f"({publicIpsTTL[publicIp]['lat']}, {publicIpsTTL[publicIp]['lng']}) - {publicIpsTTL[publicIp]['location']}")

    print("Gráfico mostrando visualmente o fluxo de dados. Largura da aresta = quantidade de vezes que ocorreu")'''

    plt.figure(figsize=(30, 20))
    pos = nx.kamada_kawai_layout(G)

    nx.draw_networkx_edges(G, pos, alpha=0.7, width=edgeWidth, edge_color="#fa6464")
    nx.draw_networkx_nodes(G, pos, node_size=14, node_color="#210070", alpha=0.9)
    label_options = {"ec": "k", "fc": "white", "alpha": 1}
    nx.draw_networkx_labels(G, pos, font_size=15, bbox=label_options)

    ax = plt.gca()
    ax.margins(0, 0)
    plt.axis("off")
    # print("é aqui?")
    plt.savefig('graphs/fluxGraph.svg', format='svg')
    # print("sepah")
    
    #plt.show()
    return publicIpsOrderedByTTL

def grafico_mapa(publicIpsOrderedByTTL):
    longitude = []
    latitude = []
    for publicIp in publicIpsOrderedByTTL:
        longitude.append(publicIpsOrderedByTTL[publicIp]['lng'])
        latitude.append(publicIpsOrderedByTTL[publicIp]['lat'])

    rep = [0]*len(latitude)
    for publicIp in publicIpsOrderedByTTL:
        lat = publicIpsOrderedByTTL[publicIp]['lat']
        lng = publicIpsOrderedByTTL[publicIp]['lng']
        for i in range(len(latitude)):
            if (lat == latitude[i] and lng == longitude[i]):
                rep[i]+=1
    data = {'Longitude': longitude, 'Latitude': latitude, 'Repeticoes': rep}
    df = pd.DataFrame(data)
    geometry = [Point(xy) for xy in zip(df['Longitude'], df['Latitude'])]
    gdf = GeoDataFrame(df, geometry=geometry)
    
    shapedFilePath = "./world/ne_110m_admin_0_countries.shp"
    world = gpd.read_file(shapedFilePath)
    
    ax = world.plot(figsize=(10, 6))
    gdf.plot(ax=ax, marker='o', color='red', markersize=df['Repeticoes']*5);
    ax.get_figure().savefig('graphs/locationsGraph.svg')



def contagem_pacotes(pcap, packet_count):
    for packet in pcap:
        if packet.haslayer(Ether):
            ether_type = packet[Ether].type
            if ether_type not in packet_count:
                packet_count[ether_type] = 0
            packet_count[ether_type] += 1

    # print(f"contagem de pacotes{packet_count}")

def grafico_contagem_pacotes(packet_count):
    x_values = [str(hex(ether_type)) for ether_type in packet_count.keys()]
    y_values = list(packet_count.values())

    # Criar o gráfico de barras usando Matplotlib
    plt.bar(x_values, y_values, color='blue')

    # Configurações do gráfico
    plt.xlabel('Tipo de Ethernet')
    plt.ylabel('Contagem de Pacotes')
    plt.title('Contagem de Pacotes por Tipo de Ethernet')
    plt.xticks(rotation=45)

    # Mostrar o gráfico
    plt.tight_layout()
    plt.show()

def grafico_ocorrencia_ipsrc(p):
    srcIP=[]
    for pkt in p:
        if IP in pkt:
            try:
                srcIP.append(pkt[IP].src)
            except:
                pass

    cnt = Counter()

    for ip in srcIP:
        cnt[ip] += 1
    #cnt
    
    xData=[]
    yData=[]

    for ip, count in cnt.most_common():
        xData.append(ip)
        yData.append(count)


    #plotly.offline.plot({"data":[  plotly.graph_objs.Bar( x=xData, y=yData) ]})

    plotly.offline.plot({"data":[plotly.graph_objs.Bar(x=xData, y=yData)],
    "layout":plotly.graph_objs.Layout(title="Source IP Occurrence",
    xaxis=dict(title="Src IP"), yaxis=dict(title="Count"))})

#precisamos ve se isto esta funcionando
#AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
def getCompanyByMACAdress(macAdress):
    try:
        req = requests.get(f"http://www.macvendorlookup.com/api/v2/{macAdress}")
        return req.json()[0]['company']
    except Exception as e:
        return "&lt;desconhecido&gt;"

def getSrcIP(packet):
    if ARP in packet:
        return packet[ARP].psrc
    else:
        return "No IP"
    
def getDstIP(packet):
    if ARP in packet:
        return packet[ARP].pdst
    else:
        return "No IP"

def getSrcMAC(packet):
    if ARP in packet:
        return packet[ARP].hwsrc
    else:
        return "No MAC"
 
def getDstMAC(packet):
    if ARP in packet:
        return packet[ARP].hwdst
    else:
        return "No MAC"


def getARPInfo(p):

    SrcIP = []
    DstIP = []
    SrcMAC = []
    DstMAC = []
    company = []

    for packet in p:
        #print(getDstIP(packet))
        #print(getDstMAC(packet))
        SrcIP.append(getSrcIP(packet))
        DstIP.append(getDstIP(packet))
        SrcMAC.append(getSrcMAC(packet))
        DstMAC.append(getDstMAC(packet))

    IPs = SrcIP + DstIP
    MACs = SrcMAC + DstMAC
    
    '''print(IPs[502])
    print(IPs[503])
    print(MACs[502])
    print(MACs[503])'''
    

    df = pd.DataFrame((zip(IPs,MACs)), columns = ["IPs", "MACs"])
    df.drop_duplicates("IPs", inplace = True)
    for m in df["MACs"]:
        company.append(getCompanyByMACAdress(m))
    df.insert(2, "Company", company)
    
    # print(df)

    tabela = df.to_dict()
    return tabela
    
    # json_object = json.dumps(tabela, indent = 4) 
    # print(json_object)
    #return json_object


# FUNÇÕES PARA O T3 RIP
def handleRIP(p):
    intervals = time(p)
    table = []

    for index, value in enumerate(p):
        # print("\n")
        # print(f'Intervalos de tempo entre atualizações RIP (em segundos): {intervals[index - 1]}s')
        table.append({"src": value.getlayer(IP).src, "dst": value.getlayer(IP).dst, "time": float(intervals[index - 1]), "table": []})
        parse_rip_entries_in_packet(table[index], value)

    return table

def time(rip):
    rip_packets = [r for r in rip if RIP in r]
    
    # Extrair horários dos pacotes RIP
    timestamps = [pkt.time for pkt in rip_packets]
    
    # Caclular intervalos entre pacotes sucessivos 
    intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]

    # Converter para segundos
    intervalsInSeconds = [interval for interval in intervals]

    temp = []

    #Exibir intervalos de tempo e o número de pacotes RIP
    # print(f'Número de pacotes RIP: {len(rip_packets)}')
    # print("Intervalos de tempo entre atualizações RIP (em segundos): ")
    # for interval in intervalsInSeconds:
    #   print(interval)
    for interval in intervalsInSeconds:
        temp.append(interval)
    
    return temp

# ACHAR ONDE COLOR O rip.command == 2

def parse_rip_entries_in_packet(dict, p):
    src_ip = p.getlayer(IP).src
    
    rip_entry = p.getlayer(RIPEntry)
    # thisdict.update({"color": "red"})
    # print(f"IP SRC: {src_ip}")

    # dict.update({"time": time})
    while rip_entry:
        # see https://scapy.readthedocs.io/en/latest/api/scapy.layers.rip.html
        # for extracting RIP entry fields
        ip_addr = rip_entry.addr
        netmask = rip_entry.mask
        next_hop = rip_entry.nextHop
        metric = rip_entry.metric
        dict["table"].append({
            "IP": ip_addr,
            "mask": netmask,
            "next": next_hop,
            "metric": metric,
        })      
        # dict[src_ip].append({
        #     "time": time,
        #     "IP": ip_addr,
        #     "mask": netmask,
        #     "next": next_hop,
        #     "metric": metric,
        # })
        # print(f"IP:{ip_addr} {netmask} | next hop: {next_hop} | metric: {metric}")
        
        # move to next RIP entry
        rip_entry = rip_entry.getlayer(RIPEntry, 2)


#FUNCÕES PARA O T4 PROTOCOLO UDP
def handleUDP(p):
    udp_packets = [u for u in p if UDP in u]
    for packet in udp_packets:
        service_sport = get_service_by_port(packet.sport, "udp")
        service_dport = get_service_by_port(packet.dport, "udp")
        packet.conversations()
        # if service:
        #print(f"Source port: {packet.sport} --- Service: {service_sport} ==> Destination port: {packet.sport} --- Service: {service_dport}")
            
        # print(packet.payload)
    # print(len(udp_packets))
    # for i in range(len(udp_packets)):
        # print(udp_packets[i])

def get_service_by_port(port, protocol):
    try:
        service = socket.getservbyport(port, protocol)
        return service
    except:
        return None


#FUNÇÕES PARA T5 PROTOCOLO TCP
def handleTCP(p):
    tcp_packets = [t for t in p if TCP in t]
    
    data = {} 

    for tcp in tcp_packets:
        src_ip = tcp[IP].src
        dst_ip = tcp[IP].dst
        src_port = tcp[TCP].sport
        dst_port = tcp[TCP].dport

        ts = tcp.seq
        if 'A' in tcp[TCP].flags:
            tsack = tcp[TCP].ack
            rtt = tsack - ts
        else:
            tsack = None
            rtt = None

        if 'R' in tcp[TCP].flags:
            retransmission = 1
        else:
            retransmission = 0

        #w_size = tcp[TCP].window_size
            
        id_occurrencies = (src_ip, dst_ip)

        if id_occurrencies not in data:
            data[id_occurrencies] = {
                'src_ip': src_ip,
                'dst_ip':dst_ip,
                'total_bytes':0,
                'src_port':[],
                'dst_port':[],
                'packets': 0,
                'bytes':[],
                'n_sequence':[],
                'w_size': [],
                'retransmission':[],
                'RTT':[]
            }
            
            data[id_occurrencies]['src_port'].append(src_port)
            data[id_occurrencies]['dst_port'].append(dst_port)
            data[id_occurrencies]['total_bytes'] += len(tcp)
            data[id_occurrencies]['packets'] += 1
            data[id_occurrencies]['bytes'].append(len(tcp))
            data[id_occurrencies]['n_sequence'].append(ts)
            #data[id_occurrencies]['w_size'].append(w_size)
            data[id_occurrencies]['retransmission'].append(retransmission)
            data[id_occurrencies]['RTT'].append(rtt)
    
    for connection, info in data.items():
        src_ip, dst_ip = connection
        print(f"Connection: {src_ip} -> {dst_ip}")
        print(f"  Source IP: {info['src_ip']}")
        print(f"  Destination IP: {info['dst_ip']}")
        print(f"  Source Ports: {info['src_port']}")
        print(f"  Destination Ports: {info['dst_port']}")
        print(f"  Total Packets: {info['packets']}")
        #total_bytes = sum(info['bytes'])
        print(f"  Total Bytes Transferred: {info['total_bytes']} bytes")
        print(f"  Sequence Number: {info['n_sequence']}")
        print(f"  Retransmission: {info['retransmission']}")
        print(f"  RTT: {info['RTT']} microssegundos")


def handleHTTP(p):
    http_packets = [h for h in p if HTTPRequest in h or HTTPResponse in h]

    for http in http_packets:
        if HTTPRequest in http:
            print("=>REQUEST")
            method = http[HTTPRequest].Method.decode()  # Decodificar para string
            path = http[HTTPRequest].Path.decode()      # Decodificar para string
            host = http[HTTPRequest].Host.decode() if b'Host' in http[HTTPRequest].fields else ''  # Decodificar para string se disponível
            # Construir a URL completa
            url = f"http:/{host}{path}"
            
            headers = http[HTTPRequest].fields          # Obter todos os campos do HTTPRequest
            print(f"Método: {method}")
            print(f"URL: {url}")
            print(f"Cabeçalhos: {headers}")
    
        if HTTPResponse in http:
            print("=>RESPONSE")
            status_code = http[HTTPResponse].Status_Code.decode()  # Decodificar para string
            reason_phrase = http[HTTPResponse].Reason_Phrase.decode()  # Decodificar para string
            headers = http[HTTPResponse].fields                     # Obter todos os campos do HTTPResponse
            print(f"Código de Status: {status_code}")
            print(f"Motivo: {reason_phrase}")
            print(f"Cabeçalhos: {headers}")
            
        print()

def save_content(content, filename):
    with open(filename, "wb") as f:
        f.write(content)

def HTTPcontent(p):
    
    http_packets = [h for h in p if HTTPRequest in h or HTTPResponse in h]
    output_dir = "output/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for i, http in enumerate(http_packets):
        
        if HTTPResponse in http:    
            response = http[HTTPResponse]

            if 'Content_Type' in response.fields:
                content_type = response.fields['Content_Type'].decode()

            #Verificar se o conteúdo é HTML
                if 'text/html' in content_type:
                    # print("aqui")
                    body = response.payload.load
                    filename = f"{output_dir}page_{i}.html"
                    save_content(body, filename)
                    print(f"HTML salvo em: {filename}")
            # Verificar se o conteúdo é uma imagem
                elif 'image' in content_type:
                    body = response.payload.load
                    ext = content_type.split('/')[1]  # Extensão da imagem (ex: png, jpeg)
                    filename = f"{output_dir}image_{i}.{ext}"
                    save_content(body, filename)
                    print(f"Imagem salva em: {filename}")
            

def handleDNS(p):

    c = 0
    occurrencies = 0
    ips = []
    data = {}
    domains_data = {}
    response_pairs = defaultdict(list)

    DNSpackets = [d for d in p if DNS in d]

    for dns in DNSpackets:
        if dns.qr == 0:  # qr == 0 consulta DNS
           response_pairs[dns.id].append(dns)
           
        elif dns.qr == 1:  # qr == 1 resposta DNS
            occurrencies += 1
            ips.append(dns[IP].dst)
            ips.append(dns[IP].src)

            data[occurrencies] = {
            'src_ip': dns[IP].dst,
            'dst_ip':dns[IP].src,
            'response_time': 0,
            'domains': [],
            'types': [],
            'domains_ips':[]
            }
            
            response_pairs[dns.id].append(dns)

            for i in range(dns.ancount):
                response = dns.an[i]
                data[occurrencies]["domains"].append(response.rrname.decode('utf-8'))
                data[occurrencies]["types"].append(response.type)
                data[occurrencies]["domains_ips"].append(response.rdata)

            occurrencies += 1

    #print(list(set(ips)))
    DDoS(data)

def DDoS(data):
    """
    sleep_interval = 15

    # Set threshold for number of connections
    connection_threshold = 1000

    # Initialize list to store previous number of connections
    previous_connections = []

    total_packets = len(data)
    unique_ip_count = len(set(entry['src_ip'] for entry in data.values()))
    for entry in data.values():
        #print(entry['dst_ip'])
        #print(entry['src_ip'])
        print(entry['domains_ips'])
    print(list(set(entry['src_ip'] for entry in data.values())))
    print(unique_ip_count)

    
    if total_packets > connection_threshold:
        print(f"Possible DDoS Attack detected! High volume of DNS packets: {total_packets}")
    
    if unique_ip_count > 50:  
        print(f"Possible DDoS Attack detected! High number of unique source IPs: {unique_ip_count}")

    print(f"Total DNS packets: {total_packets}, Unique source IPs: {unique_ip_count}")

    # Identificação e bloqueio do atacante
   if block_attacker:
        potential_attackers = [entry['src_ip'] for entry in data.values()]
        for attacker in potential_attackers:
            os.system(f'netsh advfirewall firewall add rule name="Block IP" dir=in action=block remoteip={attacker}')"""