# SaveDatabaseJSON.py
# Marcio Gameiro
# 2020-09-09
# MIT LICENSE

import DSGRN
import pychomp
import json

def dsgrn_cell_to_cc_cell_map(network):
    # Return a mapping from the top dimensional cells
    # in the DSGRN complex to the top dimensional
    # cells in the pychomp cubical complex.
    #
    # Construct a cubical complex using pychomp. A cubical complex in pychomp
    # does not contain the rightmost boundary, so make one extra layer of
    # cubes and ignore the last layer (called rightfringe in pychomp).
    cubical_complex = pychomp.CubicalComplex([x + 1 for x in network.domains()])
    dimension = network.size()
    # Mapping from DSGRN top cells to cc top cells
    cell2cc_cell = {}
    # DSGRN only uses the top dimensional cells to
    # construct the state transiton graph and the
    # corresponding morse sets and these cells are
    # indexed from 0 to n-1, where n is the number
    # of top dimensional cells. Hence we can get a
    # mapping by counting the cells in the cc.
    dsgrn_index = 0
    for cell_index in cubical_complex(dimension):
        # Ignore fringe cells
        if cubical_complex.rightfringe(cell_index):
            continue
        cell2cc_cell[dsgrn_index] = cell_index
        dsgrn_index += 1
    return cell2cc_cell

def network_json(network):
    # Return json data for network
    nodes = [] # Get network nodes
    for d in range(network.size()):
        node = {"id" : network.name(d)}
        nodes.append(node)
    # Get network edges
    edges = [(u, v) for u in range(network.size()) for v in network.outputs(u)]
    links = []
    for (u, v) in edges:
        if network.model() == 'ecology':
            # Always repressing for ecology model
            edge_type = -1
        else:
            edge_type = 1 if network.interaction(u, v) else -1
        link = {"source" : network.name(u),
                "target" : network.name(v),
                "type": edge_type}
        links.append(link)
    network_json_data = {"network" : {"nodes" : nodes, "links" : links}}
    return network_json_data

def parameter_graph_json(parameter_graph, vertices=None):
    # Return json data for parameter graph
    # Get list of vertices if none
    if vertices == None:
        vertices = list(range(parameter_graph.size()))
    all_edges = [(u, v) for u in vertices for v in parameter_graph.adjacencies(u) if v in vertices]
    # Remove double edges (all edges are double)
    edges = [(u, v) for (u, v) in all_edges if u > v]
    nodes = []
    for v in vertices:
        node = {"id" : v}
        # node = {"id" : str(v)}
        nodes.append(node)
    links = []
    for (u, v) in edges:
        link = {"source" : u, "target" : v}
        # link = {"source" : str(u), "target" : str(v)}
        links.append(link)
    parameter_graph_json_data = {"parameter_graph" : {"nodes" : nodes, "links" : links}}
    return parameter_graph_json_data

def cubical_complex_json(network):
    # Return json data for cubical complex
    # Get complex dimension
    dimension = network.size()
    # Construct a cubical complex using pychomp. A cubical complex in pychomp
    # does not contain the rightmost boundary, so make one extra layer of
    # cubes and ignore the last layer (called rightfringe in pychomp).
    cubical_complex = pychomp.CubicalComplex([x + 1 for x in network.domains()])
    # Get vertices coordinates and set a
    # mapping from coords to its index in
    # the list of coordinates.
    verts_coords = []
    coords2idx = {}
    # Get the coords of all cells of dimension 0.
    # The 0-dim cells in a cubical complex in pychomp
    # are indexed from 0 to n-1, where n is the number
    # of 0-dim cells. Hence the cell_index coincides
    # with the index of coords in the list verts_coords.
    for cell_index in cubical_complex(0):
        coords = cubical_complex.coordinates(cell_index)
        coords2idx[tuple(coords)] = cell_index
        verts_coords.append(coords)
    cells = [] # Get the cell complex data
    for cell_index in cubical_complex:
        # Ignore fringe cells
        if cubical_complex.rightfringe(cell_index):
            continue
        # Get this cell dimension
        cell_dim = cubical_complex.cell_dim(cell_index)
        # Get coords of the lower corner of the box
        coords_lower = cubical_complex.coordinates(cell_index)
        # Get index of vertex corresponding to these coords
        # Due to the way pychomp index the 0-dim cells we get
        # that idx_lower == cell_index (see coords2idx above).
        idx_lower = coords2idx[tuple(coords_lower)]
        # Get the shape of this cell (see pychomp)
        shape = cubical_complex.cell_shape(cell_index)
        # Add 1 to the appropriate entries to get coords of the upper corner
        coords_upper = [coords_lower[d] + (1 if shape & (1 << d) != 0 else 0) for d in range(dimension)]
        # Get index of vertex corresponding to these coords
        idx_upper = coords2idx[tuple(coords_upper)]
        if cell_dim == 0:
            cell_verts = [idx_lower]
        elif cell_dim == 1:
            cell_verts = [idx_lower, idx_upper]
# This is specific for 2D
        else:
            x1, y1 = coords_lower
            x2, y2 = coords_upper
            idx1 = idx_lower
            idx2 = coords2idx[(x2, y1)]
            idx3 = idx_upper
            idx4 = coords2idx[(x1, y2)]
            cell_verts = [idx1, idx2, idx3, idx4]
        cell = {"cell_dim" : cell_dim, "cell_index" : cell_index, "cell_verts" : cell_verts}
        cells.append(cell)
    complex_json_data = {"complex" : {"dimension" : dimension,
                                      "verts_coords" : verts_coords,
                                      "cells" : cells} }
    return complex_json_data

def morse_graph_json(morse_graph):
    # Return json data for Morse graph

    def vertex_rank(u):
        # Return how many levels down of children u have
        children = [v for v in morse_graph.poset().children(u)]
        if len(children) == 0:
            return 0
        return 1 + max([vertex_rank(v) for v in children])

    # Get list of Morse nodes
    morse_nodes = range(morse_graph.poset().size())
    morse_graph_data = [] # Morse graph data
    for morse_node in morse_nodes:
        label = morse_graph.annotation(morse_node)[0]
        adjacencies = morse_graph.poset().children(morse_node)
        morse_node_data = {"node" : morse_node,
                           "rank" : vertex_rank(morse_node),
                           "label" : label,
                           "adjacencies" : adjacencies}
        morse_graph_data.append(morse_node_data)
    morse_graph_json_data = {"morse_graph" : morse_graph_data}
    return morse_graph_json_data

def morse_sets_json(network, morse_decomposition):
    # Return json data for Morse sets
    # Get a mapping from DSGRN top cells to cc top cells
    cell2cc_cell = dsgrn_cell_to_cc_cell_map(network)
    # Get list of Morse nodes
    morse_nodes = range(morse_decomposition.poset().size())
    morse_sets_data = [] # Morse sets data
    for morse_node in morse_nodes:
        morse_cells = [cell2cc_cell[c] for c in morse_decomposition.morseset(morse_node)]
        morse_set = {"index" : morse_node, "cells" : morse_cells}
        morse_sets_data.append(morse_set)
    morse_sets_json_data = {"morse_sets" : morse_sets_data}
    return morse_sets_json_data

def state_transition_graph_json(network, domain_graph):
    # Return json data for state transiton graph
    # Get a mapping from DSGRN top cells to cc top cells
    cell2cc_cell = dsgrn_cell_to_cc_cell_map(network)
    # Get state transition graph vertices
    stg_vertices = range(domain_graph.digraph().size())
    stg = [] # State transition graph
    for v in stg_vertices:
        adjacencies = [cell2cc_cell[u] for u in domain_graph.digraph().adjacencies(v)]
        node_adjacency_data = {"node" : cell2cc_cell[v], "adjacencies" : adjacencies}
        stg.append(node_adjacency_data)
    stg_json_data = {"stg" : stg}
    return stg_json_data

def save_morse_graph_database_json(network, database_fname, param_indices=None):
    parameter_graph = DSGRN.ParameterGraph(network)
    if param_indices == None:
        param_indices = range(parameter_graph.size())
    network_json_data = network_json(network)
    cell_complex_json_data = cubical_complex_json(network)
    param_graph_json_data = parameter_graph_json(parameter_graph, param_indices)
    dynamics_database = [] # Dynamics database
    for par_index in param_indices:
        # Compute DSGRN dynamics
        parameter = parameter_graph.parameter(par_index)
        domain_graph = DSGRN.DomainGraph(parameter)
        morse_decomposition = DSGRN.MorseDecomposition(domain_graph.digraph())
        morse_graph = DSGRN.MorseGraph(domain_graph, morse_decomposition)
        morse_graph_json_data = morse_graph_json(morse_graph)
        morse_sets_json_data = morse_sets_json(network, morse_decomposition)
        stg_json_data = state_transition_graph_json(network, domain_graph)
        # Dynamics data for this parameter
        dynamics_json_data = {"parameter" : par_index,
                              "morse_graph" : morse_graph_json_data["morse_graph"],
                              "morse_sets" : morse_sets_json_data["morse_sets"],
                              "stg" : stg_json_data["stg"]}
        dynamics_database.append(dynamics_json_data)
    morse_graph_database = {"network" : network_json_data["network"],
                            "complex" : cell_complex_json_data["complex"],
                            "parameter_graph" : param_graph_json_data["parameter_graph"],
                            "dynamics_database" : dynamics_database}
    # Save database to a file
    with open(database_fname, 'w') as outfile:
        json.dump(morse_graph_database, outfile)
