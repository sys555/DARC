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
      uid: Map.get(attrs, :uid, Ecto.UUID.generate()),  # 处理传入的 uid
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
      insert(:actor, %{graph_id: common_graph_id, role: "PM"}),
      insert(:actor, %{graph_id: common_graph_id, uid: second_actor_uid, role: "Graph"}),
      insert(:actor, %{graph_id: common_graph_id, role: "QA"}),
      insert(:actor, %{graph_id: second_actor_uid, role: "DEV"}),
      insert(:actor, %{graph_id: second_actor_uid, role: "DEV"})
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

  def mock_distributed_topology(args) do
    start_repo()
    clear_tables()  # 清除表内容

    graph_id = Map.fetch!(args, :graph_id)
    roles = Map.keys(args) -- [:graph_id]

    # Generate actors based on the specified number of agents for each role
    actors =
      for {role, count} <- args, role != :graph_id do
        for _ <- 1..count do
          insert(:actor, %{graph_id: graph_id, role: Atom.to_string(role)})
        end
      end
      |> List.flatten()

    # Ensure actors have uid
    actors_with_uid = Enum.map(actors, fn actor ->
      case actor do
        %DB.Actor{uid: uid} = actor ->
          actor

        _ ->
          raise "Actor does not have a uid: #{inspect(actor)}"
      end
    end)

    # Generate edges ensuring each agent has at least one connection
    edges =
      for actor <- actors_with_uid, next_actor <- actors_with_uid, actor.uid != next_actor.uid do
        insert(:edge, %{
          graph_id: graph_id,
          since: Enum.random(1..10),
          from_uid: actor.uid,
          to_uid: next_actor.uid
        })
      end
    IO.inspect(edges)
    {actors_with_uid, edges}
  end
end
