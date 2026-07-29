INSTITUTIONS = {
    "香港大学":        {"openalex": "I889458895",     "ror": "02zhqgq86"},
    "香港中文大学":    {"openalex": "I177725633",    "ror": "00tve33b33"},
    "香港科技大学":    {"openalex": "I200769079",    "ror": "00q4vv597"},
    "香港城市大学":    {"openalex": "I168719708",    "ror": "03q8dnn23"},
    "香港理工大学":    {"openalex": "I14243506",     "ror": "0030zas98"},
    "香港浸会大学":    {"openalex": "I141568987",    "ror": "00a0c9s79"},
    "香港岭南大学":    {"openalex": "I165488957",    "ror": "006t60a03"},
    "香港教育大学":    {"openalex": "I4210086892",   "ror": "02x0r5z94"},
}

INSTITUTION_KEYWORDS = {
    "香港大学": ["University of Hong Kong", "HKU"],
    "香港中文大学": ["Chinese University of Hong Kong", "CUHK"],
    "香港科技大学": ["Hong Kong University of Science and Technology", "HKUST"],
    "香港城市大学": ["City University of Hong Kong", "CityU"],
    "香港理工大学": ["Hong Kong Polytechnic University", "PolyU"],
    "香港浸会大学": ["Hong Kong Baptist University", "HKBU"],
    "香港岭南大学": ["Lingnan University"],
    "香港教育大学": ["Education University of Hong Kong", "EdUHK"],
}

TOPICS = [
    {
        "name": "集成电路",
        "concept_id": "C530198007",
        "keywords": ["VLSI", "ASIC", "SoC", "FPGA", "semiconductor", "chip design",
                      "integrated circuit", "microelectronics", "CMOS", "silicon photonics"]
    },
    {
        "name": "航空航天",
        "concept_id": "C146978453",
        "keywords": ["aerospace", "aeronautics", "astronautics", "spacecraft",
                      "satellite", "rocket", "propulsion", "aviation", "unmanned aerial"]
    },
    {
        "name": "生物医药",
        "concept_id": "C66782513",
        "keywords": ["biomedical", "pharmaceutical", "drug delivery", "clinical trial",
                      "therapeutic", "diagnostic", "targeted therapy", "immunotherapy",
                      "personalized medicine", "regenerative medicine"]
    },
    {
        "name": "低空经济",
        "concept_id": None,
        "keywords": ["low altitude", "UAV", "drone", "eVTOL", "urban air mobility",
                      "UAS", "unmanned aircraft", "air taxi", "low-altitude economy"]
    },
    {
        "name": "新型储能",
        "concept_id": "C73916439",
        "keywords": ["energy storage", "battery", "supercapacitor", "solid-state battery",
                      "lithium-ion", "sodium-ion", "flow battery", "energy density",
                      "power density", "grid storage"]
    },
    {
        "name": "智能机器人",
        "concept_id": "C34413123",
        "keywords": ["robot", "robotics", "autonomous system", "humanoid",
                      "manipulator", "SLAM", "motion planning", "grasping",
                      "swarm robot", "soft robot"]
    },
    {
        "name": "量子科技",
        "concept_id": "C62520636",
        "keywords": ["quantum computing", "quantum information", "quantum communication",
                      "quantum cryptography", "quantum algorithm", "quantum gate",
                      "superconducting qubit", "topological quantum", "quantum sensor",
                      "quantum error correction", "quantum simulation"]
    },
    {
        "name": "生物制造",
        "concept_id": None,
        "keywords": ["biomanufacturing", "synthetic biology", "biofabrication",
                      "tissue engineering", "bioprinting", "metabolic engineering",
                      "cell factory", "fermentation", "bioprocess", "bioreactor"]
    },
    {
        "name": "氢能",
        "concept_id": "C542482507",
        "keywords": ["hydrogen production", "hydrogen storage", "fuel cell",
                      "hydrogen energy", "water splitting", "hydrogen evolution",
                      "PEMFC", "SOFC", "hydrogen economy"]
    },
    {
        "name": "脑机接口",
        "concept_id": "C173201364",
        "keywords": ["brain-computer interface", "BCI", "neural interface",
                      "brain-machine interface", "EEG", "ECoG", "neural decoding",
                      "neuroprosthetic", "neurostimulation"]
    },
    {
        "name": "具身智能",
        "concept_id": None,
        "keywords": ["embodied intelligence", "embodied AI", "cognitive robotics",
                      "situated agent", "affordance", "sim-to-real", "reinforcement learning",
                      "policy learning", "imitation learning", "world model"]
    },
    {
        "name": "6G",
        "concept_id": None,
        "keywords": ["6G", "terahertz", "THz communication", "beyond 5G",
                      "massive MIMO", "reconfigurable intelligent surface", "RIS",
                      "semantic communication", "integrated sensing", "communication"]
    },
    {
        "name": "新一代信息技术",
        "concept_id": "C121017731",
        "keywords": ["Internet of Things", "IoT", "cloud computing", "edge computing",
                      "ubiquitous computing", "cyber-physical", "digital twin",
                      "fog computing", "information technology", "next-generation network"]
    },
    {
        "name": "生物技术",
        "concept_id": "C150903083",
        "keywords": ["biotechnology", "gene editing", "CRISPR", "genomics",
                      "proteomics", "bioinformatics", "transgenic", "recombinant",
                      "biocatalysis", "enzyme engineering"]
    },
    {
        "name": "新能源",
        "concept_id": "C188573790",
        "keywords": ["solar cell", "photovoltaic", "perovskite", "wind energy",
                      "renewable energy", "clean energy", "sustainable energy",
                      "solar thermal", "bioenergy", "geothermal"]
    },
    {
        "name": "新材料",
        "concept_id": "C192562407",
        "keywords": ["2D material", "graphene", "MXene", "metamaterial",
                      "nanomaterial", "smart material", "functional material",
                      "composite", "metal-organic framework", "MOF",
                      "perovskite material", "topological insulator"]
    },
    {
        "name": "高端装备",
        "concept_id": None,
        "keywords": ["advanced manufacturing", "precision manufacturing",
                      "additive manufacturing", "3D printing", "CNC",
                      "high-end equipment", "smart manufacturing", "industry 4.0",
                      "digital manufacturing", "laser machining"]
    },
    {
        "name": "新能源汽车",
        "concept_id": "C2776422217",
        "keywords": ["electric vehicle", "EV", "NEV", "autonomous driving",
                      "hybrid vehicle", "battery electric", "power electronics",
                      "electric powertrain", "vehicle-to-grid", "charging infrastructure"]
    },
    {
        "name": "绿色环保",
        "concept_id": "C39432304",
        "keywords": ["carbon neutral", "carbon capture", "sustainability",
                      "green technology", "waste treatment", "water treatment",
                      "circular economy", "carbon emission", "life cycle assessment",
                      "climate change mitigation"]
    },
    {
        "name": "海洋装备",
        "concept_id": "C22372391",
        "keywords": ["marine technology", "ocean engineering", "underwater vehicle",
                      "autonomous underwater", "AUV", "ROV", "submarine",
                      "offshore platform", "marine robotics", "underwater communication"]
    },
    {
        "name": "人工智能",
        "concept_id": "C154945302",
        "keywords": ["deep learning", "machine learning", "neural network", "transformer",
                      "large language model", "LLM", "computer vision", "NLP",
                      "reinforcement learning", "generative model",
                      "diffusion model", "self-supervised learning"]
    },
]
