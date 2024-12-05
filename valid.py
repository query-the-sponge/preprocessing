from pyshacl import validate
from rdflib import Graph

data_graph = Graph()
data_graph.parse("./result/output3.ttl", format="turtle")

shapes_graph = Graph()
shapes_graph.parse("shacl_graph.ttl", format="turtle")

conforms, report_graph, report_text = validate(
    data_graph=data_graph,
    shacl_graph=shapes_graph,
    inference="rdfs",
    debug=True,
)

if conforms:
    print("Validation passed: Data conforms to the ontology.")
else:
    print("Validation failed. See details below:")
    print(report_text)
