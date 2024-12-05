from rdflib import Graph, Namespace, RDF, RDFS, URIRef, Literal
from rdflib.namespace import SH, OWL, XSD

def ontology_to_shacl(ontology_graph):
    shacl_graph = Graph()
    SHAPE = Namespace("http://example.org/shapes#")
    shacl_graph.bind("sh", SH)
    shacl_graph.bind("shapes", SHAPE)
    for cls in ontology_graph.subjects(RDF.type, OWL.Class):
        class_shape = URIRef(f"http://example.org/shapes#{cls.split('/')[-1]}Shape")
        shacl_graph.add((class_shape, RDF.type, SH.NodeShape))
        shacl_graph.add((class_shape, SH.targetClass, cls))
        for prop, domain in ontology_graph.subject_objects(RDFS.domain):
            if domain == cls:
                property_shape = URIRef(f"http://example.org/shapes#{prop.split('/')[-1]}Shape")
                shacl_graph.add((property_shape, RDF.type, SH.PropertyShape))
                shacl_graph.add((property_shape, SH.path, prop))
                shacl_graph.add((property_shape, SH.node, class_shape))
                shacl_graph.add((class_shape, SH.property, property_shape))
                range_ = ontology_graph.value(prop, RDFS.range)
                if range_:
                    if range_ == RDFS.Literal:
                        shacl_graph.add((property_shape, SH.datatype, XSD.string))  # Default to string
                    elif range_ in [XSD.string, XSD.date, XSD.decimal, XSD.integer, XSD.duration, XSD.gYear]:
                        shacl_graph.add((property_shape, SH.datatype, range_))
                    else:
                        shacl_graph.add(
                            (property_shape, SH["class"], range_)
                        )
    return shacl_graph

ontology_graph = Graph()
ontology_graph.parse("./result/inferred_ontology.ttl", format="turtle")
shacl_graph = ontology_to_shacl(ontology_graph)
shacl_graph.serialize("./result/shacl_graph.ttl", format="turtle")