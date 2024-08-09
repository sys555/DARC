defmodule MockDataHelper do
  alias Ecto.UUID
  alias Util.DBUtil

  def generate_mock_data do
    graph_id = UUID.generate()

    actors = for i <- 1..4 do
      %{
        uid: UUID.generate(),
        name: "Actor #{i}",
        role: "Speaker",
        age: 20 + i * 5,
        graph_id: graph_id
      }
    end

    edges = for actor1 <- actors, actor2 <- actors, actor1[:uid] != actor2[:uid] do
      {actor1[:uid], actor2[:uid], graph_id}
    end

    %{actors: actors, edges: edges}
  end

  def insert_mock_data(mock_data) do
    %{actors: actors, edges: edges} = mock_data

    DBUtil.insert_actors(actors)
    DBUtil.insert_edges(edges)
  end
end
