defmodule BridgeTest do
  use ExUnit.Case, async: true

  alias Bridge
  alias Ain.ActorSupervisor
  alias Util.{DBUtil, ActorUtil}
  alias DB.Repo

  setup do
    :ok = Ecto.Adapters.SQL.Sandbox.checkout(Repo)
    Ecto.Adapters.SQL.Sandbox.mode(Repo, {:shared, self()})

    # 插入测试所需数据
    graph_id = "16661c5e-b5ad-4dfd-ba14-8f1000ade9d2"
    actor_specs = [
      %{uid: Ecto.UUID.generate(), name: "Actor1", role: "Speaker", age: 30, graph_id: graph_id},
      %{uid: Ecto.UUID.generate(), name: "Actor2", role: "Speaker", age: 40, graph_id: graph_id}
    ]
    edges = [
      {actor_specs |> Enum.at(0) |> Map.get(:uid), actor_specs |> Enum.at(1) |> Map.get(:uid), graph_id}
    ]

    # 插入 actors 和 edges 数据
    DBUtil.insert_actors(actor_specs)
    DBUtil.insert_edges(edges)

    {:ok, %{actor_specs: actor_specs, graph_id: graph_id}}
  end

  test "start/1 initializes and connects actors", %{actor_specs: actor_specs, graph_id: graph_id} do
    # 直接从数据库获取 actor 规格
    obtained_actor_specs = DBUtil.generate_actor_specs_from_db(graph_id)

    # 确保从数据库获取的 actor 规格与插入的一致
    assert obtained_actor_specs == actor_specs

    # 启动 Actor Supervisor
    {:ok, _supervisor_pid} = ActorSupervisor.start_link(obtained_actor_specs)

    # 直接从数据库获取边信息
    obtained_edges = DBUtil.get_edges_by_graph_id(graph_id)
    expected_edges = [
      {obtained_actor_specs |> Enum.at(0) |> Map.get(:uid), obtained_actor_specs |> Enum.at(1) |> Map.get(:uid), graph_id}
    ]

    # Transform `obtained_edges` to match the format of `expected_edges`
    transformed_obtained_edges = Enum.map(obtained_edges, fn edge ->
      {edge.from_uid, edge.to_uid, edge.graph_id}
    end)

    # 确保从数据库获取的边信息与插入的一致
    assert transformed_obtained_edges == expected_edges

    # 连接 actors
    :ok = ActorUtil.connect_actors(obtained_edges, obtained_actor_specs)
  end
end
