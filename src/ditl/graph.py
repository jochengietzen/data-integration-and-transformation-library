import json
from typing import TYPE_CHECKING, Any

import networkx as nx

if TYPE_CHECKING:
    from ditl.models.table import Table
    from ditl.transformation import Transformation


class Node:
    def __init__(self, data: dict[str, Any]):
        self._data = data

    def __hash__(self) -> int:
        return hash(self.data)

    def __eq__(self, value: object) -> bool:
        return hash(self) == hash(value)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.label}>"

    @property
    def data(self) -> str:
        return json.dumps(self._data, sort_keys=True)

    @property
    def label(self) -> str:
        return "_".join(["-".join(kv) for kv in self._data.items()])


class TransformationNode(Node):
    def __init__(self, transformation: "Transformation"):
        super().__init__({"name": transformation.name})
        self.transformation = transformation


class TableNode(Node):
    def __init__(self, table: "Table"):
        super().__init__({"path": table.path.model_dump_json()})
        self.table = table


# class Edge:
#     def __init__(self, from_: Node, to: Node) -> None:
#         self.from_ = from_
#         self.to = to


class Lineage:
    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def add_transformations(self, transformations: dict[str, "Transformation"]) -> "Lineage":
        for transformation in transformations.values():
            t = TransformationNode(transformation=transformation)
            output_node = TableNode(table=transformation.output_table_model)
            self.graph.add_edge(t, output_node, key=t.transformation.graph_label)
            for input_model in transformation.input_table_models.values():
                input_node = TableNode(table=input_model)
                self.graph.add_edge(input_node, t, key=t.transformation.graph_label)
        return self

    def draw(self, graph: nx.MultiDiGraph | None = None):
        import itertools as it

        import matplotlib.pyplot as plt

        g = self.graph if graph is None else graph

        for layer, nodes in enumerate(nx.topological_generations(g)):
            for node in nodes:
                g.nodes[node]["layer"] = layer
        pos = nx.multipartite_layout(g, subset_key="layer")
        fig, ax = plt.subplots()
        connectionstyle = [f"arc3,rad={r}" for r in it.accumulate([0.1] * 4)]
        nx.draw_networkx_nodes(g, pos=pos, ax=ax)
        print({node.label for node in g.nodes})
        labels = nx.draw_networkx_labels(g, pos=pos, ax=ax, labels={node: node.label for node in g.nodes})
        for _, label in labels.items():
            label.set_rotation(5)
        nx.draw_networkx_edges(g, pos=pos, ax=ax, connectionstyle=connectionstyle)

        fig.tight_layout()
        fig.set_figheight(15)
        fig.set_figwidth(30)
        plt.show()
