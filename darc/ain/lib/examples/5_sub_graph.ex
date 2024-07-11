defmodule SubGraphExample do
  alias DB.Repo
  import DB.Factory

  def mockdata do
    # 生成并插入 5 个 Actor 记录和 3 个 Edge 记录，并返回这些记录
    {actors, edges} = create_actors_and_edges()
    IO.inspect(actors)
    IO.inspect(edges)
    {:ok, contract_pid} = GraphContract.start_link([])
  end

  def gen_task do
    init_data = %{
      ttl: 3600,
      nodes: %{},
      input: %{},
      output: %{},
      diff_graph: %{},
      whole_graph: %{},
      logs: %{}
    }

    case Util.GraphContractUtil.generate_task(init_data) do
      {:ok, task} -> IO.inspect(task, label: "Generated Task")
      {:error, changeset} -> IO.inspect(changeset, label: "Task Generation Error")
    end
  end
end
