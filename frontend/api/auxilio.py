from scapy.all import *
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
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
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
        return "<desconhecido>"

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
        print(getDstIP(packet))
        print(getDstMAC(packet))
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
    #df.drop_duplicates("IPs", inplace = True)

    for m in df["MACs"]:
        company.append(getCompanyByMACAdress(m))
    
    df.insert(2, "Company", company)
    print(df)
    tabela = df.to_dict()
 
    return tabela