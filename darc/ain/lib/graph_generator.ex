defmodule GraphGenerator do
  def generate_graph(node_count, edge_count) do
    nodes = generate_nodes(node_count)
    edges = generate_edges(nodes, edge_count)
    data = generate_data(nodes)

    %{
      "nodes" => nodes,
      "edges" => edges,
      "data" => data
    }
  end

  defp generate_nodes(count) do
    Enum.map(1..count, fn i ->
      node_id = "node#{i}"
      {
        node_id,
        %{
          "init" => "addr#{i}",
          "env" => "compute_prefix"
        }
      }
    end)
    |> Map.new()
  end

  defp generate_edges(nodes, count) do
    node_ids = Map.keys(nodes)

    edges = Enum.reduce(1..count, MapSet.new(), fn _, acc ->
      from_node = Enum.random(node_ids)
      to_node = Enum.random(node_ids -- [from_node])  # Ensure to_node is different from from_node
      edge = "#{from_node}:#{to_node}"

      MapSet.put(acc, edge)
    end)

    MapSet.to_list(edges)
  end

  defp generate_data(nodes) do
    nodes
    |> Map.keys()
    |> Enum.reduce(%{}, fn node, acc ->
      Map.put(acc, node, "Initial message from #{node}")
    end)
  end
end
