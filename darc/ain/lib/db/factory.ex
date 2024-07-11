defmodule DB.Factory do
  use ExMachina.Ecto, repo: DB.Repo
  alias Faker.Person
  alias DB.Repo
  alias DB.{Actor, Edge}

  def start_repo do
    case Repo.start_link() do
      {:ok, _pid} -> :ok
      {:error, {:already_started, _pid}} -> :ok
      {:error, reason} -> raise "Failed to start Repo: #{inspect(reason)}"
    end
    # 等待连接建立
    :timer.sleep(1000)
  end

  def actor_factory(attrs \\ %{}) do
    %Actor{
      name: Person.name(),
      role: Map.get(attrs, :role, ""),
      age: Enum.random(18..70),
      graph_id: Map.get(attrs, :graph_id, Ecto.UUID.generate())
    }
  end


  def edge_factory(attrs) do
    %Edge{
      since: Enum.random(1..10),
      graph_id: attrs[:graph_id],
      from_uid: attrs[:from_uid],
      to_uid: attrs[:to_uid]
    }
  end

  def clear_tables do
    Repo.delete_all(Actor)
    Repo.delete_all(Edge)
    :timer.sleep(1000)
  end

  def create_actors_and_edges do
    start_repo()
    clear_tables()  # 清除表内容

    common_graph_id = Ecto.UUID.generate()
    second_actor_uid = Ecto.UUID.generate() # Generate a UID for the second actor

    # Generate actors with specific graph_id and insert them into the database
    actors = [
      insert(:actor, %{graph_id: common_graph_id, role: "Producer"}),
      insert(:actor, %{graph_id: common_graph_id, uid: second_actor_uid, role: "Graph"}),
      insert(:actor, %{graph_id: common_graph_id, role: "Producer"}),
      insert(:actor, %{graph_id: second_actor_uid, role: "Producer"}),
      insert(:actor, %{graph_id: second_actor_uid, role: "Producer"})
    ]

    # Ensure actors have uid
    actors_with_uid = Enum.map(actors, fn actor ->
      if Map.has_key?(actor, :uid) do
        actor
      else
        raise "Actor does not have a uid: #{inspect(actor)}"
      end
    end)

    # Create edges
    edges = [
      insert(:edge, %{graph_id: common_graph_id, since: Enum.random(1..10), from_uid: Enum.at(actors_with_uid, 0).uid, to_uid: Enum.at(actors_with_uid, 1).uid}),
      insert(:edge, %{graph_id: common_graph_id, since: Enum.random(1..10), from_uid: Enum.at(actors_with_uid, 1).uid, to_uid: Enum.at(actors_with_uid, 2).uid}),
      insert(:edge, %{graph_id: second_actor_uid, since: Enum.random(1..10), from_uid: Enum.at(actors_with_uid, 3).uid, to_uid: Enum.at(actors_with_uid, 4).uid})
    ]

    {actors_with_uid, edges}
  end
end
