from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD


def infer_ontology(graph):
    ontology = Graph()
    ontology.bind("owl", OWL)
    ontology.bind("rdfs", RDFS)
    classes = set(graph.objects(None, RDF.type))
    for cls in classes:
        if isinstance(cls, URIRef):
            ontology.add((cls, RDF.type, OWL.Class))
        elif isinstance(cls, BNode):
            ontology.add((cls, RDF.type, OWL.Class))
    properties = set(graph.predicates(None, None))
    for prop in properties:
        if isinstance(prop, URIRef):
            ontology.add((prop, RDF.type, RDF.Property))
            subjects = set(graph.subjects(predicate=prop))
            inferred_domains = set()
            for subj in subjects:
                if isinstance(subj, URIRef) or isinstance(subj, BNode):
                    types = set(graph.objects(subj, RDF.type))
                    if types:
                        inferred_domains.update(types)
                    else:
                        inferred_domains.add(
                            OWL.Thing
                        )
                elif isinstance(subj, Literal):
                    inferred_domains.add(RDFS.Literal)
            for domain in inferred_domains:
                ontology.add((prop, RDFS.domain, domain))
            objects = set(graph.objects(predicate=prop))
            inferred_ranges = set()
            for obj in objects:
                if isinstance(obj, URIRef) or isinstance(obj, BNode):
                    types = set(graph.objects(obj, RDF.type))
                    if types:
                        inferred_ranges.update(types)
                    else:
                        inferred_ranges.add(
                            OWL.Thing
                        )
                elif isinstance(obj, Literal):
                    datatype = obj.datatype if obj.datatype else RDFS.Literal
                    inferred_ranges.add(datatype)
            for range_ in inferred_ranges:
                ontology.add((prop, RDFS.range, range_))
    return ontology

g = Graph()
g.parse("./result/output3.ttl", format="turtle")

ontology_graph = infer_ontology(g)
ontology_graph.serialize("inferred_ontology.ttl", format="turtle")
