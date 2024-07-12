defmodule Util.GraphContractUtil do
  alias DB.Repo
  alias DB.{Actor, Edge, Task}
  import Ecto.Query
  import Ecto.Changeset

  @doc """
  根据给定的 `uid` 获取与其 `graph_id` 相同的 actors 和 edges，并转换 actor 数据结构
  """
  def get_graph_by_uid(uid) do
    # actor.ROLE == "Graph", get the sub_graph of this actor
    # 查找具有给定 uid 的 actor
    actor = Repo.get_by(Actor, uid: uid)

    case actor do
      nil ->
        {:error, "Actor with uid #{uid} not found"}
      %Actor{graph_id: graph_id} ->
        # 获取相同 graph_id 的所有 actors 和 edges
        actors = Repo.all(from a in Actor, where: a.graph_id == ^graph_id)
        edges = Repo.all(from e in Edge, where: e.graph_id == ^graph_id)

        # 转换 actor 数据结构
        transformed_actors = transform_actors(actors)
        transformed_edges = transform_edges(edges)

        {:ok, %{actors: transformed_actors, edges: transformed_edges}}
    end
  end

  @doc """
  根据 init_data 生成任务 (Task)
  """
  def generate_task(init_data) do
    %Task{}
    |> Task.changeset(init_data)
    |> Repo.insert()
  end

  defp transform_actors(actors) do
    # [
    #   %Actor{uid: "198a4c54-77f1-490b-be52-b57c57732b82", name: "node1", role: "Producer"},
    #   %Actor{uid: "198a4c54-77f1-490b-be52-b57c57732b83", name: "node2", role: "Consumer"}
    # ]
    # to
    #
    # %{
    #   "198a4c54-77f1-490b-be52-b57c57732b82" => %{"env" => "Producer", "init" => "198a4c54-77f1-490b-be52-b57c57732b82:node1"},
    #   "198a4c54-77f1-490b-be52-b57c57732b83" => %{"env" => "Consumer", "init" => "198a4c54-77f1-490b-be52-b57c57732b83:node2"}
    # }
    Enum.reduce(actors, %{}, fn %Actor{uid: uid, name: name, role: role}, acc ->
      Map.put(acc, uid, %{
        "init" => "#{uid}:#{name}",
        "env" => String.capitalize(role)
      })
    end)
  end

  defp transform_edges(edges) do
    # %[
    #   "node1-uid:node3-uid",
    #   "node1-uid:node2-uid",
    #   "node2-uid:node4-uid",
    #   "node3-uid:node4-uid"
    # ]
    Enum.map(edges, fn %DB.Edge{from_uid: from_uid, to_uid: to_uid} ->
      "#{from_uid}:#{to_uid}"
    end)
  end

  def get_actors_and_edges_by_graph_id(graph_id) do
    actors =
      from(a in Actor, where: a.graph_id == ^graph_id)
      |> Repo.all()

    edges =
      from(e in Edge, where: e.graph_id == ^graph_id)
      |> Repo.all()

    # 转换 actor 和 edge 数据结构
    transformed_actors = transform_actors(actors)
    transformed_edges = transform_edges(edges)

    {:ok, %{actors: transformed_actors, edges: transformed_edges}}
  end


end
