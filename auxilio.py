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
# from ip2geotools.databases.noncommercial import DbIpCity
from geopy.distance import distance
from shapely.geometry import Point
import geopandas as gpd
from geopandas import GeoDataFrame
import pandas as pds
import ipinfo
import json
from collections import OrderedDict
import os
import io
import base64


api_key_ipinfo = "c059178683af37"

def lista_pacotes(file):
    file_in_memory = io.BytesIO(file)
    pcap = rdpcap(file_in_memory)
    p = PacketList(pcap)
    return p

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
    publicIpsTTL = {}

    for key in graph:
        for dst in graph[key]:
            if dst != "No IP" and key != "No IP":

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
    # return publicIpsOrderedByTTL

    result = {
        'graph': graph,
        'ipsInfo': publicIpsOrderedByTTL
    }

    return result

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
    return df.to_dict(orient="records")

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

def getCompanyByMACAdress(macAdress):
    csvFile = "./oui.csv"

    data = pd.read_csv(csvFile)
    prefixoMac = macAdress.replace(":", "")[:6].upper()
    resultado = data[data["Assignment"].str.contains(prefixoMac, na=False)]
    if resultado.empty:
        return "UNDEFINED"
    name = resultado['Organization Name'].values[0]
    return name

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

    print(len(intervals))
    rip_packets = [r for r in p if RIP in r]

    for index, value in enumerate(rip_packets):
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
    intervals = []
    if len(timestamps) > 1:
        intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
    else:
        intervals = [0]

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
    data = {}

    for packet in udp_packets:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        id_occurrencies = (src_ip, dst_ip)

        if id_occurrencies not in data:
            data[id_occurrencies] = {
                'src_ip': src_ip,
                'dst_ip':dst_ip,
                'packets': 0,
                'src_port':[],
                'dst_port':[],
                'service_src':[],
                'service_dst':[]
            }

        data[id_occurrencies]['packets'] += 1

        if packet.sport not in  data[id_occurrencies]['src_port']:
            data[id_occurrencies]['src_port'].append(packet.sport)
            data[id_occurrencies]['service_src'].append(get_service_by_port(packet.sport, "udp"))
        if packet.dport not in  data[id_occurrencies]['dst_port']:
            data[id_occurrencies]['dst_port'].append(packet.dport)
            data[id_occurrencies]['service_dst'].append(get_service_by_port(packet.dport, "udp"))

    # return data
    d = []
    for data in data.values():
        d.append(data)
    return d

    # for d in data.values():
    #     print()
    #     print(d) 

def get_service_by_port(port, protocol):
    try:
        service = socket.getservbyport(port, protocol)
        return service
    except:
        return None


def handleTCP(p):
    tcp_packets = [t for t in p if TCP in t]
    
    data = {}  # Dicionário para armazenar os dados processados
    sent_packets = {}  # Dicionário para armazenar pacotes enviados (para correlacionar com ACKs)

    for tcp in tcp_packets:
        try:
            src_ip = tcp[IP].src
            dst_ip = tcp[IP].dst
            src_port = tcp[TCP].sport
            dst_port = tcp[TCP].dport

            ts = tcp.seq
            tsack = None
            rtt = None

            # Identificador único para a conexão (src_ip, dst_ip)
            id_occurrencies = (src_ip, dst_ip)

            # Detectando retransmissão
            retransmission = 1 if 'R' in tcp[TCP].flags else 0

            # Calculando o RTT somente para pacotes com flag ACK
            if 'A' in tcp[TCP].flags:
                tsack = tcp[TCP].ack
                if tsack in sent_packets:
                    sent_packet = sent_packets[tsack]
                    rtt = tcp.time - sent_packet['timestamp'] if sent_packet else None
                    # print(f"RTT Calculado: {rtt} segundos para o pacote {tsack} de {src_ip} -> {dst_ip}")

            if ts not in sent_packets:
                sent_packets[ts] = {'timestamp': tcp.time, 'src_ip': src_ip, 'dst_ip': dst_ip}


            # Processando somente retransmissões com RTT válido
            if rtt and rtt > 0:
                if id_occurrencies not in data:
                    data[id_occurrencies] = {
                        'src_ip': src_ip,
                        'dst_ip': dst_ip,
                        'total_bytes': 0,
                        'src_port': [],
                        'dst_port': [],
                        'packets': 0,
                        'bytes': [],
                        'n_sequence': [],
                        'w_size': [],
                        'retransmission': [],
                        'RTT': []
                    }

                    # Armazenando as informações da conexão
                    data[id_occurrencies]['src_port'].append(src_port)
                    data[id_occurrencies]['dst_port'].append(dst_port)
                    data[id_occurrencies]['total_bytes'] += len(tcp)
                    data[id_occurrencies]['packets'] += 1
                    data[id_occurrencies]['bytes'].append(len(tcp))
                    data[id_occurrencies]['n_sequence'].append(ts)
                    data[id_occurrencies]['retransmission'].append(retransmission)
                    data[id_occurrencies]['RTT'].append(rtt)

            # Armazenando pacotes enviados para correlacionar com ACKs
            if ts not in sent_packets and not retransmission:
                sent_packets[ts] = {'timestamp': tcp.time, 'src_ip': src_ip, 'dst_ip': dst_ip}
                # print(f"Pacote enviado registrado: seq={ts} de {src_ip} -> {dst_ip}")

        except KeyError as e:
            # Em caso de erro ao acessar um campo, podemos registrar ou simplesmente ignorar
            print(f"Erro ao processar pacote: {e}")

    # Verificando o número de conexões processadas
    print(f"Conexões processadas: {len(data)}")

    # Transformando o dicionário em lista
    d = []
    for connection, info in data.items():
        d.append(info)
    return d

#FUNÇÕES PARA T5 PROTOCOLO TCP
# def handleTCP(p):
#     tcp_packets = [t for t in p if TCP in t]
    
#     data = {} 

#     for tcp in tcp_packets:
#         src_ip = tcp[IP].src
#         dst_ip = tcp[IP].dst
#         src_port = tcp[TCP].sport
#         dst_port = tcp[TCP].dport

#         ts = tcp.seq
#         if 'A' in tcp[TCP].flags:
#             tsack = tcp[TCP].ack
#             rtt = tsack - ts
#         else:
#             tsack = None
#             rtt = None

#         if 'R' in tcp[TCP].flags:
#             retransmission = 1
#         else:
#             retransmission = 0

#         #w_size = tcp[TCP].window_size
            
#         id_occurrencies = (src_ip, dst_ip)
      
#         if retransmission == 1 and rtt and rtt > 0:

#             if id_occurrencies not in data:
#                 data[id_occurrencies] = {
#                     'src_ip': src_ip,
#                     'dst_ip':dst_ip,
#                     'total_bytes':0,
#                     'src_port':[],
#                     'dst_port':[],
#                     'packets': 0,
#                     'bytes':[],
#                     'n_sequence':[],
#                     'w_size': [],
#                     'retransmission': [],
#                     'RTT':[]
#                 }
                
#                 data[id_occurrencies]['src_port'].append(src_port)
#                 data[id_occurrencies]['dst_port'].append(dst_port)
#                 data[id_occurrencies]['total_bytes'] += len(tcp)
#                 data[id_occurrencies]['packets'] += 1
#                 data[id_occurrencies]['bytes'].append(len(tcp))
#                 data[id_occurrencies]['n_sequence'].append(ts)
#                 data[id_occurrencies]['retransmission'].append(retransmission)
#                 data[id_occurrencies]['RTT'].append(rtt)
#                 #data[id_occurrencies]['w_size'].append(w_size)
#                 # data[id_occurrencies]['retransmission'].append(retransmission)
    
#     d = []
#     for connection, info in data.items():
#         d.append(info)
#     return d
    
    # for connection, info in data.items():
    #     src_ip, dst_ip = connection
    #     print(f"Connection: {src_ip} -> {dst_ip}")
    #     print(f"  Source IP: {info['src_ip']}")
    #     print(f"  Destination IP: {info['dst_ip']}")
    #     print(f"  Source Ports: {info['src_port']}")
    #     print(f"  Destination Ports: {info['dst_port']}")
    #     print(f"  Total Packets: {info['packets']}")
    #     #total_bytes = sum(info['bytes'])
    #     print(f"  Total Bytes Transferred: {info['total_bytes']} bytes")
    #     print(f"  Sequence Number: {info['n_sequence']}")
    #     print(f"  Retransmission: {info['retransmission']}")
    #     print(f"  RTT: {info['RTT']} microssegundos")

def save_content(content, filename):
    with open(filename, "wb") as f:
        f.write(content)
    print(f"Arquivo salvo em: {filename} com {len(content)} bytes")


def HTTPcontent(p):
    http_packets = [h for h in p if HTTPRequest in h or HTTPResponse in h]
    contentsPerIp = {}

    for http in http_packets:
        if HTTPResponse in http:
            response = http[HTTPResponse]
            if 'Content_Type' in response.fields:
                content_type = response.fields['Content_Type'].decode()

                # Verificar se o conteúdo é HTML
                if 'text/html' in content_type:
                    body = response.payload.load
                    body_base64 = base64.b64encode(body).decode('utf-8')  # Codificando o HTML em Base64
                    ipDst = http.getlayer(IP).dst
                    if ipDst not in contentsPerIp:
                        contentsPerIp[ipDst] = []
                    content = {
                        'type': 'html',  # Especificando que é HTML
                        'content': body_base64  # HTML codificado em Base64
                    }
                    contentsPerIp[ipDst].append(content)

                # Verificar se o conteúdo é uma imagem
                # elif 'image' in content_type:
                #     body = response.payload.load
                #     body_base64 = base64.b64encode(body).decode('utf-8')  # Codificando a imagem em Base64
                #     ext = content_type.split('/')[1]  # Extensão da imagem (ex: png, jpeg)
                #     ipDst = http.getlayer(IP).dst
                #     if ipDst not in contentsPerIp:
                #         contentsPerIp[ipDst] = []
                #     content = {
                #         'type': 'image',  # Especificando que é imagem
                #         'content': body_base64,  # Imagem codificada em Base64
                #         'extension': ext  # Extensão da imagem
                #     }
                #     contentsPerIp[ipDst].append(content)

    return contentsPerIp

# def HTTPcontent(p):
    
#     http_packets = [h for h in p if HTTPRequest in h or HTTPResponse in h]
#     output_dir = "output/"

#     contentsPerIp = {}

#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
#     for i, http in enumerate(http_packets):
#         if HTTPResponse in http:    
#             response = http[HTTPResponse]
#             if 'Content_Type' in response.fields:
#                 content_type = response.fields['Content_Type'].decode()
#             #Verificar se o conteúdo é HTML
#                 filename = ""
#                 if 'text/html' in content_type:
#                     # print("aqui")
#                     body = response.payload.load
#                     filename = f"{output_dir}page_{i}.html"
#                     save_content(body, filename)
#                     print(f"HTML salvo em: {filename}")
#             # Verificar se o conteúdo é uma imagem
#                 elif 'image' in content_type:
#                     body = response.payload.load
#                     ext = content_type.split('/')[1]  # Extensão da imagem (ex: png, jpeg)
#                     filename = f"{output_dir}image_{i}.{ext}"
#                     save_content(body, filename)
#                     print(f"Imagem salva em: {filename}")
#                 ipDst = http.getlayer(IP).dst
#                 if (ipDst not in contentsPerIp):
#                     contentsPerIp[ipDst] = []
#                 ipContents = contentsPerIp[ipDst]
#                 content = {
#                     'type': content_type,
#                     'path': filename
#                 }
#                 ipContents.append(content)
#     return contentsPerIp
                

def handleDNS(p):
    data = {}

    DNSpackets = [d for d in p if DNS in d]

    for dns in DNSpackets:
        if dns.qr == 0:  # qr == 0 consulta DNS
            src_ip = dns[IP].src
            domain = dns.qd.qname.decode('utf-8')
            query_type = dns.qd.qtype

        elif dns.qr == 1:
            domain = dns.qd.qname.decode('utf-8')
            key = (dns[IP].dst, domain)
            if key not in data:
                data[key] = {
                    'src_ip': dns[IP].dst,
                    'domains': domain,
                    'count': 0,
                    'types': [],
                    'domains_ips':[]
                }
                for i in range(dns.ancount):
                    response = dns.an[i]
                    data[key]["types"].append(response.type)
                    data[key]["domains_ips"].append(response.rdata)

            data[key]['count'] += 1
          
    d_api = []
    for d in data.values():
        d_api.append(d)
    return d_api

def handleSNMP(p):
    agentPdus = [SNMPinform, SNMPresponse, SNMPtrapv1, SNMPtrapv2]
    snmpPacketes = [d for d in p if SNMP in d]
    agents = {}
    managers = {}
    for snmp in snmpPacketes:
        manager = True
        for agentPdu in agentPdus:
            if agentPdu in snmp:
               manager = False
               break
        if not manager:
            ip = snmp.getlayer(IP).src
            pdu = f"{snmp[SNMP].PDU}"
            if ip not in agents:
                agents[ip] = {}
            if pdu not in agents[ip]:
                agents[ip][pdu] = 1
            else: 
                agents[ip][pdu] = agents[ip][pdu] + 1
        else:
            ip = snmp.getlayer(IP).src
            pdu = f"{snmp[SNMP].PDU}"
            if ip not in managers:
                managers[ip] = {}
            if pdu not in managers[ip]:
                managers[ip][pdu] = 1
            else: 
                managers[ip][pdu] = managers[ip][pdu] + 1
    return {
        "agents": agents,
        "managers": managers
    }
