defmodule Util.GraphContractUtil do
  alias DB.Repo
  alias DB.{Actor, Edge, Task}
  import Ecto.Changeset

  @doc """
  根据给定的 `uid` 获取与其 `graph_id` 相同的 actors 和 edges，并转换 actor 数据结构。
  """
  def get_graph_by_uid(uid) do
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

        {:ok, %{actors: transformed_actors, edges: edges}}
    end
  end

  @doc """
  根据 init_data 生成任务 (Task)。
  """
  def generate_task(init_data) do
    %Task{}
    |> Task.changeset(init_data)
    |> Repo.insert()
  end

  defp transform_actors(actors) do
    # [
    #   %{
    #     init: "1:Node1",
    #     env: "producer"
    #   },
    #   %{
    #     init: "2:Node2",
    #     env: "consumer"
    #   }
    # ]
    Enum.map(actors, fn %Actor{uid: uid, name: name, role: role} ->
      %{
        init: "#{uid}:#{name}",
        env: role
      }
    end)
  end
end
