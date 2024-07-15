defmodule SubGraphExample do
  alias DB.Repo
  alias Util.GraphContractUtil
  import DB.Factory

  def mockdata do
    # 生成并插入 5 个 Actor 记录和 3 个 Edge 记录，并返回这些记录
    {actors, edges} = create_actors_and_edges()
    IO.inspect(actors)
    IO.inspect(edges)
    {:ok, contract_pid} = GraphContract.start_link([])
  end

  def gen_task do
    Repo.start_link()
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

  def get_graph_data do
    Repo.start_link()
    IO.inspect(GraphContractUtil.get_actors_and_edges_by_graph_id("2026b8af-79d2-4853-acbe-bcd080ae403d"))
  end

  def gen_contract do
    Repo.start_link()
    pid = GraphContract.start_with_graph_id_and_init_data("2026b8af-79d2-4853-acbe-bcd080ae403d", "haha")
  end

end
