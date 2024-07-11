defmodule GraphExample do
  def run do
    num_nodes = 1000
    num_edges = 1000

    # 使用 GraphGenerator 模块直接生成图并获取 JSON 格式数据
    data = GraphGenerator.generate_graph(num_nodes, num_edges)
    IO.inspect(data)
    {:ok, contract_pid} = GraphContract.start_link([])
    GraphContract.run_setup(data, contract_pid)
    # :timer.sleep(1000)
    # loop(contract_pid, 0)
  end

  def loop(contract_pid, prev_pool) do
    logs = GraphContract.get_logs(contract_pid)
    pool = Enum.reduce(logs, 0, fn {_key, value}, acc -> acc + length(value) end)
    # 打印当前的 pool 值
    IO.puts("Current total log entries: #{pool}")

    # 检查这次的 pool 值是否与上次相同
    if pool == prev_pool do
      IO.puts("Pool size has stabilized at: #{pool}, stopping loop.")
    else
      # 等待一秒后继续递归
      Process.sleep(1000)
      loop(contract_pid, pool)
    end
  end
end
