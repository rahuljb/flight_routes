from heapq import heappush, heappop

from django.shortcuts import render, get_object_or_404
from .models import Route, RouteNode


# ---------- helpers for tree logic ----------

def deepest_child(node, side: str):
    """
    Q1: from this node, walk repeatedly to left/right child until no more.
    """
    current = node
    while True:
        child = current.children.filter(side=side).first()
        if not child:
            return current
        current = child


def longest_path_from(node):
    """
    Q2: from a starting node, find the deepest descendant (by TOTAL distance).
    Returns (max_distance_from_node, deepest_node).
    """
    best_distance = 0
    best_node = node  # if no children, longest is itself with 0 extra distance

    for child in node.children.all():
        child_distance, child_deepest = longest_path_from(child)
        total_from_node = child.duration + child_distance

        if total_from_node > best_distance:
            best_distance = total_from_node
            best_node = child_deepest

    return best_distance, best_node


def build_graph_for_route(route):
    """
    Q3 helper: build an undirected graph for this route.
    parent <-> child edge weight = child.duration (distance from parent)
    """
    graph = {}
    nodes = route.nodes.select_related('parent').all()

    for node in nodes:
        graph.setdefault(node.id, [])
        if node.parent_id:
            w = node.duration
            graph[node.id].append((node.parent_id, w))
            graph.setdefault(node.parent_id, []).append((node.id, w))

    return graph


def shortest_path_between(route, start_node, end_node):
    """
    Q3: Dijkstra shortest path between two airports in one route.
    Returns (total_distance, [RouteNode, ...]) or (None, []) if no path.
    """
    if start_node.id == end_node.id:
        return 0, [start_node]

    graph = build_graph_for_route(route)
    start_id = start_node.id
    end_id = end_node.id

    dist = {start_id: 0}
    prev = {}
    heap = [(0, start_id)]

    while heap:
        d, current = heappop(heap)
        if current == end_id:
            break
        if d > dist.get(current, float('inf')):
            continue

        for neighbor_id, w in graph.get(current, []):
            nd = d + w
            if nd < dist.get(neighbor_id, float('inf')):
                dist[neighbor_id] = nd
                prev[neighbor_id] = current
                heappush(heap, (nd, neighbor_id))

    if end_id not in dist:
        return None, []

    # reconstruct path ids
    path_ids = []
    cur = end_id
    while cur is not None:
        path_ids.append(cur)
        cur = prev.get(cur)
    path_ids.reverse()

    id_to_node = {n.id: n for n in route.nodes.all()}
    path_nodes = [id_to_node[i] for i in path_ids]

    return dist[end_id], path_nodes


# ---------- main view ----------

def route_tools(request):
    routes = Route.objects.all()
    all_nodes = RouteNode.objects.all()   # for airport dropdowns (Q1 + Q2)

    # results
    left_right_result = None          # Q1
    longest_node = None               # Q2
    longest_total = None              # Q2
    shortest_nodes = None             # Q3 (list of nodes)
    shortest_total = None             # Q3
    shortest_error = None             # Q3 error message

    # keep selected values for dropdowns
    selected_start_node_id = None     # Q1 airport
    selected_direction = None         # Q1 direction
    selected_longest_start_id = None  # Q2 airport
    selected_shortest_route_id = None # Q3 route

    if request.method == "POST":
        action = request.POST.get("action")

        # 1️⃣ Q1: last left/right node from selected airport
        if action == "left_right":
            selected_start_node_id = request.POST.get("start_node")
            selected_direction = request.POST.get("direction")

            if selected_start_node_id and selected_direction:
                start_node = get_object_or_404(RouteNode, id=selected_start_node_id)
                left_right_result = deepest_child(start_node, selected_direction)

        # 2️⃣ Q2: longest node (total distance) from selected airport
        elif action == "longest":
            selected_longest_start_id = request.POST.get("longest_start_node")
            if selected_longest_start_id:
                start_node = get_object_or_404(RouteNode, id=selected_longest_start_id)
                longest_total, longest_node = longest_path_from(start_node)

        # 3️⃣ Q3: shortest path between two airports (within a route)
        elif action == "shortest":
            selected_shortest_route_id = request.POST.get("shortest_route")
            airport_a = request.POST.get("airport_a", "").strip().upper()
            airport_b = request.POST.get("airport_b", "").strip().upper()

            if not selected_shortest_route_id:
                shortest_error = "Please select a route."
            elif not airport_a or not airport_b:
                shortest_error = "Please enter both airport codes."
            else:
                route = get_object_or_404(Route, id=selected_shortest_route_id)

                start = route.nodes.filter(airport_code__iexact=airport_a).first()
                end = route.nodes.filter(airport_code__iexact=airport_b).first()

                if not start or not end:
                    shortest_error = "One or both airports not found in this route."
                else:
                    total, path_nodes = shortest_path_between(route, start, end)
                    if total is None or not path_nodes:
                        shortest_error = (
                            f"No path found between {airport_a} and {airport_b} "
                            f"in {route.name}."
                        )
                    else:
                        shortest_total = total
                        shortest_nodes = path_nodes

    context = {
        "routes": routes,
        "all_nodes": all_nodes,

        # Q1
        "left_right_result": left_right_result,
        "selected_start_node_id": selected_start_node_id,
        "selected_direction": selected_direction,

        # Q2
        "longest_node": longest_node,
        "longest_total": longest_total,
        "selected_longest_start_id": selected_longest_start_id,

        # Q3
        "shortest_nodes": shortest_nodes,
        "shortest_total": shortest_total,
        "shortest_error": shortest_error,
        "selected_shortest_route_id": selected_shortest_route_id,
    }

    return render(request, "routes/main.html", context)
