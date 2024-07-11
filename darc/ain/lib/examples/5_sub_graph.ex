defmodule SubGraphExample do
  alias DB.Repo
  import DB.Factory

  def run do
    # 生成并插入 5 个 Actor 记录和 3 个 Edge 记录，并返回这些记录
    {actors, edges} = create_actors_and_edges()
    IO.inspect(actors)
    IO.inspect(edges)
    {:ok, contract_pid} = GraphContract.start_link([])
  end
end
