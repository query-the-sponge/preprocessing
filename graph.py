from rdflib import Graph, Literal, Namespace, URIRef, BNode
from rdflib.namespace import RDF, RDFS
from check import OpenFile, clean_str, unQuote, process_string
from dummy import *
from datetime import datetime
import re

def clean_year(value):
    import re
    match = re.match(r"^\d{4}$", value.strip())
    if match:
        return int(match.group(0))
    match = re.search(r"(\d{4})", value)
    if match:
        return int(match.group(1))
    return None

def clean_date(value):
    try:
        return datetime.strptime(value, "%B %d, %Y").date().isoformat()
    except ValueError:
        return None

def clean_time(value):
    try:
        match = re.match(r"(\d{1,2}):(\d{2})\s*(am|pm)", value, re.IGNORECASE)
        if match:
            hours, minutes, period = match.groups()
            hours = int(hours)
            if period.lower() == "pm" and hours != 12:
                hours += 12
            elif period.lower() == "am" and hours == 12:
                hours = 0
            return f"{hours:02}:{minutes}:00"
    except Exception:
        pass
    return None

def clean_duration(value):
    try:
        minutes, seconds = 0, 0
        match = re.search(r"(\d+)\s*minutes?", value, re.IGNORECASE)
        if match:
            minutes = int(match.group(1))
        match = re.search(r"(\d+)\s*seconds?", value, re.IGNORECASE)
        if match:
            seconds = int(match.group(1))
        return f"PT{minutes}M{seconds}S" if minutes or seconds else None
    except Exception:
        pass
    return None

def clean_decimal(value):
    try:
        match = re.match(r"([\d.]+)", value)
        if match:
            return float(match.group(1))
    except Exception:
        pass
    return None

def process_human_name(name):
    import re
    match = re.match(r"(.*?)(\s*\((.*?)\))?$", name.strip())
    base_name = match.group(1).strip() if match.group(1) else name.strip()
    metadata = match.group(3).strip() if match.group(3) else None
    role_match = re.search(r"\s+as\s+(.+)$", base_name, re.IGNORECASE)
    if role_match:
        role = role_match.group(1).strip()
        base_name = re.sub(r"\s+as\s+.+$", "", base_name, flags=re.IGNORECASE).strip()
        metadata = role
    return base_name, metadata

def process_portrayer_entry(entry):
    match = re.match(r"^(.*?)(\s*\((.*?)\))?$", entry.strip())
    base_name = match.group(1).strip() if match.group(1) else entry.strip()
    content = match.group(3).strip() if match.group(3) else None
    episodes = []
    explanation = None
    conjunction_match = re.match(r"^(.*?)(\s+(in|for)\s+)(.*)$", base_name, re.IGNORECASE)
    if conjunction_match:
        base_name = conjunction_match.group(1).strip()
        explanation = conjunction_match.group(4).strip()
    if content:
        for part in re.split(r',\s*', content):
            if re.match(r"\".*?\"", part):
                episodes.append(part.strip('"'))
            else:
                explanation = f"{explanation}, {part}" if explanation else part
    return base_name, explanation, episodes

def main():
    char_path = "./data/spongebob_characters.json"
    char_data = OpenFile(char_path)
    base_uri = "http://example.org/data/"
    vocab = Namespace("http://example.org/vocab#")
    g = Graph()
    g.bind("v", vocab)
    for char in char_data:
        char_name = clean_str(char["name"])
        if "Birth" in char["info"] or "Performed by" in char["info"] or "Location" in char["info"]:
            continue
        g.add((URIRef(f"{base_uri}{char_name}"), RDF.type, URIRef(f"{base_uri}Character")))
        g.add((URIRef(f"{base_uri}{char_name}"), vocab.hasName, Literal(char["name"], datatype=XSD.string)))
        g.add((URIRef(f"{base_uri}{char_name}"), RDFS.label, Literal(char["name"], datatype=XSD.string)))
        g.add((URIRef(f"{base_uri}{char_name}"), vocab["hasUrl"], Literal(char["url"], datatype=XSD.string)))
        for key, value in char["info"].items():
            if key in CHAR_INFO_LITERAL:
                value = char["info"][key]
                if type(value) == list:
                    for lst_value in value:
                        g.add((URIRef(f"{base_uri}{char_name}"), vocab[CHAR_INFO_LITERAL[key]], Literal(unQuote(lst_value), datatype=XSD.string)))
                else:
                    g.add((URIRef(f"{base_uri}{char_name}"), vocab[CHAR_INFO_LITERAL[key]], Literal(unQuote(value), datatype=XSD.string)))
            elif key in CHAR_INFO_CHAR:
                value = char["info"][key]
                if type(value) == list:
                    for lst_value in value:
                        clean_value = clean_str(process_string(lst_value))
                        if clean_value not in CHARS:
                            continue
                        g.add((URIRef(f"{base_uri}{char_name}"), vocab[CHAR_INFO_CHAR[key]], URIRef(f"{base_uri}{clean_value}")))
                else:
                    clean_value = clean_str(process_string(value))
                    if clean_value not in CHARS:
                        continue
                    g.add((URIRef(f"{base_uri}{char_name}"), vocab[CHAR_INFO_CHAR[key]], URIRef(f"{base_uri}{clean_value}")))
            elif key == "Portrayer":
                portrayer_entries = value if isinstance(value, list) else [value]
                for entry in portrayer_entries:
                    name, explanation, episodes = process_portrayer_entry(entry)
                    encoded_name = clean_str(unQuote(name))
                    human_node = URIRef(f"{base_uri}{encoded_name}")
                    g.add((human_node, RDF.type, URIRef(f"{base_uri}Human")))
                    g.add((human_node, RDFS.label, Literal(name, datatype=XSD.string)))
                    g.add((human_node, vocab.hasName, Literal(name, datatype=XSD.string)))
                    relationship_node = BNode()
                    g.add((relationship_node, RDF.type, URIRef(f"{base_uri}PortrayalRole")))
                    g.add((relationship_node, vocab.portrayedBy, human_node))
                    if explanation:
                        g.add((relationship_node, vocab.hasExplanation, Literal(explanation, datatype=XSD.string)))
                    g.add((URIRef(f"{base_uri}{char_name}"), vocab.hasPortrayer, relationship_node))
                    for episode_name in episodes:
                        clean_episode = process_string(episode_name)
                        if clean_episode in EPS_DICT:
                            episode_ref = EPS_DICT[clean_episode]
                            g.add((relationship_node, vocab.inEpisode, URIRef(f"{base_uri}{episode_ref}")))
            elif key in CHAR_INFO_EPS:
                eps_title = char["info"][key]
                if type(eps_title) == list:
                    for lst_value in value:
                        clean = process_string(lst_value)
                        if clean not in EPS_DICT:
                            continue
                        eps_ref = EPS_DICT[clean]
                        g.add((URIRef(f"{base_uri}{char_name}"), vocab[CHAR_INFO_EPS[key]], URIRef(f"{base_uri}{eps_ref}")))
                else:
                    clean = process_string(char["info"][key])
                    if clean not in EPS_DICT:
                        continue
                    eps_ref = EPS_DICT[clean]
                    g.add((URIRef(f"{base_uri}{char_name}"), vocab[CHAR_INFO_EPS[key]], URIRef(f"{base_uri}{eps_ref}")))
    eps_path = "./data/spongebob_episodesv2.json"
    eps_data = OpenFile(eps_path)
    for eps in eps_data:
        eps_name = process_string(eps["title"])
        eps_ref = EPS_DICT[eps_name]
        g.add((URIRef(eps_ref), RDF.type, URIRef(f"{base_uri}Episode")))
        g.add((URIRef(eps_ref), vocab.hasTitle, Literal(unQuote(eps["title"]), datatype=XSD.string)))
        g.add((URIRef(eps_ref), RDFS.label, Literal(unQuote(eps["title"]), datatype=XSD.string)))
        g.add((URIRef(eps_ref), vocab.hasUrl, Literal(eps["url"], datatype=XSD.string)))
        for char in eps["characters"]:
            char_name = clean_str(process_string(char))
            g.add((URIRef(eps_ref), vocab.hasCharacter, URIRef(f"{base_uri}{char_name}")))
        for key, value in eps["info"].items():
            if key in EPS_INFO_LITERAL:
                datatype = EPS_INFO_LITERAL_TYPES.get(key, XSD.string)
                if type(value) == list:
                    for lst_value in value:
                        cleaned_value = None
                        if datatype == XSD.date:
                            cleaned_value = clean_date(lst_value)
                        elif datatype == XSD.time:
                            cleaned_value = clean_time(lst_value)
                        elif datatype == XSD.duration:
                            cleaned_value = clean_duration(lst_value)
                        elif datatype == XSD.decimal:
                            cleaned_value = clean_decimal(lst_value)
                        elif datatype == XSD.gYear:
                            cleaned_value = clean_year(lst_value)
                        else:
                            cleaned_value = lst_value
                        if cleaned_value is not None:
                            g.add((URIRef(eps_ref), vocab[EPS_INFO_LITERAL[key]], Literal(cleaned_value, datatype=datatype)))
                else:
                    cleaned_value = None
                    if datatype == XSD.date:
                        cleaned_value = clean_date(value)
                    elif datatype == XSD.time:
                        cleaned_value = clean_time(value)
                    elif datatype == XSD.duration:
                        cleaned_value = clean_duration(value)
                    elif datatype == XSD.decimal:
                        cleaned_value = clean_decimal(value)
                    elif datatype == XSD.gYear:
                        cleaned_value = clean_year(value)
                    else:
                        cleaned_value = value
                    if cleaned_value is not None:
                        g.add((URIRef(eps_ref), vocab[EPS_INFO_LITERAL[key]], Literal(cleaned_value, datatype=datatype)))
            elif key in EPS_INFO_NODES:
                predicate = EPS_INFO_NODES[key]
                if isinstance(value, list):
                    for item in value:
                        base_name, metadata = process_human_name(item)
                        encoded_name = clean_str(unQuote(base_name))
                        person_uri = URIRef(f"{base_uri}{encoded_name}")
                        relationship_node = BNode()
                        g.add((relationship_node, RDF.type, URIRef(f"{base_uri}EpisodeRole")))
                        g.add((relationship_node, vocab[predicate], person_uri))
                        g.add((URIRef(f"{base_uri}{eps_ref}"), vocab.generalInfo, relationship_node))
                        if metadata:
                            g.add((relationship_node, vocab.hasRole, Literal(metadata, datatype=XSD.string)))
                        g.add((person_uri, RDF.type, URIRef(f"{base_uri}Human")))
                        g.add((person_uri, RDFS.label, Literal(base_name, datatype=XSD.string)))
                        g.add((person_uri, vocab.hasName, Literal(base_name, datatype=XSD.string)))
                else:
                    base_name, metadata = process_human_name(value)
                    encoded_name = clean_str(unQuote(base_name))
                    person_uri = URIRef(f"{base_uri}{encoded_name}")
                    relationship_node = BNode()
                    g.add((relationship_node, RDF.type, URIRef(f"{base_uri}EpisodeRole")))
                    g.add((relationship_node, vocab[predicate], person_uri))
                    g.add((URIRef(f"{base_uri}{eps_ref}"), vocab.generalInfo, relationship_node))
                    if metadata:
                        g.add((relationship_node, vocab.hasRole, Literal(metadata, datatype=XSD.string)))
                    g.add((person_uri, RDF.type, URIRef(f"{base_uri}Human")))
                    g.add((person_uri, RDFS.label, Literal(base_name, datatype=XSD.string)))
                    g.add((person_uri, vocab.hasName, Literal(base_name, datatype=XSD.string)))
            elif key in EPS_INFO_EPS:
                if type(value) == list:
                    for lst_value in value:
                        obj = process_string(lst_value)
                        if obj not in EPS_DICT:
                            continue
                        obj_ref = EPS_DICT[obj]
                        g.add((URIRef(eps_ref), vocab[EPS_INFO_EPS[key]], URIRef(f"{base_uri}{obj_ref}")))
                else:
                    obj = process_string(value)
                    if obj not in EPS_DICT:
                        continue
                    obj_ref = EPS_DICT[obj]
                    g.add((URIRef(eps_ref), vocab[EPS_INFO_EPS[key]], URIRef(f"{base_uri}{obj_ref}")))
    output = g.serialize(format="turtle", base=base_uri)
    with open("./result/output.ttl", "w", encoding="utf-8") as file:
        file.write(str(output))

if __name__ == "__main__":
    main()