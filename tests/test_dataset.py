import random
import torch
import unittest
from torch_geometric.datasets import TUDataset, Planetoid
import copy
from copy import deepcopy
from deepsnap.graph import Graph
from deepsnap.hetero_graph import HeteroGraph
from deepsnap.dataset import GraphDataset, Generator, EnsembleGenerator
from tests.utils import (
    simple_networkx_graph,
    simple_networkx_graph_alphabet,
    simple_networkx_multigraph,
    generate_dense_hete_dataset,
    gen_graph,
)


class TestDataset(unittest.TestCase):

    def test_dataset_basic(self):
        G, x, y, edge_x, edge_y, edge_index, graph_x, graph_y = (
            simple_networkx_graph()
        )
        Graph.add_edge_attr(G, "edge_feature", edge_x)
        Graph.add_edge_attr(G, "edge_label", edge_y)
        Graph.add_node_attr(G, "node_feature", x)
        Graph.add_node_attr(G, "node_label", y)
        Graph.add_graph_attr(G, "graph_feature", graph_x)
        Graph.add_graph_attr(G, "graph_label", graph_y)
        H = deepcopy(G)
        graphs = GraphDataset.list_to_graphs([G, H])
        dataset = GraphDataset(graphs)
        self.assertEqual(len(dataset), 2)

    def test_dataset_property(self):
        G, x, y, edge_x, edge_y, edge_index, graph_x, graph_y = (
            simple_networkx_graph()
        )
        Graph.add_edge_attr(G, "edge_feature", edge_x)
        Graph.add_edge_attr(G, "edge_label", edge_y)
        Graph.add_node_attr(G, "node_feature", x)
        Graph.add_node_attr(G, "node_label", y)
        Graph.add_graph_attr(G, "graph_feature", graph_x)
        Graph.add_graph_attr(G, "graph_label", graph_y)
        H = G.copy()
        Graph.add_graph_attr(H, "graph_label", torch.tensor([1]))

        graphs = GraphDataset.list_to_graphs([G, H])
        dataset = GraphDataset(graphs)
        self.assertEqual(dataset.num_node_labels, 5)
        self.assertEqual(dataset.num_node_features, 2)
        self.assertEqual(dataset.num_edge_labels, 4)
        self.assertEqual(dataset.num_edge_features, 2)
        self.assertEqual(dataset.num_graph_labels, 2)
        self.assertEqual(dataset.num_graph_features, 2)
        self.assertEqual(dataset.num_labels, 5)  # node task
        dataset = GraphDataset(graphs, task="edge")
        self.assertEqual(dataset.num_labels, 4)
        dataset = GraphDataset(graphs, task="link_pred")
        self.assertEqual(dataset.num_labels, 4)
        dataset = GraphDataset(graphs, task="graph")
        self.assertEqual(dataset.num_labels, 2)

    def test_dataset_hetero_graph_split(self):
        G = generate_dense_hete_dataset()
        hete = HeteroGraph(G)
        # node
        dataset = GraphDataset([hete], task="node")
        split_res = dataset.split()
        for node_type in hete.node_label_index:
            num_nodes = int(len(hete.node_label_index[node_type]))
            num_nodes_reduced = num_nodes - 3
            node_0 = 1 + int(num_nodes_reduced * 0.8)
            node_1 = 1 + int(num_nodes_reduced * 0.1)
            node_2 = num_nodes - node_0 - node_1

            self.assertEqual(
                len(split_res[0][0].node_label_index[node_type]),
                node_0,
            )

            self.assertEqual(
                len(split_res[1][0].node_label_index[node_type]),
                node_1,
            )

            self.assertEqual(
                len(split_res[2][0].node_label_index[node_type]),
                node_2,
            )

        # node with specified split type
        dataset = GraphDataset([hete], task="node")
        node_split_types = ["n1"]
        split_res = dataset.split(split_types=node_split_types)
        for node_type in hete.node_label_index:
            if node_type in node_split_types:
                num_nodes = int(len(hete.node_label_index[node_type]))
                num_nodes_reduced = num_nodes - 3
                node_0 = 1 + int(num_nodes_reduced * 0.8)
                node_1 = 1 + int(num_nodes_reduced * 0.1)
                node_2 = num_nodes - node_0 - node_1
                self.assertEqual(
                    len(split_res[0][0].node_label_index[node_type]),
                    node_0,
                )

                self.assertEqual(
                    len(split_res[1][0].node_label_index[node_type]),
                    node_1,
                )

                self.assertEqual(
                    len(split_res[2][0].node_label_index[node_type]),
                    node_2,
                )
            else:
                num_nodes = int(len(hete.node_label_index[node_type]))
                self.assertEqual(
                    len(split_res[0][0].node_label_index[node_type]),
                    num_nodes,
                )

                self.assertEqual(
                    len(split_res[1][0].node_label_index[node_type]),
                    num_nodes,
                )

                self.assertEqual(
                    len(split_res[2][0].node_label_index[node_type]),
                    num_nodes,
                )

        # node with specified split type (string mode)
        dataset = GraphDataset([hete], task="node")
        node_split_types = "n1"
        split_res = dataset.split(split_types=node_split_types)
        for node_type in hete.node_label_index:
            if node_type in node_split_types:
                num_nodes = int(len(hete.node_label_index[node_type]))
                num_nodes_reduced = num_nodes - 3
                node_0 = 1 + int(num_nodes_reduced * 0.8)
                node_1 = 1 + int(num_nodes_reduced * 0.1)
                node_2 = num_nodes - node_0 - node_1
                self.assertEqual(
                    len(split_res[0][0].node_label_index[node_type]),
                    node_0,
                )

                self.assertEqual(
                    len(split_res[1][0].node_label_index[node_type]),
                    node_1,
                )

                self.assertEqual(
                    len(split_res[2][0].node_label_index[node_type]),
                    node_2,
                )
            else:
                num_nodes = int(len(hete.node_label_index[node_type]))
                self.assertEqual(
                    len(split_res[0][0].node_label_index[node_type]),
                    num_nodes,
                )

                self.assertEqual(
                    len(split_res[1][0].node_label_index[node_type]),
                    num_nodes,
                )

                self.assertEqual(
                    len(split_res[2][0].node_label_index[node_type]),
                    num_nodes,
                )

        # edge
        dataset = GraphDataset([hete], task="edge")
        split_res = dataset.split()
        for edge_type in hete.edge_label_index:
            num_edges = hete.edge_label_index[edge_type].shape[1]
            num_edges_reduced = num_edges - 3
            edge_0 = 1 + int(num_edges_reduced * 0.8)
            edge_1 = 1 + int(num_edges_reduced * 0.1)
            edge_2 = num_edges - edge_0 - edge_1
            self.assertEqual(
                split_res[0][0].edge_label_index[edge_type].shape[1],
                edge_0,
            )

            self.assertEqual(
                split_res[1][0].edge_label_index[edge_type].shape[1],
                edge_1,
            )

            self.assertEqual(
                split_res[2][0].edge_label_index[edge_type].shape[1],
                edge_2,
            )

        # edge with specified split type
        dataset = GraphDataset([hete], task="edge")
        edge_split_types = [("n1", "e1", "n1"), ("n1", "e2", "n2")]
        split_res = dataset.split(split_types=edge_split_types)
        for edge_type in hete.edge_label_index:
            if edge_type in edge_split_types:
                num_edges = hete.edge_label_index[edge_type].shape[1]
                num_edges_reduced = num_edges - 3
                edge_0 = 1 + int(num_edges_reduced * 0.8)
                edge_1 = 1 + int(num_edges_reduced * 0.1)
                edge_2 = num_edges - edge_0 - edge_1
                self.assertEqual(
                    split_res[0][0].edge_label_index[edge_type].shape[1],
                    edge_0,
                )

                self.assertEqual(
                    split_res[1][0].edge_label_index[edge_type].shape[1],
                    edge_1,
                )

                self.assertEqual(
                    split_res[2][0].edge_label_index[edge_type].shape[1],
                    edge_2,
                )
            else:
                num_edges = hete.edge_label_index[edge_type].shape[1]
                self.assertEqual(
                    split_res[0][0].edge_label_index[edge_type].shape[1],
                    num_edges,
                )

                self.assertEqual(
                    split_res[1][0].edge_label_index[edge_type].shape[1],
                    num_edges,
                )

                self.assertEqual(
                    split_res[2][0].edge_label_index[edge_type].shape[1],
                    num_edges,
                )

        # link_pred
        dataset = GraphDataset([hete], task="link_pred")
        split_res = dataset.split(transductive=True)
        for edge_type in hete.edge_label_index:
            num_edges = hete.edge_label_index[edge_type].shape[1]
            num_edges_reduced = num_edges - 3
            self.assertEqual(
                split_res[0][0].edge_label_index[edge_type].shape[1],
                2 * (1 + int(0.8 * (num_edges_reduced)))
            )
            self.assertEqual(
                split_res[1][0].edge_label_index[edge_type].shape[1],
                2 * (1 + (int(0.1 * (num_edges_reduced))))
            )
            self.assertEqual(
                split_res[2][0].edge_label_index[edge_type].shape[1],
                2
                * num_edges
                - 2
                * (
                    2
                    + int(0.1 * num_edges_reduced)
                    + int(0.8 * num_edges_reduced)
                )
            )

        # link_pred with specified split type
        dataset = GraphDataset([hete], task="link_pred")
        link_split_types = [("n1", "e1", "n1"), ("n1", "e2", "n2")]
        split_res = dataset.split(
            transductive=True,
            split_types=link_split_types
        )

        for edge_type in hete.edge_label_index:
            if edge_type in link_split_types:
                num_edges = hete.edge_label_index[edge_type].shape[1]
                num_edges_reduced = num_edges - 3
                self.assertEqual(
                    split_res[0][0].edge_label_index[edge_type].shape[1],
                    2 * (1 + int(0.8 * (num_edges_reduced)))
                )
                self.assertEqual(
                    split_res[1][0].edge_label_index[edge_type].shape[1],
                    2 * (1 + (int(0.1 * (num_edges_reduced))))
                )
                self.assertEqual(
                    split_res[2][0].edge_label_index[edge_type].shape[1],
                    2
                    * num_edges
                    - 2
                    * (
                        2
                        + int(0.1 * num_edges_reduced)
                        + int(0.8 * num_edges_reduced)
                    )
                )
            else:
                num_edges = hete.edge_label_index[edge_type].shape[1]
                self.assertEqual(
                    split_res[0][0].edge_label_index[edge_type].shape[1],
                    1 * (0 + int(1.0 * (num_edges))),
                )
                self.assertEqual(
                    split_res[1][0].edge_label_index[edge_type].shape[1],
                    1 * (0 + (int(1.0 * (num_edges)))),
                )
                self.assertEqual(
                    split_res[2][0].edge_label_index[edge_type].shape[1],
                    1 * (0 + (int(1.0 * (num_edges)))),
                )

        # link_pred + disjoint
        dataset = GraphDataset(
            [hete],
            task="link_pred",
            edge_train_mode="disjoint",
            edge_message_ratio=0.5,
        )
        split_res = dataset.split(
            transductive=True,
            split_ratio=[0.6, 0.2, 0.2],
        )
        for edge_type in hete.edge_label_index:
            num_edges = hete.edge_label_index[edge_type].shape[1]
            num_edges_reduced = num_edges - 3
            edge_0 = 1 + int(0.6 * num_edges_reduced)
            edge_0 = 2 * (edge_0 - (1 + int(0.5 * (edge_0 - 2))))

            self.assertEqual(
                split_res[0][0].edge_label_index[edge_type].shape[1],
                edge_0,
            )
            edge_1 = 2 * (1 + int(0.2 * num_edges_reduced))
            self.assertEqual(
                split_res[1][0].edge_label_index[edge_type].shape[1],
                edge_1,
            )
            edge_2 = (
                2
                * int(num_edges)
                - 2
                * (1 + int(0.6 * num_edges_reduced))
                - edge_1
            )
            self.assertEqual(
                split_res[2][0].edge_label_index[edge_type].shape[1],
                edge_2,
            )

        # link pred with edge_split_mode set to "exact"
        dataset = GraphDataset(
            [hete],
            task="link_pred",
            edge_split_mode="approximate"
        )
        split_res = dataset.split(transductive=True)
        hete_link_train_edge_num = 0
        hete_link_test_edge_num = 0
        hete_link_val_edge_num = 0
        num_edges = 0
        for edge_type in hete.edge_label_index:
            num_edges += hete.edge_label_index[edge_type].shape[1]
            if edge_type in split_res[0][0].edge_label_index:
                hete_link_train_edge_num += (
                    split_res[0][0].edge_label_index[edge_type].shape[1]
                )
            if edge_type in split_res[1][0].edge_label_index:
                hete_link_test_edge_num += (
                    split_res[1][0].edge_label_index[edge_type].shape[1]
                )
            if edge_type in split_res[2][0].edge_label_index:
                hete_link_val_edge_num += (
                    split_res[2][0].edge_label_index[edge_type].shape[1]
                )

        num_edges_reduced = num_edges - 3
        self.assertEqual(
            hete_link_train_edge_num,
            2 * (1 + int(0.8 * (num_edges_reduced)))
        )
        self.assertEqual(
            hete_link_test_edge_num,
            2 * (1 + (int(0.1 * (num_edges_reduced))))
        )
        self.assertEqual(
            hete_link_val_edge_num,
            2
            * num_edges
            - 2
            * (
                2
                + int(0.1 * num_edges_reduced)
                + int(0.8 * num_edges_reduced)
            )
        )

        # link pred with specified types and edge_split_mode set to "exact"
        dataset = GraphDataset(
            [hete],
            task="link_pred",
            edge_split_mode="approximate",
        )
        link_split_types = [("n1", "e1", "n1"), ("n1", "e2", "n2")]
        split_res = dataset.split(
            transductive=True,
            split_types=link_split_types,
        )
        hete_link_train_edge_num = 0
        hete_link_test_edge_num = 0
        hete_link_val_edge_num = 0

        num_split_type_edges = 0
        num_non_split_type_edges = 0
        for edge_type in hete.edge_label_index:
            if edge_type in link_split_types:
                num_split_type_edges += (
                    hete.edge_label_index[edge_type].shape[1]
                )
            else:
                num_non_split_type_edges += (
                    hete.edge_label_index[edge_type].shape[1]
                )
            if edge_type in split_res[0][0].edge_label_index:
                hete_link_train_edge_num += (
                    split_res[0][0].edge_label_index[edge_type].shape[1]
                )
            if edge_type in split_res[1][0].edge_label_index:
                hete_link_test_edge_num += (
                    split_res[1][0].edge_label_index[edge_type].shape[1]
                )
            if edge_type in split_res[2][0].edge_label_index:
                hete_link_val_edge_num += (
                    split_res[2][0].edge_label_index[edge_type].shape[1]
                )

        num_edges_reduced = num_split_type_edges - 3
        edge_0 = (
            2 * (1 + int(0.8 * (num_edges_reduced))) + num_non_split_type_edges
        )
        edge_1 = (
            2 * (1 + int(0.1 * (num_edges_reduced))) + num_non_split_type_edges
        )
        edge_2 = (
            2
            * num_split_type_edges
            - 2
            * (
                2
                + int(0.1 * num_edges_reduced)
                + int(0.8 * num_edges_reduced)
            )
            + num_non_split_type_edges
        )

        self.assertEqual(hete_link_train_edge_num, edge_0)
        self.assertEqual(hete_link_test_edge_num, edge_1)
        self.assertEqual(hete_link_val_edge_num, edge_2)

    def test_dataset_split(self):
        # inductively split with graph task
        pyg_dataset = TUDataset("./enzymes", "ENZYMES")
        graphs = GraphDataset.pyg_to_graphs(pyg_dataset)
        dataset = GraphDataset(graphs, task="graph")
        split_res = dataset.split(transductive=False)
        num_graphs = len(dataset)
        num_graphs_reduced = num_graphs - 3
        num_train = 1 + int(num_graphs_reduced * 0.8)
        num_val = 1 + int(num_graphs_reduced * 0.1)
        num_test = num_graphs - num_train - num_val
        self.assertEqual(num_train, len(split_res[0]))
        self.assertEqual(num_val, len(split_res[1]))
        self.assertEqual(num_test, len(split_res[2]))

        # inductively split with link_pred task
        # and default (`all`) edge_train_mode
        pyg_dataset = TUDataset("./enzymes", "ENZYMES")
        graphs = GraphDataset.pyg_to_graphs(pyg_dataset)
        dataset = GraphDataset(graphs, task="link_pred")
        split_res = dataset.split(transductive=False)
        num_graphs = len(dataset)
        num_graphs_reduced = num_graphs - 3
        num_train = 1 + int(num_graphs_reduced * 0.8)
        num_val = 1 + int(num_graphs_reduced * 0.1)
        num_test = num_graphs - num_train - num_val
        self.assertEqual(num_train, len(split_res[0]))
        self.assertEqual(num_val, len(split_res[1]))
        self.assertEqual(num_test, len(split_res[2]))

        # inductively split with link_pred task and `disjoint` edge_train_mode
        pyg_dataset = TUDataset("./enzymes", "ENZYMES")
        graphs = GraphDataset.pyg_to_graphs(pyg_dataset)
        dataset = GraphDataset(
            graphs,
            task="link_pred",
            edge_train_mode="disjoint",
        )
        split_res = dataset.split(transductive=False)
        num_graphs = len(dataset)
        num_graphs_reduced = num_graphs - 3
        num_train = 1 + int(num_graphs_reduced * 0.8)
        num_val = 1 + int(num_graphs_reduced * 0.1)
        num_test = num_graphs - num_train - num_val
        self.assertEqual(num_train, len(split_res[0]))
        self.assertEqual(num_val, len(split_res[1]))
        self.assertEqual(num_test, len(split_res[2]))

        # transductively split with node task
        pyg_dataset = Planetoid("./cora", "Cora")
        graphs = GraphDataset.pyg_to_graphs(pyg_dataset)
        dataset = GraphDataset(graphs, task="node")
        num_nodes = dataset.num_nodes[0]
        num_nodes_reduced = num_nodes - 3
        num_edges = dataset.num_edges[0]
        num_edges_reduced = num_edges - 3
        split_res = dataset.split()
        self.assertEqual(
            len(split_res[0][0].node_label_index),
            1 + int(0.8 * num_nodes_reduced)
        )
        self.assertEqual(
            len(split_res[1][0].node_label_index),
            1 + int(0.1 * num_nodes_reduced)
        )
        self.assertEqual(
            len(split_res[2][0].node_label_index),
            num_nodes
            - 2
            - int(0.8 * num_nodes_reduced)
            - int(0.1 * num_nodes_reduced)
        )

        # transductively split with edge task
        dataset = GraphDataset(graphs, task="edge")
        split_res = dataset.split()
        edge_0 = 2 * (1 + int(0.8 * (num_edges_reduced)))
        self.assertEqual(
            split_res[0][0].edge_label_index.shape[1],
            edge_0,
        )
        edge_1 = 2 * (1 + int(0.1 * (num_edges_reduced)))
        self.assertEqual(
            split_res[1][0].edge_label_index.shape[1],
            edge_1,
        )
        self.assertEqual(
            split_res[2][0].edge_label_index.shape[1],
            2 * num_edges - edge_0 - edge_1,
        )

        # transductively split with link_pred task
        # and default (`all`) edge_train_mode
        dataset = GraphDataset(graphs, task="link_pred")
        split_res = dataset.split()
        self.assertEqual(
            split_res[0][0].edge_label_index.shape[1],
            2 * 2 * (1 + int(0.8 * (num_edges_reduced)))
        )
        self.assertEqual(
            split_res[1][0].edge_label_index.shape[1],
            2
            * 2 * (1 + (int(0.1 * (num_edges_reduced))))
        )
        self.assertEqual(
            split_res[2][0].edge_label_index.shape[1],
            2
            * 2
            * num_edges
            - 2
            * 2
            * (
                2
                + int(0.1 * num_edges_reduced)
                + int(0.8 * num_edges_reduced)
            )
        )

        # transductively split with link_pred task, `split` edge_train_mode
        # and 0.5 edge_message_ratio
        dataset = GraphDataset(
            graphs,
            task="link_pred",
            edge_train_mode="disjoint",
            edge_message_ratio=0.5,
        )
        split_res = dataset.split()
        edge_0 = 2 * (1 + int(0.8 * num_edges_reduced))
        edge_0 = 2 * (edge_0 - (1 + int(0.5 * (edge_0 - 3))))
        self.assertEqual(
            split_res[0][0].edge_label_index.shape[1],
            edge_0,
        )
        edge_1 = 2 * 2 * (1 + int(0.1 * num_edges_reduced))
        self.assertEqual(split_res[1][0].edge_label_index.shape[1], edge_1)
        edge_2 = (
            2
            * 2
            * int(num_edges)
            - 2
            * 2 * (1 + int(0.8 * num_edges_reduced))
            - edge_1
        )

        self.assertEqual(split_res[2][0].edge_label_index.shape[1], edge_2)

        # transductively split with link_pred task
        # and specified edge_negative_sampling_ratio
        dataset = GraphDataset(
            graphs,
            task="link_pred",
            edge_negative_sampling_ratio=2
        )
        split_res = dataset.split()
        edge_0 = (2 + 1) * (2 * (1 + int(0.8 * num_edges_reduced)))
        self.assertEqual(split_res[0][0].edge_label_index.shape[1], edge_0)
        edge_1 = (2 + 1) * 2 * (1 + int(0.1 * num_edges_reduced))
        self.assertEqual(split_res[1][0].edge_label_index.shape[1], edge_1)
        edge_2 = (2 + 1) * 2 * int(num_edges) - edge_0 - edge_1
        self.assertEqual(split_res[2][0].edge_label_index.shape[1], edge_2)

    def test_dataset_split_custom(self):
        # transductive split with node task (self defined dataset)
        G, x, y, edge_x, edge_y, edge_index, graph_x, graph_y = (
            simple_networkx_graph_alphabet()
        )
        Graph.add_edge_attr(G, "edge_feature", edge_x)
        Graph.add_edge_attr(G, "edge_label", edge_y)
        Graph.add_node_attr(G, "node_feature", x)
        Graph.add_node_attr(G, "node_label", y)
        Graph.add_graph_attr(G, "graph_feature", graph_x)
        Graph.add_graph_attr(G, "graph_label", graph_y)

        num_nodes = len(list(G.nodes))
        nodes_train = list(G.nodes)[: int(0.3 * num_nodes)]
        nodes_val = list(G.nodes)[int(0.3 * num_nodes): int(0.6 * num_nodes)]
        nodes_test = list(G.nodes)[int(0.6 * num_nodes): ]
        graph = Graph(
            G,
            custom_splits=[
                nodes_train,
                nodes_val,
                nodes_test
            ],
            task="node"
        )
        graphs = [graph]
        dataset = GraphDataset(
            graphs, task="node", general_split_mode="custom",
        )

        split_res = dataset.split(transductive=True)
        self.assertEqual(
            split_res[0][0].node_label_index,
            list(range(int(0.3 * num_nodes)))
        )
        self.assertEqual(
            split_res[1][0].node_label_index,
            list(range(int(0.3 * num_nodes), int(0.6 * num_nodes)))
        )
        self.assertEqual(
            split_res[2][0].node_label_index,
            list(range(int(0.6 * num_nodes), num_nodes))
        )

        # transductive split with link_pred task (disjoint mode) (self defined dataset)
        edges = list(G.edges)
        num_edges = len(edges)
        edges_train = edges[: int(0.3 * num_edges)]
        edges_train_disjoint = edges[: int(0.5 * 0.3 * num_edges)]
        edges_val = edges[int(0.3 * num_edges): int(0.6 * num_edges)]
        edges_test = edges[int(0.6 * num_edges):]
        link_size_list = [len(edges_train_disjoint), len(edges_val), len(edges_test)]
        graph = Graph(
            G,
            custom_splits=[
                edges_train,
                edges_val,
                edges_test
            ],
            custom_disjoint_split=edges_train_disjoint,
            task="link_pred"
        )

        graphs = [graph]

        dataset = GraphDataset(
            graphs,
            task="link_pred",
            edge_train_mode="disjoint",
            general_split_mode="custom",
            disjoint_split_mode="custom",
        )

        split_res = dataset.split(transductive=True)
        self.assertEqual(
            split_res[0][0].edge_label_index.shape[1],
            2 * link_size_list[0]
        )
        self.assertEqual(
            split_res[1][0].edge_label_index.shape[1],
            2 * link_size_list[1]
        )
        self.assertEqual(
            split_res[2][0].edge_label_index.shape[1],
            2 * link_size_list[2]
        )

        # transductive split with link_pred task (disjoint mode) (self defined disjoint data)
        edges = list(G.edges)
        num_edges = len(edges)
        edges_train = edges[: int(0.7 * num_edges)]
        edges_train_disjoint = edges[: int(0.5 * 0.7 * num_edges)]
        edges_val = edges[int(0.7 * num_edges):]
        link_size_list = [len(edges_train_disjoint), len(edges_val)]

        graph = Graph(
            G,
            custom_splits=[
                edges_train,
                edges_val,
            ],
            custom_disjoint_split=edges_train_disjoint,
            task="link_pred"
        )

        graphs = [graph]

        dataset = GraphDataset(
            graphs,
            task="link_pred",
            edge_train_mode="disjoint",
            general_split_mode="custom",
            disjoint_split_mode="custom",
        )

        split_res = dataset.split(transductive=True)

        self.assertEqual(
            split_res[0][0].edge_label_index.shape[1],
            2 * link_size_list[0]
        )
        self.assertEqual(
            split_res[1][0].edge_label_index.shape[1],
            2 * link_size_list[1]
        )

        # transductive split with link_pred task (disjoint mode) (self defined disjoint data) (multigraph) (train/val split)
        G, x, y, edge_x, edge_y, edge_index, graph_x, graph_y = (
            simple_networkx_multigraph()
        )
        Graph.add_edge_attr(G, "edge_feature", edge_x)
        Graph.add_edge_attr(G, "edge_label", edge_y)
        Graph.add_node_attr(G, "node_feature", x)
        Graph.add_node_attr(G, "node_label", y)
        Graph.add_graph_attr(G, "graph_feature", graph_x)
        Graph.add_graph_attr(G, "graph_label", graph_y)
        edges = list(G.edges)
        num_edges = len(edges)
        edges_train = edges[: int(0.6 * num_edges)]
        edges_train_disjoint = edges[: int(0.6 * 0.2 * num_edges)]
        edges_val = edges[int(0.6 * num_edges):]
        link_size_list = [len(edges_train_disjoint), len(edges_val)]

        graph = Graph(
            G,
            custom_splits=[
                edges_train,
                edges_val,
            ],
            custom_disjoint_split=edges_train_disjoint,
            task="link_pred"
        )

        graphs = [graph]

        dataset = GraphDataset(
            graphs,
            task="link_pred",
            edge_train_mode="disjoint",
            general_split_mode="custom",
            disjoint_split_mode="custom",
        )

        split_res = dataset.split(transductive=True)

        self.assertEqual(
            split_res[0][0].edge_label_index.shape[1],
            2 * link_size_list[0]
        )
        self.assertEqual(
            split_res[1][0].edge_label_index.shape[1],
            2 * link_size_list[1]
        )

        # transductive split with link_pred task (disjoint mode) (self defined disjoint data) (multigraph) (train/val/test split)
        G, x, y, edge_x, edge_y, edge_index, graph_x, graph_y = (
            simple_networkx_multigraph()
        )
        Graph.add_edge_attr(G, "edge_feature", edge_x)
        Graph.add_edge_attr(G, "edge_label", edge_y)
        Graph.add_node_attr(G, "node_feature", x)
        Graph.add_node_attr(G, "node_label", y)
        Graph.add_graph_attr(G, "graph_feature", graph_x)
        Graph.add_graph_attr(G, "graph_label", graph_y)

        edges = list(G.edges)
        num_edges = len(edges)
        edges_train = edges[: int(0.6 * num_edges)]
        edges_train_disjoint = edges[: int(0.6 * 0.2 * num_edges)]
        edges_val = edges[int(0.6 * num_edges):int(0.8 * num_edges)]
        edges_test = edges[int(0.8 * num_edges):]
        link_size_list = [len(edges_train_disjoint), len(edges_val), len(edges_test)]

        graph = Graph(
            G,
            custom_splits=[
                edges_train,
                edges_val,
                edges_test,
            ],
            custom_disjoint_split=edges_train_disjoint,
            task="link_pred"
        )

        graphs = [graph]

        dataset = GraphDataset(
            graphs,
            task="link_pred",
            edge_train_mode="disjoint",
            general_split_mode="custom",
            disjoint_split_mode="custom",
        )

        split_res = dataset.split(transductive=True)

        self.assertEqual(
            split_res[0][0].edge_label_index.shape[1],
            2 * link_size_list[0]
        )
        self.assertEqual(
            split_res[1][0].edge_label_index.shape[1],
            2 * link_size_list[1]
        )
        self.assertEqual(
            split_res[2][0].edge_label_index.shape[1],
            2 * link_size_list[2]
        )

        # transductive split with node task (pytorch geometric dataset)
        pyg_dataset = Planetoid("./cora", "Cora")
        graphs = GraphDataset.pyg_to_graphs(pyg_dataset)
        split_ratio = [0.3, 0.3, 0.4]
        
        node_size_list = [0 for i in range(len(split_ratio))]
        for graph in graphs:
            custom_splits = [[] for i in range(len(split_ratio))]
            split_offset = 0
            shuffled_node_indices = torch.randperm(graph.num_nodes)
            for i, split_ratio_i in enumerate(split_ratio):
                if i != len(split_ratio) - 1:
                    num_split_i = (
                        1 +
                        int(
                            split_ratio_i *
                            (graph.num_nodes - len(split_ratio))
                        )
                    )
                    nodes_split_i = (
                        shuffled_node_indices[split_offset: split_offset + num_split_i]
                    )
                    split_offset += num_split_i
                else:
                    nodes_split_i = shuffled_node_indices[split_offset:]

                custom_splits[i] = nodes_split_i
                node_size_list[i] += len(nodes_split_i)
            graph.custom_splits = custom_splits

        dataset = GraphDataset(
            graphs, task="node", general_split_mode="custom",
        )

        split_res = dataset.split(transductive=True)
        self.assertEqual(
            len(split_res[0][0].node_label_index),
            node_size_list[0]
        )
        self.assertEqual(
            len(split_res[1][0].node_label_index),
            node_size_list[1]
        )
        self.assertEqual(
            len(split_res[2][0].node_label_index),
            node_size_list[2]
        )

        # transductive split with edge task
        pyg_dataset = Planetoid("./cora", "Cora")
        graphs = GraphDataset.pyg_to_graphs(pyg_dataset)
        split_ratio = [0.3, 0.3, 0.4]
        edge_size_list = [0 for i in range(len(split_ratio))]
        for graph in graphs:
            custom_splits = [[] for i in range(len(split_ratio))]
            split_offset = 0
            edges = list(graph.G.edges)
            random.shuffle(edges)
            for i, split_ratio_i in enumerate(split_ratio):
                if i != len(split_ratio) - 1:
                    num_split_i = (
                        1 +
                        int(
                            split_ratio_i
                            * (graph.num_edges - len(split_ratio))
                        )
                    )
                    edges_split_i = (
                        edges[split_offset: split_offset + num_split_i]
                    )
                    split_offset += num_split_i
                else:
                    edges_split_i = edges[split_offset:]

                custom_splits[i] = edges_split_i
                edge_size_list[i] += len(edges_split_i)
            graph.custom_splits = custom_splits

        dataset = GraphDataset(
            graphs, task="edge", general_split_mode="custom",
        )
        split_res = dataset.split(transductive=True)
        self.assertEqual(
            split_res[0][0].edge_label_index.shape[1],
            2 * edge_size_list[0]
        )
        self.assertEqual(
            split_res[1][0].edge_label_index.shape[1],
            2 * edge_size_list[1]
        )
        self.assertEqual(
            split_res[2][0].edge_label_index.shape[1],
            2 * edge_size_list[2]
        )

        # transductive split with link_pred task
        pyg_dataset = Planetoid("./cora", "Cora")
        graphs = GraphDataset.pyg_to_graphs(pyg_dataset)
        split_ratio = [0.3, 0.3, 0.4]
        link_size_list = [0 for i in range(len(split_ratio))]

        for graph in graphs:
            split_offset = 0
            edges = list(graph.G.edges)
            random.shuffle(edges)
            num_edges_train = 1 + int(split_ratio[0] * (graph.num_edges - 3))
            num_edges_val = 1 + int(split_ratio[0] * (graph.num_edges - 3))
            edges_train = edges[:num_edges_train]
            edges_val = edges[num_edges_train:num_edges_train + num_edges_val]
            edges_test = edges[num_edges_train + num_edges_val:]

            custom_splits = [
                edges_train,
                edges_val,
                edges_test,
            ]
            graph.custom_splits = custom_splits

            link_size_list[0] += len(edges_train)
            link_size_list[1] += len(edges_val)
            link_size_list[2] += len(edges_test)

        dataset = GraphDataset(
            graphs, task="link_pred", general_split_mode="custom",
        )
        split_res = dataset.split(transductive=True)
        self.assertEqual(
            split_res[0][0].edge_label_index.shape[1],
            2 * 2 * link_size_list[0]
        )
        self.assertEqual(
            split_res[1][0].edge_label_index.shape[1],
            2 * 2 * link_size_list[1]
        )
        self.assertEqual(
            split_res[2][0].edge_label_index.shape[1],
            2 * 2 * link_size_list[2]
        )

        # inductive split with graph task
        pyg_dataset = TUDataset("./enzymes", "ENZYMES")
        graphs = GraphDataset.pyg_to_graphs(pyg_dataset)
        num_graphs = len(graphs)
        split_ratio = [0.3, 0.3, 0.4]
        graph_size_list = []
        split_offset = 0
        custom_split_graphs = []
        for i, split_ratio_i in enumerate(split_ratio):
            if i != len(split_ratio) - 1:
                num_split_i = (
                    1 +
                    int(split_ratio_i * (num_graphs - len(split_ratio)))
                )
                custom_split_graphs.append(
                    graphs[split_offset: split_offset + num_split_i]
                )
                split_offset += num_split_i
                graph_size_list.append(num_split_i)
            else:
                custom_split_graphs.append(graphs[split_offset:])
                graph_size_list.append(len(graphs[split_offset:]))
        dataset = GraphDataset(
            graphs, task="graph", general_split_mode="custom",
            custom_split_graphs=custom_split_graphs,
        )
        split_res = dataset.split(transductive=False)
        self.assertEqual(graph_size_list[0], len(split_res[0]))
        self.assertEqual(graph_size_list[1], len(split_res[1]))
        self.assertEqual(graph_size_list[2], len(split_res[2]))

        # transductive split with link_pred task in `disjoint` edge_train_mode.
        pyg_dataset = Planetoid("./cora", "Cora")
        graphs = GraphDataset.pyg_to_graphs(pyg_dataset)
        split_ratio = [0.3, 0.3, 0.4]
        link_size_list = [0 for i in range(len(split_ratio))]

        for graph in graphs:
            split_offset = 0
            edges = list(graph.G.edges)
            random.shuffle(edges)
            num_edges_train = 1 + int(split_ratio[0] * (graph.num_edges - 3))
            num_edges_train_disjoint = (
                1 + int(split_ratio[0] * 0.5 * (graph.num_edges - 3))
            )
            num_edges_val = 1 + int(split_ratio[0] * (graph.num_edges - 3))

            edges_train = edges[:num_edges_train]
            edges_train_disjoint = edges[:num_edges_train_disjoint]
            edges_val = edges[num_edges_train:num_edges_train + num_edges_val]
            edges_test = edges[num_edges_train + num_edges_val:]

            custom_splits = [
                edges_train,
                edges_val,
                edges_test,
            ]
            graph.custom_splits = custom_splits
            graph.custom_disjoint_split = edges_train_disjoint

            link_size_list[0] += len(edges_train_disjoint)
            link_size_list[1] += len(edges_val)
            link_size_list[2] += len(edges_test)

        dataset = GraphDataset(
            graphs,
            task="link_pred",
            edge_train_mode="disjoint",
            general_split_mode="custom",
            disjoint_split_mode="custom",
        )
        split_res = dataset.split(transductive=True)
        self.assertEqual(
            split_res[0][0].edge_label_index.shape[1],
            2 * 2 * link_size_list[0]
        )
        self.assertEqual(
            split_res[1][0].edge_label_index.shape[1],
            2 * 2 * link_size_list[1]
        )
        self.assertEqual(
            split_res[2][0].edge_label_index.shape[1],
            2 * 2 * link_size_list[2]
        )

        # TODO: test for transductive split w/ hetero graph
        # TODO: test for inductive split w/ hetero graph

    def test_generator(self):
        pyg_dataset = Planetoid("./cora", "Cora")
        dg = Graph.pyg_to_graph(pyg_dataset[0])

        num_nodes = 500
        sizes = [2, 3]

        class NeighborGenerator(Generator):
            def __len__(self):
                return sizes

            def generate(self):
                graph = Graph(gen_graph(num_nodes, dg.G))
                return graph

        dataset = GraphDataset(None, generator=NeighborGenerator(sizes))
        self.assertTrue(dataset[0].node_feature.shape[0] == num_nodes)

    def test_ensemble_generator(self):
        pyg_dataset = Planetoid("./cora", "Cora")
        dg = Graph.pyg_to_graph(pyg_dataset[0])

        num_nodes = 500
        sizes = [2, 3]

        class NeighborGenerator1(Generator):
            def __len__(self):
                return sizes

            def generate(self):
                graph = Graph(gen_graph(num_nodes, dg.G))
                return graph

        class NeighborGenerator2(Generator):
            def __len__(self):
                return sizes

            def generate(self):
                graph = Graph(gen_graph(num_nodes, dg.G))
                return graph

        ensemble_generator = (
            EnsembleGenerator(
                [
                    NeighborGenerator1(sizes),
                    NeighborGenerator2(sizes),
                ]
            )
        )
        dataset = GraphDataset(None, generator=ensemble_generator)
        self.assertTrue(dataset[0].node_feature.shape[0] == num_nodes)

    def test_filter(self):
        pyg_dataset = TUDataset("./enzymes", "ENZYMES")
        graphs = GraphDataset.pyg_to_graphs(pyg_dataset)
        dataset = GraphDataset(graphs, task="graph")
        thresh = 90

        orig_dataset_size = len(dataset)
        num_graphs_large = 0
        for graph in dataset:
            if len(graph.G) >= thresh:
                num_graphs_large += 1

        dataset = dataset.filter(
            lambda graph: len(graph.G) < thresh, deep_copy=False
        )
        filtered_dataset_size = len(dataset)

        self.assertEqual(
            orig_dataset_size - filtered_dataset_size,
            num_graphs_large,
        )


if __name__ == "__main__":
    unittest.main()
