from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

from check import OpenFile, clean_str, unQuote, process_string
from dummy import *


def main():
    char_path = "./data/spongebob_characters.json"
    char_data = OpenFile(char_path)
    base_uri = "http://example.org/data/"
    vocab = Namespace("http://example.org/vocab#")

    g = Graph()
    g.bind("v", vocab)

    # CHARACTER
    for char in char_data:
        char_name = clean_str(char["name"])

        if "Birth" in char["info"] or "Performed by" in char["info"] or "Location" in char["info"]:
            continue
        
        g.add((URIRef(f"{base_uri}{char_name}"), RDF.type, URIRef(f"{base_uri}Character")))
        g.add((URIRef(f"{base_uri}{char_name}"), vocab.hasName, Literal(char["name"])))
        g.add((URIRef(f"{base_uri}{char_name}"), vocab['hasUrl'], Literal(char["url"])))

        for key, value in char["info"].items():

            if key in CHAR_INFO_LITERAL:
                value = char["info"][key]
                if type(value) == list:
                    for lst_value in value:
                        g.add((URIRef(f"{base_uri}{char_name}"), vocab[CHAR_INFO_LITERAL[key]], Literal(unQuote(lst_value))))
                else:
                    g.add((URIRef(f"{base_uri}{char_name}"), vocab[CHAR_INFO_LITERAL[key]], Literal(unQuote(value))))
            
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


    # EPISODE
    eps_path = "./data/spongebob_episodes.json"
    eps_data = OpenFile(eps_path)

    for eps in eps_data:
        eps_name = process_string(eps["title"])
        eps_ref = EPS_DICT[eps_name]

        g.add((URIRef(eps_ref), RDF.type, URIRef(f"{base_uri}Episode")))
        g.add((URIRef(eps_ref), vocab.hasTitle, Literal(unQuote(eps["title"]))))
        g.add((URIRef(eps_ref), vocab.hasUrl, Literal(eps["url"])))

        for char in eps["characters"]:
            char_name = clean_str(process_string(char))
            g.add((URIRef(eps_ref), vocab.hasCharacter, URIRef(f"{base_uri}{char_name}")))

        for key, value in eps["info"].items():
            
            if key in EPS_INFO_LITERAL:
                if type(value) == list:
                    for lst_value in value:
                        g.add((URIRef(eps_ref), vocab[EPS_INFO_LITERAL[key]], Literal(lst_value)))
                else:
                    g.add((URIRef(eps_ref), vocab[EPS_INFO_LITERAL[key]], Literal(value)))

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