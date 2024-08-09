defmodule Util.DBUtil do
  alias DB.Repo
  alias DB.{Actor, Edge, Task}
  import Ecto.Query
  import Ecto.Changeset

  def generate_actor_specs_from_db(graph_id) do
    actors =
      from(a in Actor, where: a.graph_id == ^graph_id)
      |> Repo.all()

    transform_actors(actors)
  end

  def get_edges_by_graph_id(graph_id) do
    edges =
      from(e in Edge, where: e.graph_id == ^graph_id)
      |> Repo.all()

    edges
  end

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

  defp transform_actors(actors) do
    # [
    #   %Actor{uid: "198a4c54-77f1-490b-be52-b57c57732b82", name: "node1", role: "Producer"},
    #   %Actor{uid: "198a4c54-77f1-490b-be52-b57c57732b83", name: "node2", role: "Consumer"}
    # ]
    # to
    # [
    # :uid => uid,
    # :name => name,
    # :role => role
    # ]
    Enum.map(actors, fn %Actor{uid: uid, name: name, role: role, age: age, graph_id: graph_id}->
      %{
        :uid => uid,
        :name => name,
        :role => role,
        :age => age,
        :graph_id => graph_id
      }
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

  def get_actor_with_uid(uid) do
    Repo.get(Actor, uid)
  end

  def insert_actors(actor_specs) do
    Enum.each(actor_specs, fn spec ->
      %Actor{}
      |> Actor.changeset(spec)
      |> Repo.insert!()
    end)
  end

  def insert_edges(edges) do
    Enum.each(edges, fn {from_id, to_id, graph_id} ->
      edge_attrs = %{
        "from_uid" => to_string(from_id),
        "to_uid" => to_string(to_id),
        "graph_id" => graph_id
      }

      %Edge{}
      |> Edge.changeset(edge_attrs)
      |> Repo.insert()
    end)
  end
end
