from dataclasses import dataclass, field
from typing import Optional
import json

@dataclass
class DataCenter:
    id: str
    name: str
    operator: str
    state: str
    city: str
    lat: float
    lng: float
    status: str
    capacity_mw: Optional[float] = None
    area_sqft: Optional[int] = None
    announced_year: Optional[int] = None
    operational_year: Optional[int] = None
    investment_usd_bn: Optional[float] = None
    description: str = ""
    tags: list = field(default_factory=list)
    source_url: str = ""

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "operator": self.operator,
            "state": self.state,
            "city": self.city,
            "lat": self.lat,
            "lng": self.lng,
            "status": self.status,
            "capacity_mw": self.capacity_mw,
            "area_sqft": self.area_sqft,
            "announced_year": self.announced_year,
            "operational_year": self.operational_year,
            "investment_usd_bn": self.investment_usd_bn,
            "description": self.description,
            "tags": self.tags,
            "source_url": self.source_url,
        }

DATACENTERS = [
    DataCenter("ms-va-1","Microsoft Datacenter Campus","Microsoft","Virginia","Boydton",36.667,-78.375,"active",capacity_mw=400,announced_year=2010,operational_year=2011,description="One of Microsoft's largest US data center campuses, part of the Mid-Atlantic Region.",tags=["hyperscale","azure","ai"]),
    DataCenter("ms-va-2","Microsoft Azure Datacenter","Microsoft","Virginia","Ashburn",39.043,-77.487,"active",capacity_mw=200,announced_year=2020,operational_year=2022,description="Major Azure hub in Ashburn, the 'Data Center Alley' of Northern Virginia.",tags=["hyperscale","azure","ai"]),
    DataCenter("ms-ia-1","Microsoft Iowa Datacenter","Microsoft","Iowa","Altoona",41.655,-93.468,"active",capacity_mw=300,announced_year=2012,operational_year=2014,description="Large renewable-powered campus, one of Microsoft's greenest facilities.",tags=["hyperscale","azure","renewable"]),
    DataCenter("ms-wa-1","Microsoft Redmond Datacenter","Microsoft","Washington","Redmond",47.673,-122.121,"active",capacity_mw=150,announced_year=2008,operational_year=2009,description="Near Microsoft HQ; original Azure infrastructure hub.",tags=["hyperscale","azure"]),
    DataCenter("ms-il-1","Microsoft Chicago Datacenter","Microsoft","Illinois","Chicago",41.831,-88.012,"active",capacity_mw=200,announced_year=2015,operational_year=2017,description="Strategic Midwest hub supporting Azure Central US region.",tags=["hyperscale","azure"]),
    DataCenter("ms-tx-1","Microsoft San Antonio Datacenter","Microsoft","Texas","San Antonio",29.488,-98.628,"active",capacity_mw=250,announced_year=2017,operational_year=2019,description="Large Texas campus with significant AI/ML workload support.",tags=["hyperscale","azure","ai"]),
    DataCenter("ms-wi-1","Microsoft Mount Pleasant Datacenter","Microsoft","Wisconsin","Mount Pleasant",42.698,-88.189,"construction",capacity_mw=800,investment_usd_bn=3.3,announced_year=2023,operational_year=2026,description="$3.3B mega-campus for AI infrastructure expansion, one of the largest in the Midwest.",tags=["hyperscale","azure","ai","megacampus"]),
    DataCenter("ms-pa-1","Microsoft Cambria County Datacenter","Microsoft","Pennsylvania","Ebensburg",40.484,-78.724,"planned",capacity_mw=500,investment_usd_bn=10.0,announced_year=2024,operational_year=2027,description="Part of Microsoft's $10B Pennsylvania investment for AI data centers.",tags=["hyperscale","azure","ai"]),
    DataCenter("ms-oh-1","Microsoft New Albany Datacenter","Microsoft","Ohio","New Albany",40.082,-82.792,"construction",capacity_mw=600,investment_usd_bn=1.0,announced_year=2022,operational_year=2025,description="Rapidly expanding Ohio campus anchoring the Microsoft Midwest AI corridor.",tags=["hyperscale","azure","ai"]),
    DataCenter("goog-or-1","Google The Dalles Datacenter","Google","Oregon","The Dalles",45.594,-121.178,"active",capacity_mw=280,announced_year=2005,operational_year=2006,description="Google's first purpose-built data center; supports Search and AI workloads.",tags=["hyperscale","gcp","ai"]),
    DataCenter("goog-ia-1","Google Council Bluffs Datacenter","Google","Iowa","Council Bluffs",41.262,-95.861,"active",capacity_mw=350,announced_year=2006,operational_year=2008,description="Major GCP facility; Google has invested $4B+ in Iowa.",tags=["hyperscale","gcp","renewable"]),
    DataCenter("goog-sc-1","Google Berkeley County Datacenter","Google","South Carolina","Moncks Corner",33.195,-80.012,"active",capacity_mw=200,announced_year=2007,operational_year=2008,description="First East Coast Google data center; significant AI inference capacity.",tags=["hyperscale","gcp"]),
    DataCenter("goog-ok-1","Google Pryor Creek Datacenter","Google","Oklahoma","Pryor",36.303,-95.319,"active",capacity_mw=250,announced_year=2007,operational_year=2009,description="Wind-powered facility in the MidAmerica Industrial Park.",tags=["hyperscale","gcp","renewable"]),
    DataCenter("goog-al-1","Google Jackson County Datacenter","Google","Alabama","Hollywood",34.742,-86.113,"active",capacity_mw=150,announced_year=2018,operational_year=2020,description="Tennessee Valley Authority renewable power anchor.",tags=["hyperscale","gcp","renewable"]),
    DataCenter("goog-tx-1","Google Midlothian Datacenter","Google","Texas","Midlothian",32.480,-97.004,"active",capacity_mw=300,announced_year=2019,operational_year=2021,description="Large Texas campus; key Gemini AI inference node.",tags=["hyperscale","gcp","ai"]),
    DataCenter("goog-nv-1","Google Las Vegas Datacenter","Google","Nevada","Henderson",36.044,-115.032,"construction",capacity_mw=400,investment_usd_bn=1.0,announced_year=2023,operational_year=2026,description="New Nevada campus for AI/ML workloads and GCP Southwest expansion.",tags=["hyperscale","gcp","ai"]),
    DataCenter("goog-va-1","Google Reston Datacenter","Google","Virginia","Reston",38.959,-77.357,"active",capacity_mw=180,announced_year=2019,operational_year=2021,description="Northern Virginia hub supporting Google Cloud East US.",tags=["hyperscale","gcp"]),
    DataCenter("aws-va-1","AWS us-east-1 Campus","Amazon","Virginia","Ashburn",39.033,-77.478,"active",capacity_mw=600,announced_year=2006,operational_year=2007,description="AWS's largest and most trafficked region; hosts massive AI training infrastructure.",tags=["hyperscale","aws","ai"]),
    DataCenter("aws-or-1","AWS us-west-2 Campus","Amazon","Oregon","Boardman",45.843,-119.700,"active",capacity_mw=450,announced_year=2011,operational_year=2012,description="Key West Coast AWS region; major SageMaker and Bedrock hub.",tags=["hyperscale","aws","ai"]),
    DataCenter("aws-oh-1","AWS us-east-2 Campus","Amazon","Ohio","New Albany",40.082,-82.799,"active",capacity_mw=350,announced_year=2016,operational_year=2016,description="Rapidly growing Central US AWS region for AI workloads.",tags=["hyperscale","aws","ai"]),
    DataCenter("aws-ca-1","AWS us-west-1 Campus","Amazon","California","San Jose",37.338,-121.886,"active",capacity_mw=200,announced_year=2009,operational_year=2009,description="Silicon Valley AWS hub; proximity to tech customers.",tags=["hyperscale","aws"]),
    DataCenter("aws-tn-1","AWS Clarksville Datacenter","Amazon","Tennessee","Clarksville",36.529,-87.359,"construction",capacity_mw=500,investment_usd_bn=1.5,announced_year=2023,operational_year=2026,description="Massive new AWS campus focused on AI and cloud expansion in the Southeast.",tags=["hyperscale","aws","ai"]),
    DataCenter("aws-ms-1","AWS Mississippi Datacenter","Amazon","Mississippi","Hernando",34.836,-89.997,"planned",capacity_mw=300,investment_usd_bn=1.0,announced_year=2024,operational_year=2027,description="New AWS facility anchoring Mississippi's data center growth.",tags=["hyperscale","aws"]),
    DataCenter("aws-in-1","AWS Indiana Datacenter","Amazon","Indiana","New Carlisle",41.700,-86.515,"construction",capacity_mw=700,investment_usd_bn=11.0,announced_year=2024,operational_year=2026,description="Part of AWS's $11B Indiana investment; major AI/ML training cluster.",tags=["hyperscale","aws","ai","megacampus"]),
    DataCenter("meta-or-1","Meta Prineville Datacenter","Meta","Oregon","Prineville",44.300,-120.834,"active",capacity_mw=350,announced_year=2010,operational_year=2011,description="Meta's first owned data center; Open Compute Project birthplace.",tags=["hyperscale","meta","ai"]),
    DataCenter("meta-nc-1","Meta Forest City Datacenter","Meta","North Carolina","Forest City",35.335,-81.865,"active",capacity_mw=300,announced_year=2011,operational_year=2012,description="Major East Coast Meta facility; supports AI model training.",tags=["hyperscale","meta","ai"]),
    DataCenter("meta-ia-1","Meta Altoona Datacenter","Meta","Iowa","Altoona",41.655,-93.468,"active",capacity_mw=400,announced_year=2013,operational_year=2015,description="Large renewable-powered Meta campus in central Iowa.",tags=["hyperscale","meta","renewable"]),
    DataCenter("meta-tx-1","Meta Fort Worth Datacenter","Meta","Texas","Fort Worth",32.712,-97.427,"active",capacity_mw=400,announced_year=2015,operational_year=2017,description="Massive Texas campus; key Llama AI model training node.",tags=["hyperscale","meta","ai"]),
    DataCenter("meta-nm-1","Meta Eagle Mountain Datacenter","Meta","New Mexico","Los Lunas",34.809,-106.737,"construction",capacity_mw=400,investment_usd_bn=1.0,announced_year=2022,operational_year=2025,description="Expanding Meta presence in the Southwest; AI/inference focused.",tags=["hyperscale","meta","ai"]),
    DataCenter("meta-id-1","Meta Kuna Datacenter","Meta","Idaho","Kuna",43.488,-116.419,"construction",capacity_mw=300,investment_usd_bn=0.8,announced_year=2023,operational_year=2026,description="New Meta campus in the Treasure Valley; part of AI infrastructure buildout.",tags=["hyperscale","meta","ai"]),
    DataCenter("meta-la-1","Meta DeRidder Datacenter","Meta","Louisiana","DeRidder",30.846,-93.291,"announced",capacity_mw=500,investment_usd_bn=1.0,announced_year=2024,operational_year=2027,description="Announced Meta facility leveraging Louisiana's energy costs and incentives.",tags=["hyperscale","meta","ai"]),
    DataCenter("nv-tx-1","NVIDIA Voyager Datacenter","NVIDIA","Texas","Austin",30.266,-97.750,"construction",capacity_mw=200,investment_usd_bn=0.5,announced_year=2024,operational_year=2026,description="NVIDIA's first owned data center for AI research and DGX Cloud.",tags=["ai","gpu","nvidia"]),
    DataCenter("xai-tn-1","xAI Colossus Memphis","xAI","Tennessee","Memphis",35.149,-90.048,"active",capacity_mw=150,investment_usd_bn=1.0,announced_year=2024,operational_year=2024,description="World's largest GPU cluster (100k+ H100s). Built in record ~120 days. Training Grok models.",tags=["ai","gpu","llm","xai"]),
    DataCenter("xai-tn-2","xAI Colossus Expansion","xAI","Tennessee","Memphis",35.155,-90.052,"construction",capacity_mw=300,investment_usd_bn=3.0,announced_year=2024,operational_year=2025,description="Rapid 2x expansion of the Colossus supercluster to 200k+ GPUs.",tags=["ai","gpu","llm","xai"]),
    DataCenter("oai-tx-1","Stargate Texas Datacenter","OpenAI/SoftBank/Oracle","Texas","Abilene",32.449,-99.733,"construction",capacity_mw=800,investment_usd_bn=100.0,announced_year=2025,operational_year=2026,description="First site of Project Stargate — $100B AI infrastructure initiative. Massive GPU supercluster for OpenAI training.",tags=["ai","gpu","llm","stargate","megacampus"]),
    DataCenter("oai-pa-1","Stargate Pennsylvania Datacenter","OpenAI/SoftBank/Oracle","Pennsylvania","Bethlehem",40.625,-75.370,"planned",capacity_mw=600,investment_usd_bn=20.0,announced_year=2025,operational_year=2027,description="Stargate expansion site on former Bethlehem Steel grounds.",tags=["ai","gpu","llm","stargate"]),
    DataCenter("ora-tx-1","Oracle Austin Datacenter","Oracle","Texas","Austin",30.399,-97.727,"active",capacity_mw=200,announced_year=2016,operational_year=2018,description="Major Oracle Cloud Infrastructure hub; AI/OCI services.",tags=["hyperscale","oci","ai"]),
    DataCenter("ora-il-1","Oracle Chicago Datacenter","Oracle","Illinois","Chicago",41.843,-87.888,"active",capacity_mw=150,announced_year=2019,operational_year=2020,description="Oracle Cloud Midwest region supporting enterprise AI workloads.",tags=["hyperscale","oci","ai"]),
    DataCenter("ora-wa-1","Oracle Hillsboro Datacenter","Oracle","Washington","Hillsboro",45.524,-122.990,"active",capacity_mw=180,announced_year=2020,operational_year=2022,description="Pacific Northwest OCI region; AI inference services.",tags=["hyperscale","oci","ai"]),
    DataCenter("ora-tx-2","Oracle San Antonio AI Campus","Oracle","Texas","San Antonio",29.500,-98.620,"construction",capacity_mw=400,investment_usd_bn=1.5,announced_year=2024,operational_year=2026,description="New AI-optimized Oracle campus; part of Stargate partnership buildout.",tags=["hyperscale","oci","ai","stargate"]),
    DataCenter("apple-nc-1","Apple Maiden Datacenter","Apple","North Carolina","Maiden",35.573,-81.222,"active",capacity_mw=100,announced_year=2009,operational_year=2012,description="Apple's flagship US data center; iCloud & Siri AI backend.",tags=["hyperscale","apple","ai"]),
    DataCenter("apple-or-1","Apple Prineville Datacenter","Apple","Oregon","Prineville",44.307,-120.843,"active",capacity_mw=100,announced_year=2012,operational_year=2013,description="Renewable-powered Apple facility for iCloud West Coast.",tags=["hyperscale","apple","renewable"]),
    DataCenter("apple-nv-1","Apple Reno Datacenter","Apple","Nevada","Reno",39.485,-119.698,"active",capacity_mw=100,announced_year=2012,operational_year=2013,description="Solar and geothermal powered facility for Apple services.",tags=["hyperscale","apple","renewable"]),
    DataCenter("apple-ia-1","Apple Waukee Datacenter","Apple","Iowa","Waukee",41.607,-93.888,"active",capacity_mw=150,investment_usd_bn=1.3,announced_year=2015,operational_year=2018,description="Expanded Iowa campus with $1.3B investment; renewable powered.",tags=["hyperscale","apple","renewable"]),
    DataCenter("ibm-tx-1","IBM Dallas Datacenter","IBM","Texas","Dallas",32.899,-97.040,"active",capacity_mw=100,announced_year=2015,operational_year=2017,description="IBM Cloud US South region; watsonx AI platform anchor.",tags=["cloud","ibm","ai"]),
    DataCenter("ibm-va-1","IBM Ashburn Datacenter","IBM","Virginia","Ashburn",39.035,-77.491,"active",capacity_mw=80,announced_year=2017,operational_year=2019,description="IBM Cloud US East region; enterprise AI services.",tags=["cloud","ibm","ai"]),
    DataCenter("eq-va-1","Equinix DC Campus","Equinix","Virginia","Ashburn",39.032,-77.474,"active",capacity_mw=300,announced_year=2000,operational_year=2001,description="Equinix's largest US campus; critical AI interconnection hub.",tags=["colocation","equinix"]),
    DataCenter("eq-ca-1","Equinix SV Campus","Equinix","California","San Jose",37.341,-121.895,"active",capacity_mw=200,announced_year=1998,operational_year=1999,description="Original Equinix campus; Silicon Valley AI startup ecosystem hub.",tags=["colocation","equinix"]),
    DataCenter("eq-ny-1","Equinix NY Campus","Equinix","New York","Secaucus",40.789,-74.060,"active",capacity_mw=150,announced_year=2002,operational_year=2003,description="Financial district AI & HFT infrastructure nexus.",tags=["colocation","equinix"]),
    DataCenter("cw-nj-1","CoreWeave Weehawken Campus","CoreWeave","New Jersey","Weehawken",40.768,-74.021,"active",capacity_mw=100,announced_year=2022,operational_year=2022,description="CoreWeave HQ campus; GPU cloud pioneer for AI/ML startups.",tags=["gpu","cloud","ai","coreweave"]),
    DataCenter("cw-il-1","CoreWeave Chicago Campus","CoreWeave","Illinois","Chicago",41.873,-87.702,"active",capacity_mw=200,announced_year=2023,operational_year=2023,description="Major CoreWeave expansion; thousands of H100 GPUs for AI training.",tags=["gpu","cloud","ai","coreweave"]),
    DataCenter("cw-tx-1","CoreWeave Texas Campus","CoreWeave","Texas","Garland",32.912,-96.638,"construction",capacity_mw=300,investment_usd_bn=1.2,announced_year=2024,operational_year=2025,description="New CoreWeave GPU supercluster in the Dallas metro area.",tags=["gpu","cloud","ai","coreweave"]),
    DataCenter("ll-tx-1","Lambda Labs Austin GPU Cloud","Lambda Labs","Texas","Austin",30.275,-97.740,"active",capacity_mw=50,announced_year=2022,operational_year=2023,description="Lambda GPU Cloud facility; on-demand AI training for researchers.",tags=["gpu","cloud","ai"]),
    DataCenter("cr-nd-1","Crusoe AI Datacenter","Crusoe Energy","North Dakota","Tioga",48.397,-102.939,"active",capacity_mw=40,announced_year=2021,operational_year=2021,description="Stranded gas-powered AI compute; carbon-negative data center.",tags=["ai","gpu","sustainable"]),
    DataCenter("nextera-fl-1","NextEra Doral AI Campus","NextEra Energy","Florida","Doral",25.818,-80.340,"planned",capacity_mw=400,investment_usd_bn=1.5,announced_year=2024,operational_year=2027,description="Nuclear-backed AI data center campus leveraging Florida Power & Light.",tags=["ai","nuclear","planned"]),
    DataCenter("aws-or-2","AWS Anthropic Training Cluster","Amazon/Anthropic","Oregon","Hillsboro",45.522,-122.987,"active",capacity_mw=120,announced_year=2023,operational_year=2024,description="Dedicated AWS Trainium2 cluster for Anthropic Claude model training.",tags=["ai","gpu","llm","anthropic"]),
    DataCenter("switch-nv-1","Switch SuperNAP Las Vegas","Switch","Nevada","Las Vegas",36.098,-115.172,"active",capacity_mw=650,announced_year=2007,operational_year=2008,description="One of the world's largest data centers; hosts major AI/cloud tenants.",tags=["colocation","switch"]),
    DataCenter("cyrus-mi-1","CyrusOne Detroit Datacenter","CyrusOne","Michigan","Auburn Hills",42.668,-83.232,"construction",capacity_mw=200,investment_usd_bn=0.6,announced_year=2023,operational_year=2025,description="Rapid Midwest expansion in response to AI demand surge.",tags=["colocation","ai"]),
    DataCenter("qts-ga-1","QTS Atlanta Datacenter","QTS Realty","Georgia","Atlanta",33.749,-84.388,"active",capacity_mw=150,announced_year=2012,operational_year=2014,description="Major Southeast hub; Microsoft and AWS anchor tenants.",tags=["colocation","ai"]),
    DataCenter("vantage-wy-1","Vantage Wyoming AI Campus","Vantage Data Centers","Wyoming","Cheyenne",41.140,-104.820,"construction",capacity_mw=200,investment_usd_bn=0.4,announced_year=2023,operational_year=2025,description="Cheyenne is emerging as a top-5 US data center market for AI workloads.",tags=["colocation","ai"]),
]

def get_all_datacenters():
    return DATACENTERS

def get_datacenters_as_json():
    return json.dumps([dc.to_dict() for dc in DATACENTERS], indent=2)

def get_stats():
    total = len(DATACENTERS)
    active = sum(1 for dc in DATACENTERS if dc.status == "active")
    construction = sum(1 for dc in DATACENTERS if dc.status == "construction")
    planned = sum(1 for dc in DATACENTERS if dc.status in ("planned", "announced"))
    total_mw = sum(dc.capacity_mw for dc in DATACENTERS if dc.capacity_mw)
    total_inv = sum(dc.investment_usd_bn for dc in DATACENTERS if dc.investment_usd_bn)
    operators = len(set(dc.operator for dc in DATACENTERS))
    return {
        "total": total,
        "active": active,
        "construction": construction,
        "planned": planned,
        "total_mw": round(total_mw),
        "total_investment_bn": round(total_inv, 1),
        "operators": operators,
        "states": len(set(dc.state for dc in DATACENTERS)),
    }
